import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from algo import exact, heuristic

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
import random
items = [(30,20),(30,20),(30,20),(30,20),(30,20),(30,20),(30,20),(30,20),(30,20),(30,20),(32,22),(32,22),(32,22),(32,22),(32,22),(32,22),(32,22),(32,22),(36,25),(36,25),(36,25),(36,25),(36,25),(36,25),(40,28),(40,28),(40,28),(40,28),]
random.shuffle(items)
stocks = [(90,90),(90,90),(90,90),(90,90),]

# result, fill_percentage, solutionTime = exact.exact_2d_csp(items, stocks, timeout=1200, threads=32, verbose=True)
result, fill_percentage, solutionTime = heuristic.heuristic_2d_csp(items, stocks, verbose=True)

plot_result(result, items, stocks, 'heu')
