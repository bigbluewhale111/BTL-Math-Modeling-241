# My scripts
import scripts.testCSP_real_exact as exact_algo
import scripts.maxrect_multi as heuristic_algo
from scripts.maxrect_multi import Rectangle, MaxRects_BSSF
# Imports
import os
import csv
import time

def s_i(inp: str) -> int:
    return int(inp.strip(), 10)

def get_dataset(filename: str):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # items
    M = int(rows[0][0])
    items = [(int(row[0]), int(row[1]), id) for id, row in enumerate(rows[1:1 + M])]

    # stocks
    N = int(rows[1 + M][0])
    stocks = [(int(row[0]), int(row[1])) for row in rows[2 + M:2 + M + N]]

    return items, stocks

def exact_solution(items, stocks, filename: str, output_dir: str):
    run_time = -1
    try:
        start_time = time.time()
        result = exact_algo.two_d_cutting_stock_multiple_sheets(items, stocks)
        end_time = time.time()
        run_time = end_time - start_time
    except:
        print('Failed')
        return -1
    print(result)
    if result is not None:
        exact_algo.plot_result(result, items, stocks, output_dir + 'exact/' + filename.split('.')[0])

        # Calculate the total area of placed rectangles
        total_rect_area = 0
        used_stock_bins = set()

        for placement in result:
            sheet_index = placement['sheet']
            used_stock_bins.add(sheet_index)

            rect_id = items[result.index(placement)][2]
            width, height = items[result.index(placement)][:2]

            total_rect_area += width * height

        total_stock_area = sum(stocks[sheet][0] * stocks[sheet][1] for sheet in used_stock_bins)
        fill_percentage = (total_rect_area / total_stock_area) * 100 if total_stock_area > 0 else 0
        # print(f"Fill Percentage: {fill_percentage:.2f}%")
        
        return fill_percentage, run_time
    else:
        print("No solution found.")

    return -1

def heuristic_solution(items, stocks, filename: str, output_dir: str):
    # items, stocks = get_dataset(input_dir + filename)

    rectangles = []
    for item in items:
        rectangles.append(Rectangle(item[0], item[1], item[2]))
        
    # Pack rectangles
    start_time = time.time()
    bin_packs, unplaced_rectangles = heuristic_algo.pack_rectangles(rectangles, stocks)
    end_time = time.time()
    run_time = end_time - start_time
    
    # Print results
    for bin_index in range(len(stocks)):
        bin_width, bin_height = stocks[bin_index]
        print(f"\nBin {bin_index} placements (Dimensions: {bin_width} x {bin_height}):")
        # Check if the bin was used
        bin_pack = next((bp for idx, bp in bin_packs if idx == bin_index), None)
        if bin_pack and bin_pack.used_rectangles:
            for rect in bin_pack.used_rectangles:
                print(f"  Rectangle {rect.rid}: x={rect.x}, y={rect.y}, width={rect.width}, height={rect.height}, rotated={rect.rotated}")
        else:
            print("  No rectangles placed in this bin.")

    flag = False
    if unplaced_rectangles:
        flag = True
        print("\nUnfulfilled products:")
        for rect in unplaced_rectangles:
            print(f"  Rectangle {rect.rid}: width={rect.width}, height={rect.height}")

    heuristic_algo.plot_result(bin_packs, rectangles, stocks, output_dir + 'heuristic/' + filename.split('.')[0])
    
    if flag:
        print('Unfulfilled')
        return -1
    
    # Calculate the total area of placed rectangles
    placed_rectangles = {rect.rid for bp in bin_packs for rect in bp[1].used_rectangles}
    total_rect_area = sum(rect.width * rect.height for rect in rectangles if rect.rid in placed_rectangles)

    # Calculate the total area of used stock bins
    used_stock_bins = {bp[0] for bp in bin_packs}
    total_stock_area = sum(stocks[idx][0] * stocks[idx][1] for idx in used_stock_bins)

    # Calculate fill percentage
    fill_percentage = (total_rect_area / total_stock_area) * 100 if total_stock_area > 0 else 0

    return fill_percentage, run_time

items = [(17, 16), (43, 6), (30, 28), (9, 13), (48, 17), (25, 45), (18, 29), (50, 19), (10, 3), (20, 17), (38, 19), (46, 47), (1, 8), (21, 6), (34, 10), (24, 13), (9, 7), (7, 3), (24, 12), (25, 30), (5, 33), (26, 26), (14, 18), (29, 11), (11, 5), (48, 2), (27, 36), (11, 47), (2, 3), (46, 22), (16, 6), (38, 5), (20, 15), (22, 37), (13, 7), (7, 14), (26, 38), (1, 37)]
for i in range(len(items)):
    items[i] = (items[i][0], items[i][0], i)
stocks = [(85, 99), (98, 95)]

res_h = heuristic_solution(items, stocks, 'dbg', 'test/')
print(res_h)