import os
import random
import csv
import shutil

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

def prepare_workspace():
    folders = ['dataset', 'results', 'results/exact', 'results/heuristic']
    ensure_folders_exist(folders)
    # Base case
    items = [(2, 1), (2, 1), (2, 1), (2, 1), (2, 1), (4, 2), (4, 2), (4, 2), (4, 2), (4, 2), (5, 3), (5, 3), (7, 4), (7, 4), (7, 4), (8, 5), (8, 5),]
    stocks = [(24, 14),]
    NUM_CASE = 10
    for i in range(NUM_CASE + 1):
        if i == 0:
            items = [(2, 1), (2, 1), (2, 1), (2, 1), (2, 1), (4, 2), (4, 2), (4, 2), (4, 2), (4, 2), (5, 3), (5, 3), (7, 4), (7, 4), (7, 4), (8, 5), (8, 5),]
            stocks = [(24, 14),]
        else:
            items, stocks = generate_test_case()

        # Write to CSV in simplified format
        with open(f'dataset/CASE_{i}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write items count and items
            writer.writerow([len(items)])
            writer.writerows(items)
            
            # Write stocks count and stocks
            writer.writerow([len(stocks)])
            writer.writerows(stocks)

        # print(f"Generated CASE_{i}.csv")

prepare_workspace()
