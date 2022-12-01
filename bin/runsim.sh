#!/bin/bash

SAMPLE_PER=100 # sampled percentage
DATA_TYPE="Chattanooga" # "NYC"  

for i in 3
do
	for t in 1 # 0.1, 0.2, 0.3, 0.4 second
	do
		python app/run_sim.py --data_type $DATA_TYPE --sample_per $SAMPLE_PER --num_vehicles $i --time_limit $t &
	done
done
wait
echo "All done"