#!/bin/bash

# Define an array of sizes
sizes=(1000 2000 3000 4000 5000)

# Prompt the user for the number of test cases
read -p "Enter the number of test cases: " num_test_cases

# Loop over the sizes array
for size in "${sizes[@]}"; do
    # Generate test case
    python3 CSP_genTestCase.py "$size" "$num_test_cases"
done