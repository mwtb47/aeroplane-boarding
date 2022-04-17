import argparse
import time

import pandas as pd

from analysis_tools.multiple_runs import Simulations

    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', required=False, default=10, type=int, help="Number of rows in plane (default: 10)")
    parser.add_argument('--abreast', required=False, default="3,3", type=str, help="Comma separated seat blocks. e.g. '3,3' for 3 seats, aisle, 3 seats (default: '3,3'")
    parser.add_argument('--bag-percent', required=False, default=50, type=int, help="Percentage of passengers with bags (default: 50)")
    parser.add_argument('--slow-medium-fast', required=False, default="30,40,30", type=str, help="Percentage of slow, medium, and fast boarders (default: '30,40,30')")
    parser.add_argument('--iterations', required=False, default=1000, type=int, help="Number of simulations per specification (default: 1,000)")
    parser.add_argument('--simulate-plot', required=True, type=str, help="Either 'simulate' or 'plot'")
    parser.add_argument('--simulate-by-method', action='store_true', help="Perform simulations by boarding method")
    parser.add_argument('--simulate-by-aisles', action='store_true', help="Perform simulations by aisle arrangement")
    parser.add_argument('--simulate-by-groups', action='store_true', help="Perform simulations by number of groups")
    parser.add_argument('--plot-by-method', action='store_true', help="Plot simulations by boarding method")
    parser.add_argument('--plot-by-aisles', action='store_true', help="Plot simulations by aisle arrangement")
    parser.add_argument('--plot-by-groups', action='store_true', help="Plot simulations by number of groups")
    parser.add_argument('--plot-regression-by-method', action='store_true', help="Plot regression of simulations by boarding method")
    parser.add_argument('--plot-std-by-method', action='store_true', help="Plot S.D. of simulations by boarding method")
    args = parser.parse_args()

    if args.simulate_plot not in ('simulate', 'plot'):
        raise ValueError("--simulate-plot must be simulate or plot")

    elif args.simulate_plot == 'simulate':
        if not any((args.simulate_by_method, args.simulate_by_aisles, args.simulate_by_groups)):
            raise ValueError((
                "With --simulate-plot=simulate, at least one of --simulate-by-method,\n"
                "    --simulate-by-aisles or --simulate-by-groups must be chosen"
            ))
    elif args.simulate_plot == 'plot':
        if not any((args.plot_by_method, args.plot_by_aisles, args.plot_by_groups)):
            raise ValueError((
                "With --simulate-plot=plot, at least one of --plot-by-method,\n"
                "    --plot-by-aisles, --plot-by-groups, --plot-regression-by-method or\n"
                "    --plot-std-by-method must be chosen"
            ))

    rows = args.rows
    abreast = [int(i) for i in args.abreast.split(',')]
    bag_percent = args.bag_percent / 100
    slow_medium_fast = [int(i) / 100 for i in args.slow_medium_fast.split(',')]
    iterations = args.iterations


    if args.simulate_plot == 'simulate':
        s = Simulations(rows, abreast, bag_percent, slow_medium_fast, iterations)
        if args.simulate_by_method:
            s.steps_by_method()
        if args.simulate_by_aisles:
            start = time.perf_counter()
            s.steps_by_aisles()
            end = time.perf_counter()
            print(end - start)
        if args.simulate_by_groups:
            start = time.perf_counter()
            s.steps_by_groups()
            end = time.perf_counter()
            print(end - start)

    

if __name__ == "__main__":
    main()

