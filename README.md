# Paratransit Rolling Horizon Heuristic Baseline

This is mainly implemented by Mike Wilbur (wilburmike25@gmail.com) and edited by Youngseo Kim (yk796@cornell.edu). 

## Guideline 

```
sh bin/runsim.sh
```
bin/runsim.sh is the shell script to run app/run_sim.py file with varying configurations. The results will be stored in data/baseline_output.

Parameters to set 
```DATA_TYPE``` - region of the data (set either "Chattanooga" or "NYC")
```SAMPLE_PER``` - sampled percentage of the data (We use the full (100%) data of Chattanooga dataset and sample 1% and 20% of NYC data)

```
python app/post_processing.ipynb
```
create output csv file that is stored in data/processed_baseline_output directory. 

## Data Folder Description:


## Required python packages

ortools
fiona
pyproj
rtree
shapely
geopandas
jupyterlab
