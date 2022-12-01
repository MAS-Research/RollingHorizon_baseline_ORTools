# Paratransit Rolling Horizon Heuristic Baseline

This is mainly implemented by Mike Wilbur (wilburmike25@gmail.com) and edited by Youngseo Kim (yk796@cornell.edu). 

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
1. data/map 
  a. nodes.csv 
  b. edges.csv
  c. times.csv
2. data/requests - 
3. data/vehicles - 

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
