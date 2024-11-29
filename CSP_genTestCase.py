import random
import json
import sys
import math
import os 

least_space = lambda rectangles: sum([rect[0] * rect[1] for rect in rectangles])
variableCount = lambda n, m: 3*n*m + n + m + n*(n-1)*m*2 + 1

def generate_test_size(variableNum=10000, epsilon=0.1):
    max_stocks_size = math.ceil((variableNum / 18) ** (1./3))
    max_items_size = max_stocks_size * 3
    while True:
        items_size = random.randint(1, max_items_size)
        stocks_size = random.randint(1, max_stocks_size)
        if abs(variableCount(items_size, stocks_size) - variableNum) < epsilon * variableNum and items_size >= stocks_size:
            break
    return items_size, stocks_size

def generate_test_case(items_size, stocks_size, minw, maxw, minh, maxh):
    while True:
        items = [(random.randint(1, minw + 1), random.randint(1, minh + 1)) for _ in range(items_size)]
        total_items_area = sum(w * h for w, h in items)
        stocks = [(random.randint(minw, maxw + 1), random.randint(minh, maxh + 1)) for _ in range(stocks_size)]
        total_stocks_area = sum(w * h for w, h in stocks)
        if total_items_area < total_stocks_area:
            return items, stocks

if __name__ == "__main__":
    # generate test case and put to json file the items and stocks
    if len(sys.argv) != 3:
        print("Usage: python CSP_genTestCase.py <variable_count> <test_case_count>")
        exit(1)
    variable_count = int(sys.argv[1])
    testcases = []
    test_case_count = int(sys.argv[2])
    for i in range(test_case_count):
        print(f"================Test case {i}================")
        items_size, stocks_size = generate_test_size(variable_count)
        while True:
            items, stocks = generate_test_case(items_size, stocks_size, 50, 100, 50, 100)
            if least_space(items) <= least_space(stocks):
                break
        print(f"Items has {items_size} elements: {items}")
        print(f"Stocks has {stocks_size} elements: {stocks}")
        print(f"Variable count: {variableCount(items_size, stocks_size)}")
        # Append results to JSON file
        output_data = {
            'items': items,
            'stocks': stocks,
            'variable_count': variableCount(items_size, stocks_size)
        }
        testcases.append(output_data)
    if not os.path.exists(f'testcase/testcase_{variable_count}'):
        os.makedirs(f'testcase/testcase_{variable_count}')
    with open(f'testcase/testcase_{variable_count}/testcase.json', 'w') as json_file:
        json.dump(testcases, json_file)