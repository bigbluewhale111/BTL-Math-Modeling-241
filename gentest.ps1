# Define an array of sizes 
$sizes = @(1000, 2000, 3000, 4000, 5000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000,100000000000, 1000000000000)
# Define the number of test cases
$num_test_cases = 100

# Define the types
$types = @("fixed", "normal")

# Loop over the sizes array
foreach ($size in $sizes) {
    foreach ($type in $types) {
        # Generate test case
        python CSP_genTestCase.py $size $num_test_cases $type
    }
}