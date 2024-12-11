# Array of numbers
$numbers = @(1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000)

# Convert numbers to strings
$testcase_folders = $numbers | ForEach-Object { "$_" }

# Loop over test case folders and algorithms
foreach ($testcase_folder in $testcase_folders) {
    python .\CSP_genTestCase.py $testcase_folder 200
}
