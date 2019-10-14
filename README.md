# Source code for TSA

Usage:

python Code/auction.py [-ewc] [-p path_to_input_data] [-s file_with_influence_data] [-a file_with_advertiser_data] [-i number_of_iterations] [-o path_for_output] [-g seed_for_group_split] [-r seed_for_random_allocation]

For the baseline (BORGS), run with the -c option, without the -e and -w option.
For TSA, runt with the -c, -e, and -w option.

BORGS example:

python Code/auction.py -p Flixster/ -s influence_10_iterations_top.csv -a value=random(0.5,2).csv -i 100 -o Results/results_flixster.csv -g 138579744 -r 197285670 -c

TSA example:

python Code/auction.py -p Flixster/ -s influence_10_iterations_top.csv -a value=random(0.5,2).csv -i 100 -o Results/results_flixster.csv -g 138579744 -r 197285670 -c -w -e
