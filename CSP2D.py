import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from algo import exact, heuristic

least_space = lambda rectangles: sum([rect[0] * rect[1] for rect in rectangles])

# def plot_result(result, rectangles, sheets, output_filename='output.png'): # ugly chart
#     fig, axs = plt.subplots(len(sheets), figsize=(8, 6 * len(sheets)))
#     if len(sheets) == 1:
#         axs = [axs]  # Ensure axs is iterable
#     for k, ax in enumerate(axs):
#         ax.set_title(f"Sheet {k} - {sheets[k][0]}x{sheets[k][1]}")
#         sheet_width, sheet_height = sheets[k]
#         ax.set_xlim(0, sheet_width)
#         ax.set_ylim(0, sheet_height)
#         ax.set_aspect('equal')
#         for i in range(len(result)):
#             if result[i]['sheet'] == k:
#                 x = float(result[i]['x'])
#                 y = float(result[i]['y'])
#                 rotated = result[i]['rotated']
#                 rect_width = rectangles[i][1] if rotated else rectangles[i][0]
#                 rect_height = rectangles[i][0] if rotated else rectangles[i][1]
#                 rect = patches.Rectangle((x, y), rect_width, rect_height, linewidth=1, edgecolor='black', facecolor='cyan', alpha=0.5)
#                 ax.add_patch(rect)
#                 ax.text(x + rect_width / 2, y + rect_height / 2, str(i), ha='center', va='center')
#         ax.invert_yaxis()
#     plt.tight_layout()
#     plt.savefig(output_filename)
#     plt.close()

def plot_result(result, rectangles, sheets, output_filename='output.png'):
    n_sheets = len(sheets)
    ncols = int(np.ceil(np.sqrt(n_sheets)))
    nrows = int(np.ceil(n_sheets / ncols))
    fig, axs = plt.subplots(nrows, ncols, figsize=(8 * ncols, 6 * nrows))
    axs = axs.flatten()  # Ensure axs is iterable
    colors = plt.cm.get_cmap('hsv', len(rectangles))

    for k, ax in enumerate(axs[:n_sheets]):
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
                color = colors(i)  # Assign a unique color
                rect = patches.Rectangle((x, y), rect_width, rect_height, linewidth=1, edgecolor='black', facecolor=color, alpha=0.5)
                ax.add_patch(rect)
                ax.text(x + rect_width / 2, y + rect_height / 2, str(i), ha='center', va='center')
        ax.invert_yaxis()
    # Remove unused subplots
    for ax in axs[n_sheets:]:
        fig.delaxes(ax)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testCSP_exact_pulp.py <testcase_folder> <algo>")
        exit(1)
    testcase_folder = sys.argv[1]
    testcase_folder = os.path.join('testcase', testcase_folder)
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
    isExact = None
    if sys.argv[2] == 'exact':
        isExact = True
    elif sys.argv[2] == 'heuristic':
        isExact = False
    else:
        print("Invalid algorithm.")
        exit(1)
    if not os.path.exists(f'{'exact' if isExact else 'heuristic'}_output'):
        os.makedirs(f'{'exact' if isExact else 'heuristic'}_output')
    os.chdir(f'{'exact' if isExact else 'heuristic'}_output')
    testcaseCount = len(testcases)
    for i in range(testcaseCount):
        items, stocks = testcases[i]['items'], testcases[i]['stocks']
        items_size, stocks_size = len(items), len(stocks)
        print(f"Items has {items_size} elements: {items}")
        print(f"Stocks has {stocks_size} elements: {stocks}")
        print(f"Variable count: {testcases[i]['variable_count']}")
        if isExact:
            result, fill_percentage, solutionTime = exact.exact_2d_csp(items, stocks, timeout=1200, threads=64, verbose=True)
        else:
            result, fill_percentage, solutionTime = heuristic.heuristic_2d_csp(items, stocks, verbose=True)
        if result is None:
            print("No solution found.")
        else:
            print(result)
            print(f"Fill percentage: {fill_percentage}")
            print(f"Solution time: {solutionTime}")
            # plot_result(result, items, stocks, f"output_{'exact' if isExact else 'heuristic'}_{i}.png")
        # Append results to JSON file
        output_data = {
            'items_size': items_size,
            'stocks_size': stocks_size,
            'fill_percentage': fill_percentage,
            'solution_time': solutionTime
        }
        with open(f"results_{'exact' if isExact else 'heuristic'}.json", 'a') as json_file:
            json.dump(output_data, json_file)
            json_file.write('\n')
    