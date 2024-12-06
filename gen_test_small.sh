#!/bin/bash

# Define an array of sizes
sizes=(125 250 375 500 625 750 875)

# Prompt the user for the number of test cases
read -p "Enter the number of test cases: " num_test_cases

# Loop over the sizes array
for size in "${sizes[@]}"; do
    # Generate test case
    python3 CSP_genTestCase.py "$size" "$num_test_cases"
done