import os
from ortools.constraint_solver import routing_enums_pb2


# # filepaths
# REQUESTS_DIR = os.path.join(os.getcwd(), "data", "data", "requests")
# MAP_DIR = os.path.join(os.getcwd(), "data", "data", "map")
# VEHICLES_DIR = os.path.join(os.getcwd(), "data", "data", "vehicles")
# BASELINE_OUTPUT_DIR = os.path.join(os.getcwd(), "data", "baseline_output")

# sim settings
VEHICLE_CAPACITY = 8
MAX_WAITING_TIME = 1800 # 30 minutes
MAX_DELAY_TIME = 1800 # 30 minutes
DWELL_TIME = 300 # 5 minutes
DAY_END_TIME = 90000 # @Mike, Could we set this to 86400? 
#NUM_VEHICLES_1 = [3, 4, 5, 6]
#NUM_VEHICLES_10 = [3, 4, 5, 6]
#NUM_VEHICLES_20 = [30, 40, 50, 60]

# VRP settings
N_CORES = 5
START_CUMUL_TO_ZERO = True
MAX_VEHICLE_SLACK = 90000  # i don't know what this is, check with Youngseo
#PENALTY_FUN = "sum_all_times"
PENALTY_FUN = "sum_day_end_time"
FIRST_SOLUTION_STRATEGY = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
LOCAL_SEARCH_METAHEURISTIC = routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING
VRP_TIME_LIMIT = None # total time limit
LOG_SEARCH = False
LOGGING = False