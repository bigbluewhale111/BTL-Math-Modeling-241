#!/bin/bash

# Define arrays of parameters
testcase_folders=("testcase_125" "testcase_250" "testcase_375" "testcase_500" "testcase_625"  "testcase_750" "testcase_875")
algorithms=("heuristic" "exact" )

# Loop over test case folders and algorithms
for testcase_folder in "${testcase_folders[@]}"; do
    for algo in "${algorithms[@]}"; do
        python3 CSP2D.py "$testcase_folder" "$algo"
    done
done