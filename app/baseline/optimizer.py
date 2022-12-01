import pandas as pd
import math
from copy import deepcopy
import sys
import time
import numpy as np
from multiprocessing import Pool
#from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from . import config


def generate_transformed_time_matrix(locations, time_matrix):
    new_time_matrix = []
    for source in locations:
        new_time_matrix_row = []
        for target in locations:
            new_time_matrix_row.append(int(time_matrix[source][target]))
        new_time_matrix.append(new_time_matrix_row)
    return new_time_matrix


def generate_transformed_time_matrix_chunk(chunk, locations, time_matrix):
    new_time_matrix = []
    for source in chunk:
        new_time_matrix_row = []
        for target in locations:
            new_time_matrix_row.append(int(time_matrix[source][target]))
        new_time_matrix.append(new_time_matrix_row)
    return new_time_matrix


def generate_transformed_time_matrix_parallel(locations, time_matrix):
    locations_split = [list(x) for x in np.array_split(locations, config.N_CORES)]
    input_args = [[x, locations, time_matrix] for x in locations_split]
    with Pool(config.N_CORES) as pool:
        results = pool.starmap(generate_transformed_time_matrix_chunk, input_args)
    result = []
    for x in results:
        for y in x:
            result.append(y)
    return result


def extract_vehicles(df_vehicles, num_vehicles):
    vehicle_ids = list(range(num_vehicles))
    result = df_vehicles[df_vehicles['vehicle_id'].isin(vehicle_ids)]
    result = result.sort_values(by=['vehicle_id'])
    return result


def get_sum_of_all_distances(time_matrix, num_vehicles):
    result = 0
    for i in range(num_vehicles*2, len(time_matrix)):
        result += sum(time_matrix[i])
    return result


def create_data_model(date, df_all_requests, time_matrix, df_vehicles, num_vehicles):
    vehicles = extract_vehicles(df_vehicles, num_vehicles)
    df_requests = df_all_requests[df_all_requests['date']==date].sort_values(by=['time']).reset_index(drop=True)

    # generate locations, time_windows, pickups_deliveries, starts, ends, vehicle_capacities
    locations = []  # node_id
    time_windows = []  # [window_start, window_end]
    pickups_deliveries = []  # [source_location, target_location]
    starts = []  # node id
    ends = []  # node id
    vehicle_capacities = []  # 8
    request_ids = []
    location_types = []

    current_location = 0
    for k, v in vehicles.iterrows():
        vehicle_capacities.append(int(v['capacity']))
        locations.append(int(v['node_id']))
        locations.append(int(v['node_id']))
        time_windows.append([int(v['time']), config.DAY_END_TIME])
        time_windows.append([int(v['time']), config.DAY_END_TIME])
        starts.append(current_location)
        ends.append(current_location+1)
        request_ids.append(-1)
        request_ids.append(-1)
        location_types.append("depot_start")
        location_types.append("depot_end")
        current_location += 2

    for k, v in df_requests.iterrows():
        locations.append(int(v['source']))
        locations.append(int(v['target']))
        time_windows.append([int(v['source_window_start']), int(v['source_window_end'])])
        time_windows.append([int(v['target_window_start']), int(v['target_window_end'])])
        pickups_deliveries.append([current_location, current_location+1])
        request_ids.append(v['request_id'])
        request_ids.append(v['request_id'])
        location_types.append("pickup")
        location_types.append("dropoff")
        current_location += 2

    # generate travel time matrix
    #transformed_time_matrix = generate_transformed_time_matrix(locations, time_matrix)
    transformed_time_matrix = generate_transformed_time_matrix_parallel(locations, time_matrix)

    data = {'locations': locations,
            'time_windows': time_windows,
            'pickups_deliveries': pickups_deliveries,
            'starts': starts,
            'ends': ends,
            'vehicle_capacities': vehicle_capacities,
            'time_matrix': transformed_time_matrix,
            'num_vehicles': num_vehicles,
            'vehicles': vehicles,
            'date': date,
            'request_ids': request_ids,
            'location_types': location_types,
            'df_requests': df_requests}
    return data


def run_vrp(data, time_limit):
    if config.VRP_TIME_LIMIT is None:
        vrp_time_limit = int(len(data['pickups_deliveries']) * time_limit / 10)
    else:
        vrp_time_limit = config.VRP_TIME_LIMIT
    if config.LOGGING:
        print(f"time limit will be {vrp_time_limit}")
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'],
                                           data['starts'],
                                           data['ends'])
    if config.LOGGING:
        print("got manager")
        time.sleep(1)
    # Create routing model
    routing = pywrapcp.RoutingModel(manager)
    print("got routing")
    time.sleep(1)

    # define the transit callback
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node] + config.DWELL_TIME

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    if config.LOGGING:
        print("defined transit callback")
        time.sleep(1)

    # add time dimension
    dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        config.MAX_VEHICLE_SLACK,  # slack TODO
        config.DAY_END_TIME,  # max time per vehicle
        config.START_CUMUL_TO_ZERO,  # start cumul to zero
        dimension_name)
    time_dimension = routing.GetDimensionOrDie(dimension_name)
    #time_dimension.SetGlobalSpanCostCoefficient(100)
    if config.LOGGING:
        print("add time dimension")
        time.sleep(1)

    # pickup and deliveries.
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            time_dimension.CumulVar(pickup_index) <=
            time_dimension.CumulVar(delivery_index))
    if config.LOGGING:
        print("done with pickup and deliveries")
        time.sleep(1)

    # time windows (trips)
    for time_window_index in range(0, len(data['time_windows'])):
        if (time_window_index in data['starts'] + data['ends']):
            continue
        index = manager.NodeToIndex(time_window_index)
        v = data['time_windows'][time_window_index]
        #print(f"time_window_index: {time_window_index}, time_window: {v}")
        time_dimension.CumulVar(index).SetRange(v[0], v[1])
    if config.LOGGING:
        print("done with time windows")
        time.sleep(1)

    # time windows (start and end locations)
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        start_loc = data['starts'][vehicle_id]
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][start_loc][0],
            data['time_windows'][start_loc][1])

        index = routing.End(vehicle_id)
        end_loc = data['ends'][vehicle_id]
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][end_loc][0],
            data['time_windows'][end_loc][1])
    if config.LOGGING:
        print("done with time windows (start and end locations)")
        time.sleep(1)

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
    if config.LOGGING:
        print("instantiated route start and end times")
        time.sleep(1)

    # capacity constraints
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        location_type = data['location_types'][from_node]
        if location_type == "pickup":
            return 1
        elif location_type == "dropoff":
            return -1
        else:
            return 0

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    if config.LOGGING:
        print("done with capacity constraints")
        time.sleep(1)

    # Allow to drop nodes
    if config.PENALTY_FUN == "sum_all_times":
        penalty = get_sum_of_all_distances(data['time_matrix'], data['num_vehicles'])
    else:
        penalty = config.DAY_END_TIME * data['num_vehicles']
    for node in range(data['num_vehicles'] * 2, len(data['time_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
    if config.LOGGING:
        print("done with allowing to drop nodes")
        time.sleep(1)

    # search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        config.FIRST_SOLUTION_STRATEGY)
    search_parameters.local_search_metaheuristic = (
        config.LOCAL_SEARCH_METAHEURISTIC)
    search_parameters.time_limit.seconds = vrp_time_limit
    if config.LOGGING:
        print("done with search parameters")
        time.sleep(1)

    # Solve the problem.
    search_parameters.log_search = config.LOG_SEARCH
    solution = routing.SolveWithParameters(search_parameters)
    if config.LOGGING:
        print("got solution")
        time.sleep(1)

    try:
        vehicle_runs = extract_vehicle_runs(data, manager, routing, solution)
        df_vehicle_runs = vehicle_runs_to_df(data, vehicle_runs)
        return df_vehicle_runs
    except Exception as e:
        print(f"Error with date={data['date']}")
        print(e)
        sys.stdout.flush()
        time.sleep(5)
        return None


def extract_vehicle_runs(data, manager, routing, solution):
    if config.LOGGING:
        print(f"Objective: {solution.ObjectiveValue()}")
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    vehicle_runs = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        vehicle_run = []
        i = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2}) -> '.format(
                manager.IndexToNode(index), solution.Min(time_var),
                solution.Max(time_var))
            vehicle_run.append({'loc': manager.IndexToNode(index),
                                'early_time': solution.Min(time_var),
                                'late_time': solution.Max(time_var),
                                'order': i})
            index = solution.Value(routing.NextVar(index))
            i += 1
        time_var = time_dimension.CumulVar(index)
        vehicle_run.append({'loc': manager.IndexToNode(index),
                            'early_time': solution.Min(time_var),
                            'late_time': solution.Max(time_var),
                            'order': i})
        vehicle_runs.append(vehicle_run)
        plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                    solution.Min(time_var),
                                                    solution.Max(time_var))
        plan_output += 'Time of the route: {}min\n'.format(
            solution.Min(time_var))
        if config.LOGGING:
            print(plan_output)
        total_time += solution.Min(time_var)
    return vehicle_runs


def vehicle_runs_to_df(data, vehicle_runs):
    dfs = []
    for i in range(len(vehicle_runs)):
        vehicle_run = vehicle_runs[i]
        df = pd.DataFrame.from_records(vehicle_run)
        df['vehicle_id'] = i
        #df['run_id'] = run_id
        dfs.append(df)
    result = pd.concat(dfs, ignore_index=True)
    temp = pd.DataFrame({'request_id': data['request_ids'],
                         'location': data['locations'],
                         'location_type': data['location_types']})
    #result = temp.merge(result, how='left', left_on='loc', right_on='location', validate='one_to_one')
    result = result.merge(temp, how='left', left_on='loc', right_index=True, validate='one_to_one')
    result['node_id'] = result['location']
    result['location'] = result['loc']
    result = result.drop(columns=['loc'])
    return result
