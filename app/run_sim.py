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
    parser.add_argument('--suffix', required=True)
    parser.add_argument('--num_vehicles', required=True)
    parser.add_argument('--time_limit', required=True) #unit is milisecond
    args = parser.parse_args()
    suffix = int(args.suffix)
    num_vehicles = int(args.num_vehicles)
    time_limit = int(args.time_limit)
    print(f"Starting simulation with suffix: {suffix}, num_vehicles: {num_vehicles}, time_limit: {time_limit}")

    # load nodes, edges and times
    file_path = os.path.join(config.MAP_DIR, "nodes.csv")
    df_nodes = disk.read_nodes(file_path)
    file_path = os.path.join(config.MAP_DIR, "edges.csv")
    df_edges = disk.read_edges(file_path)
    file_path = os.path.join(config.MAP_DIR, "times.csv")
    time_matrix = disk.read_time_matrix(file_path)
    print("Loaded nodes, edges, and times")

    # load requests
    if suffix == 1:
        file_path = os.path.join(config.REQUESTS_DIR, "requests_1.csv")
    elif suffix == 10:
        file_path = os.path.join(config.REQUESTS_DIR, "requests_10.csv")
    elif suffix == 20: #sampling for NYC data
        file_path = os.path.join(config.REQUESTS_DIR, "requests_20.csv")
    elif suffix == 100: # for chatta data
        file_path = os.path.join(config.REQUESTS_DIR, "requests_100.csv")
    else:
        raise ValueError("We need to sample the data first")
    df_requests = disk.read_requests(file_path, time_matrix=time_matrix)
    print(f"Loaded requests. Total number of requests: {len(df_requests)}")

    # load vehicles
    file_path = os.path.join(config.VEHICLES_DIR, "vehicles.csv")
    df_vehicles = disk.read_vehicles(file_path)

    unique_dates = df_requests['date'].unique()
    total_time_start = time.time()
    for date in unique_dates:
        start_time = time.time()
        file_exists = disk.vehicle_runs_exist(config.BASELINE_OUTPUT_DIR, date, suffix, num_vehicles, time_limit)
        if file_exists:
            print(f"skipping date={date}, suffix={suffix}, num_vehicles={num_vehicles}, time_limit={time_limit}, file already exists")
            continue
        data = optimizer.create_data_model(date, df_requests, time_matrix, df_vehicles, num_vehicles)
        df_vehicle_runs = optimizer.run_vrp(data, time_limit)
        if df_vehicle_runs is not None:
            disk.write_vehicle_runs(df_vehicle_runs, config.BASELINE_OUTPUT_DIR, date, suffix, num_vehicles, time_limit)
            print(f"successfully finished date={date}, suffix={suffix}, num_vehicles={num_vehicles} in {time.time()-start_time} seconds")
    print(f"done with suffix={suffix}, num_vehicles={num_vehicles} in {time.time() - total_time_start} seconds")

