import json
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from algo import exact

least_space = lambda rectangles: sum([rect[0] * rect[1] for rect in rectangles])

def plot_result(result, rectangles, sheets, output_filename='output.png'):
    fig, axs = plt.subplots(len(sheets), figsize=(8, 6 * len(sheets)))
    if len(sheets) == 1:
        axs = [axs]  # Ensure axs is iterable
    for k, ax in enumerate(axs):
        ax.set_title(f"Sheet {k} - {sheets[k][0]}x{sheets[k][1]}")
        sheet_width, sheet_height = sheets[k]
        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_height)
        ax.set_aspect('equal')
        for i in range(len(result)):
            if result[i]['sheet'] == k:
                x = float(result[i]['x'])
                y = float(result[i]['y'])
                rotated = result[i]['rotated']
                rect_width = rectangles[i][1] if rotated else rectangles[i][0]
                rect_height = rectangles[i][0] if rotated else rectangles[i][1]
                rect = patches.Rectangle((x, y), rect_width, rect_height, linewidth=1, edgecolor='black', facecolor='cyan', alpha=0.5)
                ax.add_patch(rect)
                ax.text(x + rect_width / 2, y + rect_height / 2, str(i), ha='center', va='center')
        ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python testCSP_exact_pulp.py <testcase_folder>")
        exit(1)
    testcase_folder = sys.argv[1]
    if not os.path.exists(testcase_folder):
        print("Test case folder not found.")
        exit
    os.chdir(testcase_folder)
    if not os.path.exists('testcase.json'):
        print("Test case file not found.")
        exit(1)
    # load test cases from json file
    testcases = None
    with open('testcase.json', 'r') as json_file:
        testcases = json.load(json_file)
    if testcases is None:
        print("No test cases found.")
        exit(1)
    
    testcaseCount = len(testcases)
    for i in range(testcaseCount):
        items, stocks = testcases[i]['items'], testcases[i]['stocks']
        items_size, stocks_size = len(items), len(stocks)
        print(f"Items has {items_size} elements: {items}")
        print(f"Stocks has {stocks_size} elements: {stocks}")
        print(f"Variable count: {testcases[i]['variable_count']}")
        result, fill_percentage, solutionTime = exact.exact_2d_csp(items, stocks, timeout=1000, threads=8, verbose=True)
        if result is None:
            print("No solution found.")
        else:
            print(result)
            print(f"Fill percentage: {fill_percentage}")
            print(f"Solution time: {solutionTime}")
            plot_result(result, items, stocks, f"output_{i}.png")
        # Append results to JSON file
        output_data = {
            'items_size': items_size,
            'stocks_size': stocks_size,
            'fill_percentage': fill_percentage,
            'solution_time': solutionTime
        }
        with open('results.json', 'a') as json_file:
            json.dump(output_data, json_file)
            json_file.write('\n')