#!/bin/bash

SUFFIX=100 # sampled percentage

for i in 3 4 5 6
do
	for t in 1 2 3 4 # 0.1, 0.2, 0.3, 0.4 second
	do
		python app/run_sim.py --suffix $SUFFIX --num_vehicles $i --time_limit $t &
	done
done
wait
echo "All done"