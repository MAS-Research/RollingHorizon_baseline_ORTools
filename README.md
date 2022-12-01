# Paratransit Rolling Horizon Heuristic Baseline

This is mainly implemented by Mike Wilbur (wilburmike25@gmail.com) and edited by Youngseo Kim (yk796@cornell.edu). 

## Guideline 
bin/runsim.sh is the shell script to run app/run_sim.py file with varying configurations. SUFFIX is sampled percentage. If SUFFIX=100, we use full data from Chattanooga dataset. If SUFFIX=1 or 20, we use New York City dataset sampled by 1%, 20%, respectively. The results will be stored in data/baseline_output. Then, one can use app/post_processing.ipynb to create output csv file that is stored in data/processed_baseline_output directory. 


## Required python packages

ortools
fiona
pyproj
rtree
shapely
geopandas
jupyterlab
