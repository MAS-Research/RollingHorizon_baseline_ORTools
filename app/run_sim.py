import os
import pandas as pd
import numpy as np
import csv
import datetime as dt
import time
import argparse

from baseline import disk, optimizer, config


if __name__=="__main__":
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument('--data_type', required=True)
    parser.add_argument('--sample_per', required=False)
    parser.add_argument('--num_vehicles', required=True)
    parser.add_argument('--time_limit', required=True) #unit is milisecond
    args = parser.parse_args()
    data_type = args.data_type
    sample_per = int(args.sample_per)
    num_vehicles = int(args.num_vehicles)
    time_limit = int(args.time_limit)
    print(f"Starting simulation with data_type: {data_type}, sample_per: {sample_per}, num_vehicles: {num_vehicles}, time_limit: {time_limit}")

    # load nodes, edges and times
    file_path = os.path.join(os.path.join(os.getcwd(), "data", "data_{}".format(data_type), "map"), "nodes.csv")
    df_nodes = disk.read_nodes(file_path)
    file_path = os.path.join(os.path.join(os.getcwd(), "data", "data_{}".format(data_type), "map"), "edges.csv")
    df_edges = disk.read_edges(file_path)
    file_path = os.path.join(os.path.join(os.getcwd(), "data", "data_{}".format(data_type), "map"), "times.csv")
    time_matrix = disk.read_time_matrix(file_path)
    print("Loaded nodes, edges, and times")

    if data_type == "Chattanooga":
        vehicle_file_path = os.path.join(os.getcwd(), "data", "data_Chattanooga", "vehicles", "vehicles.csv")
        request_file_path = os.path.join(os.getcwd(), "data", "data_Chattanooga", "requests", "requests.csv")
        
    elif data_type == "NYC":
        vehicle_file_path = os.path.join(os.getcwd(), "data", "data_NYC", "vehicles", "vehicles.csv")
        if sample_per == 1:
            request_file_path = os.path.join(os.getcwd(), "data", "data_NYC", "requests", "requests_1.csv")
        elif sample_per == 10:
            request_file_path = os.path.join(os.getcwd(), "data", "data_NYC", "requests", "requests_10.csv")
        elif sample_per == 20:
            request_file_path = os.path.join(os.getcwd(), "data", "data_NYC", "requests", "requests_20.csv")
    else:
        raise ValueError("Such a data is not prepared")

    df_requests = disk.read_requests(request_file_path, time_matrix=time_matrix)
    print(f"Loaded requests. Total number of requests: {len(df_requests)}")

    # load vehicles
    df_vehicles = disk.read_vehicles(vehicle_file_path)

    unique_dates = df_requests['date'].unique()
    total_time_start = time.time()
    for date in unique_dates:
        start_time = time.time()
        file_exists = disk.vehicle_runs_exist(os.path.join(os.getcwd(), "data", "baseline_output"), date, data_type, sample_per, num_vehicles, time_limit)
        if file_exists:
            print(f"skipping date={date}, data_type={data_type}, sample_per={sample_per}, num_vehicles={num_vehicles}, time_limit={time_limit}, file already exists")
            continue
        data = optimizer.create_data_model(date, df_requests, time_matrix, df_vehicles, num_vehicles)
        df_vehicle_runs = optimizer.run_vrp(data, time_limit)
        if df_vehicle_runs is not None:
            disk.write_vehicle_runs(df_vehicle_runs, os.path.join(os.getcwd(), "data", "baseline_output"), date, data_type, sample_per, num_vehicles, time_limit)
            print(f"successfully finished date={date}, data_type={data_type}, sample_per={sample_per}, num_vehicles={num_vehicles} in {time.time()-start_time} seconds")
    print(f"done with data_type={data_type}, sample_per={sample_per}, num_vehicles={num_vehicles} in {time.time() - total_time_start} seconds")

