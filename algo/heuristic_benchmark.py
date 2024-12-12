from algo.heuristic_benchmark_lib.driver import mr_vars, sort_modes, maxrect_driver
import json
def heuristic_benchmark(products, stocks):
    output_data = {}
    for mr_var in mr_vars:
        for sort_mode in sort_modes:
            result, fill_percentage, fill_ratio, solution_time = maxrect_driver(products, stocks, mr_var, sort_mode, False)
            output_data[f'{mr_var}_{sort_mode}'] = {
                'result': result,
                'fill_percentage': fill_percentage,
                'fill_ratio': fill_ratio,
                'solution_time': solution_time
            }
    return output_data