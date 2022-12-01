import pandas as pd
import math


def extract_service_rate(requests_in, routes_in, perc):
    requests = requests_in[requests_in['perc']==perc]
    routes = routes_in[(routes_in['perc']==perc) & (routes_in['request_id']!=-1)]
    unique_dates = sorted(requests['date'].unique())
    unique_vehicles = sorted(routes['num_vehicles'].unique())
    result = {f"veh{x}": [] for x in unique_vehicles}
    for num_vehicles in unique_vehicles:
        row = []
        for date in unique_dates:
            total_num_requests = len(requests[requests['date']==date]['request_id'].unique())
            num_request_served = len(routes[(routes['date']==date) & (routes['num_vehicles']==num_vehicles)]['request_id'].unique())
            #print(total_num_requests, num_request_served)
            val = (num_request_served / total_num_requests) * 100
            row.append(math.floor(val))
        result[f"veh{num_vehicles}"] = row
    df = pd.DataFrame(result)
    return df
