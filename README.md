# Paratransit Rolling Horizon Heuristic Baseline

This is the baseline offline heuristics used in the paper below.

Offline Pickup and Delivery Problem with Time Windows via Rolling Horizon Trip-Vehicle Assignment, Y Kim, D Edirimanna, M Wilbur, P Pugliese, A Laszka, A Dubey, S Samaranayake, accepted in The 37th AAAI Conference on Artificial Intelligence


---
## Guideline 

I) Unzip the data file 

II) Run schell script
```
sh bin/runsim.sh
```
bin/runsim.sh is the shell script to run app/run_sim.py file with varying configurations. The results will be stored in data/baseline_output.

#### Parameters to set 

```DATA_TYPE``` - region of the data (set either "Chattanooga" or "NYC")

```SAMPLE_PER``` - sampled percentage of the data (We use the full (100%) data of Chattanooga dataset and sample 1% and 20% of NYC data)

```NUM_VEHICLES``` - fleet size

```TIME_LIMIT```- unit is milisecond per request (Since we utilize anytime algorithm)

III) Post processing to get results as csv file
```
python app/post_processing.ipynb
```
create output csv file that is stored in data/processed_baseline_output directory. 

---

## Data Folder Description
1. data/map - (a) nodes.csv with columns of 'node_id', 'lat', 'lon' (b) edges.csv with columns of 'source_node', 'target_node', 'edge_weight' (c) times.csv is travel time matrix
2. data/requests - column names are 'origin node', 'origin lon', 'origin lat', 'destin node', 'destin lon', 'destin lat', 'time', 'date'
3. data/vehicles - column names are 'vehicle id', 'node id', 'node lat', 'node lon', 'start time', 'capacity'

To generate data for other regions, one can use [PrepforOpenRidepoolSimulator](https://github.com/youngseo-Kim/PrepforOpenRidepoolSimulator)

---
## Required python packages

ortools
fiona
pyproj
rtree
shapely
geopandas
jupyterlab

___
## Contributers
This is mainly implemented by Mike Wilbur (wilburmike25@gmail.com) and edited by Youngseo Kim (yk796@cornell.edu). 
