# My scripts
import scripts.testCSP_real_exact as exact_algo
import scripts.maxrect_multi as heuristic_algo
from scripts.maxrect_multi import Rectangle, MaxRects_BSSF
# Imports
import os
import csv
import time
import random
import shutil
import json
import multiprocessing

NUM_CASE = 100
IN_DIR = './dataset/'
OUT_DIR = './results/'

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
        return -1, -1
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

    return -1, -1

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
        return -1, -1
    
    # Calculate the total area of placed rectangles
    placed_rectangles = {rect.rid for bp in bin_packs for rect in bp[1].used_rectangles}
    total_rect_area = sum(rect.width * rect.height for rect in rectangles if rect.rid in placed_rectangles)

    # Calculate the total area of used stock bins
    used_stock_bins = {bp[0] for bp in bin_packs}
    total_stock_area = sum(stocks[idx][0] * stocks[idx][1] for idx in used_stock_bins)

    # Calculate fill percentage
    fill_percentage = (total_rect_area / total_stock_area) * 100 if total_stock_area > 0 else 0

    return fill_percentage, run_time

def ensure_folders_exist(folders):
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Deleted folder: {folder}")
        os.makedirs(folder)
        print(f"Created folder: {folder}")

def generate_test_case(variableNum=10000):
    max_items_size = 40
    max_stocks_size = 10
    while True:
        items_size = random.randint(1, max_items_size)
        stocks_size = random.randint(1, max_stocks_size)
        if items_size ** 2 * stocks_size < variableNum and items_size >= stocks_size:
            break
    while True:
        items = [(random.randint(1, 40), random.randint(1, 40)) for _ in range(items_size)]
        total_items_area = sum(w * h for w, h in items)
        stocks = [(random.randint(10, 100), random.randint(10, 100)) for _ in range(stocks_size)]
        total_stocks_area = sum(w * h for w, h in stocks)
        if total_items_area < total_stocks_area:
            return items, stocks

def write_csv(filename: str, items, stocks):
    # Write to CSV in simplified format
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write items count and items
        writer.writerow([len(items)])
        writer.writerows(items)
        
        # Write stocks count and stocks
        writer.writerow([len(stocks)])
        writer.writerows(stocks)

def prepare_workspace():
    folders = [IN_DIR, OUT_DIR, f'{OUT_DIR}exact', f'{OUT_DIR}heuristic']
    ensure_folders_exist(folders)
    # Base case
    items = [(2, 1), (2, 1), (2, 1), (2, 1), (2, 1), (4, 2), (4, 2), (4, 2), (4, 2), (4, 2), (5, 3), (5, 3), (7, 4), (7, 4), (7, 4), (8, 5), (8, 5),]
    stocks = [(24, 14),]
    write_csv(f'{IN_DIR}BASE.csv', items, stocks)
    
    for i in range(NUM_CASE):
        items, stocks = generate_test_case()
        write_csv(f'{IN_DIR}CASE_{i}.csv', items, stocks)

def process_file(filename):
    items, stocks = get_dataset(IN_DIR + filename)
    print(f'Processing {filename}')

    res_h, time_h = heuristic_solution(items, stocks, filename, OUT_DIR)
    res_e, time_e = exact_solution(items, stocks, filename, OUT_DIR)
    
    result = {
        "filename": filename,
        "items": items,
        "stocks": stocks,
        "num_items": len(items),
        "num_stocks": len(stocks),
        "fill_h": f"{res_h:.2f}" if res_h != -1 else "N/A",
        "fill_e": f"{res_e:.2f}" if res_e != -1 else "N/A",
        "h_on_e": f"{(res_h / res_e * 100):.2f}" if res_h != -1 and res_e not in [-1, 0] else "N/A",
        "time_h": f"{time_h:.4f}" if time_h != -1 else "N/A",
        "time_e": f"{time_e:.4f}" if time_e != -1 else "N/A",
    }
    return result

if __name__ == "__main__":
    
    prepare_workspace()

    files = os.listdir(IN_DIR)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(process_file, files)

    # In case we want to go back to csv :)
    # with open("results.csv", mode="w", newline="") as file:
    #     writer = csv.DictWriter(file, fieldnames=[
    #         "filename", "num_items", "num_stocks", "fill_h", "fill_e", "time_h", "time_e"
    #     ])
    #     writer.writeheader()

    #     for result in results:
    #         writer.writerow({
    #             "filename": result["filename"],
    #             "num_items": result["num_items"],
    #             "num_stocks": result["num_stocks"],
    #             "fill_h": result["fill_h"],
    #             "fill_e": result["fill_e"],
    #             "time_h": result["time_h"],
    #             "time_e": result["time_e"],
    #         })

    with open("results.json", mode="w") as file:
        json.dump(results, file)

    print('\nFINAL RESULTS\n=============\n')
    for result in results:
        print(f'{result["filename"]}\tResults: H ({result["fill_h"]}%), E ({result["fill_e"]}%)')
        print(f'\t\tHeuristics acheived\t{result["h_on_e"]}%')
        print(f'\t\tTime: H ({result["time_h"]} s), E ({result["time_e"]} s)')
        print()