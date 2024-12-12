import os
from concurrent.futures import ProcessPoolExecutor
#filenum = [10000000000,]

# Define arrays for the test case folders, MR variables, and sort modes 1000, 2000, 3000, 4000, 5000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000
filenum = [1000, 2000, 3000, 4000, 5000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000,100000000000, 1000000000000]

testcase_folders = [f'testcase_{i}' for i in filenum]+ [f'testcase_fixed_{i}' for i in filenum]

mr_vars = ["BAF", "BSSF", "BL", "BLSF"]
sort_modes = ["FF", "FT", "TF", "TT"]

# Generate all combinations of parameters
commands = [
    f"python CSP2D.py {folder} heuristic {mr_var} {sort_mode}"
    for folder in testcase_folders
    for mr_var in mr_vars
    for sort_mode in sort_modes
]

# Function to execute a single command
def run_command(command):
    # print(f"Executing: {command}")
    result = os.system(command)
    if result != 0:
        print(f"Error: Execution failed for command: {command}")
    return result

# Split the commands across 4 processes
def main():
    with ProcessPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(run_command, commands))

    # Check if any commands failed
    failed_commands = [cmd for cmd, result in zip(commands, results) if result != 0]
    if failed_commands:
        print("The following commands failed:")
        for cmd in failed_commands:
            print(cmd)
    else:
        print("All tasks completed successfully!")

if __name__ == "__main__":
    main()