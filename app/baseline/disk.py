import os
import pandas as pd
import numpy as np
import datetime as dt
from . import config


##### Helper functions #####


def time_str_to_int(t_str, date):
    hour, minute, sec = [int(x) for x in t_str.split(":")]
    dt_obj = dt.datetime(date.year, date.month, date.day, hour=hour, minute=minute, second=sec)
    result = dt_obj - dt.datetime(date.year, date.month, date.day)
    return int(result.total_seconds())


def date_str_to_dateobj(d_str):
    year, month, day = [int(x) for x in d_str.split("-")]
    return dt.date(year, month, day)


##### Read from Disk #####


def read_nodes(file_path):
    df_nodes = pd.read_csv(file_path, names=['node_id', 'lat', 'lon'])
    df_nodes['node_id'] = df_nodes['node_id'].apply(lambda x: x - 1)
    return df_nodes


def read_edges(file_path):
    df_edges = pd.read_csv(file_path, names=['source', 'target', 'travel_time'])
    df_edges['source'] = df_edges['source'].apply(lambda x: x - 1)
    df_edges['target'] = df_edges['target'].apply(lambda x: x - 1)
    return df_edges


def read_time_matrix(file_path):
    time_matrix = np.loadtxt(file_path, delimiter=",", dtype=int)
    time_matrix = time_matrix.tolist()
    return time_matrix


def read_requests(file_path, time_matrix=None):
    columns = ['request_id', 'source', 'source_lon', 'source_lat', 'target', 'target_lon', 'target_lat', 'time', 'date']
    df_requests = pd.read_csv(file_path, names=columns)
    df_requests['date'] = df_requests['date'].apply(lambda x: date_str_to_dateobj(x))
    df_requests['time'] = df_requests.apply(lambda row: time_str_to_int(row['time'], row['date']), axis=1)
    df_requests['source'] = df_requests['source'].apply(lambda x: x - 1)
    df_requests['target'] = df_requests['target'].apply(lambda x: x - 1)
    if time_matrix is not None:
        df_requests['source_window_start'] = df_requests['time']
        df_requests['source_window_end'] = df_requests['source_window_start'].apply(lambda x: x + config.MAX_WAITING_TIME)
        df_requests['target_window_start'] = df_requests.apply(lambda row: row['source_window_start'] + time_matrix[row['source']][row['target']], axis=1)
        df_requests['target_window_end'] = df_requests.apply(lambda row: row['target_window_start'] + config.MAX_DELAY_TIME, axis=1)
    return df_requests


def read_vehicles(file_path):
    columns = ['vehicle_id', 'node_id', 'lat', 'lon', 'time', 'capacity']
    df = pd.read_csv(file_path, names=columns)
    df['node_id'] = df['node_id'].apply(lambda x: x - 1)
    df['vehicle_id'] = df['vehicle_id'].apply(lambda x: x - 1)
    df['time'] = df.apply(lambda row: time_str_to_int(row['time'], dt.date(2021, 1, 5)), axis=1)
    df = df.sort_values(by=['vehicle_id'])
    return df


def write_vehicle_runs(df, dirpath, date, data_type, suffix, num_vehicles, time_limit):
    file_path = os.path.join(dirpath, f"{date.year}_{date.month}_{date.day}_{num_vehicles}_{data_type}_{suffix}_{time_limit}.csv")
    df.to_csv(file_path, index=False)


def vehicle_runs_exist(dirpath, date, data_type, suffix, num_vehicles, time_limit):
    file_path = os.path.join(dirpath, f"{date.year}_{date.month}_{date.day}_{num_vehicles}_{data_type}_{suffix}_{time_limit}.csv")
    result = os.path.exists(file_path)
    return result


def read_vehicle_runs(dirpath):
    dfs = []
    for filename in os.listdir(dirpath):
        if filename.endswith(".csv"):
            filepath = os.path.join(dirpath, filename)
            temp = filename.split("_")
            year, month, day, num_vehicles, perc, time_limit_temp = int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]), temp[4], temp[5]
            time_limit = time_limit_temp.split(".")[0]
            date = dt.date(year, month, day)
            df_temp = pd.read_csv(filepath)
            df_temp['date'] = date
            df_temp['perc'] = int(perc)
            df_temp['num_vehicles'] = num_vehicles
            df_temp['time_limit'] = int(time_limit)
            dfs.append(df_temp)
    df = pd.concat(dfs, ignore_index=True)
    return df
