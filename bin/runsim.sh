#!/bin/bash

DATA_TYPE="Chattanooga" # "NYC"  
SAMPLE_PER=100 # sampled percentage

for NUM_VEHICLES in 3
do
	for TIME_LIMIT in 1 # 0.1, 0.2, 0.3, 0.4 second
	do
		python app/run_sim.py --data_type $DATA_TYPE --sample_per $SAMPLE_PER --num_vehicles $NUM_VEHICLES --time_limit $TIME_LIMIT &
	done
done
wait
echo "All done"