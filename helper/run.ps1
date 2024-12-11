# Define arrays of parameters
# Array of numbers
$numbers = @(1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000)

# Concatenate each number with 'testcase_'
$testcase_folders = $numbers | ForEach-Object { "testcase_$($_)" }
$algorithms = @("H_baf", "H_blsf", "H_bssf", "H_bl")

# Loop over test case folders and algorithms
foreach ($testcase_folder in $testcase_folders) {
    foreach ($algo in $algorithms) {
        python CSP2D.py $testcase_folder $algo
    }
}
