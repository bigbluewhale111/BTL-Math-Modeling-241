#!/bin/bash

# Define arrays of parameters
testcase_folders=("testcase_1000" "testcase_2000" "testcase_3000" "testcase_4000" "testcase_5000")
algorithms=("heuristic" "exact" )

# Loop over test case folders and algorithms
for testcase_folder in "${testcase_folders[@]}"; do
    for algo in "${algorithms[@]}"; do
        python3 CSP2D.py "$testcase_folder" "$algo"
    done
done