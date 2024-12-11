import json
import os
import matplotlib.pyplot as plt
import numpy as np

MAX_NUM = 100000

def parse_results(filename: str):
    lines = [i.strip() for i in open(filename, 'r').readlines()]
    results = []
    for line in lines:
        results.append(json.loads(line))
    return results

def get_avg(res, key):
    tot = 0
    avg_cnt = 0
    for i in res:
        if i[key] is None:
            # print('null!')
            continue
        if i[key] >= 1000:
            # print('null!')
            continue
        avg_cnt += 1
        tot += i[key]
        
    avg = tot / avg_cnt if avg_cnt > 0 else 0
    
    return avg, avg_cnt / len(res)

TEST_DIR = './testcase/'
filenum = [1000, 2000, 3000, 4000, 5000]#, 6000000, 7000000, 8000000, 9000000, 10000000]
files = [f'testcase_{i}' for i in filenum]

modes = ['exact', 'heuristic']

# modes = ['H_baf', 'H_bssf', 'H_blsf', 'H_bl']
colors = ['green', 'red', 'blue', 'black']

# Initialize storage for metrics

success_rate = {'exact': [], 'heuristic': []}
AVG_fill = {'exact': [], 'heuristic': []}
AVG_time = {'exact': [], 'heuristic': []}
Validity = {'exact': [], 'heuristic': []}
# success_rate = {'H_baf': [], 'H_bssf': [], 'H_blsf': [], 'H_bl': []}
# AVG_fill = {'H_baf': [], 'H_bssf': [], 'H_blsf': [], 'H_bl': []}
# AVG_time = {'H_baf': [], 'H_bssf': [], 'H_blsf': [], 'H_bl': []}
# Validity = {'H_baf': [], 'H_bssf': [], 'H_blsf': [], 'H_bl': []}

for file in files:
    res = {mode: parse_results(f'{TEST_DIR}{file}/{mode}_output/results_{mode}.json') for mode in modes}
    for mode in modes:
        avg_fill, isValid_fill = get_avg(res[mode], 'fill_percentage')
        avg_time, isValid_time = get_avg(res[mode], 'solution_time')
        # print(avg_fill, avg_time)
        AVG_fill[mode].append(avg_fill * 100)
        AVG_time[mode].append(avg_time)
        Validity[mode].append(isValid_fill)
    # print(Validity['H_baf'])
# print(np.mean([i for i in AVG_fill['H_bssf']]))
# Prepare data for bar chart (fill percentage)
print(([np.mean(AVG_fill[i]) for i in AVG_fill]))

x = np.arange(len(files))
bar_width = 0.1

plt.figure(figsize=(12, 8))

# Plot Bar Chart for Fill Percentage
for idx, mode in enumerate(modes):
    plt.bar(
        x + idx * bar_width,
        AVG_fill[mode],
        width=bar_width,
        color=colors[idx],
        label=f'{mode.capitalize()} Solution'
    )

plt.xticks(x + bar_width, filenum)
plt.title("Comparison of Average Fill Percentage by Complexity")
plt.xlabel("Variable count")
plt.ylabel("Fill Percentage (%)")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('result_fill')

# Prepare data for line graph (solution time)
plt.figure(figsize=(12, 8))

for idx, mode in enumerate(modes):
    plt.plot(
        x,
        AVG_time[mode],
        marker='o',
        color=colors[idx],
        linestyle='-',
        label=f'{mode.capitalize()} Solution'
    )

plt.xticks(x, filenum)
# plt.title("Comparison of Average Solution Time by Complexity (Log Scale)")
plt.title("Comparison of Average Solution Time by Complexity")
plt.xlabel("Variable count")
plt.ylabel("Solution Time (s)")
plt.yscale('log')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('result_time')

def normalize(values):
    values = np.array(values)
    return (values - np.min(values)) / (np.max(values) - np.min(values))

w = 0.7

cumulative_scores = {algo: 0 for algo in AVG_fill.keys()}

num_test_cases = len(next(iter(AVG_fill.values())))
for i in range(num_test_cases):
    for algo in AVG_fill.keys():
        fill = AVG_fill[algo][i]
        time = AVG_time[algo][i]

        fills = [AVG_fill[a][i] for a in AVG_fill.keys()]
        times = [AVG_time[a][i] for a in AVG_time.keys()]
        normalized_fill = (fill - min(fills)) / (max(fills) - min(fills))  # Higher is better
        normalized_time = 1 - (time - min(times)) / (max(times) - min(times))  # Lower is better

        score = w * normalized_fill + (1 - w) * normalized_time

        cumulative_scores[algo] += score

average_scores = {algo: cumulative_scores[algo] / num_test_cases for algo in cumulative_scores.keys()}

print("Average Scores:")
for algo, avg_score in sorted(average_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{algo}: {avg_score:.3f}")