import concurrent.futures
from itertools import product
import os
import sys

import pandas as pd

from simulate import BoardingSim


def progress_bar(current_frame: int, total_frames: int, message: str):
    progress = int(80 * (current_frame + 1) / total_frames)
    remaining = 80 - progress
    sys.stdout.write(f"\r|{'█'* progress}{' ' * remaining}|   Combination {current_frame + 1} of {total_frames}")
    sys.stdout.flush()
    if current_frame + 1 == total_frames:
        print(f"\nCompleted iterations of steps by {message}")

class Simulations:
    """Class with methods to run boarding simulations and save csv files
    for the following:
        - steps by boarding method
        - steps by number of boarding aisles
        - steps by number of boarding groups
    """
    def __init__(self, rows: int, abreast: int, bag_percent: float, slow_average_fast: list, iterations: int):
        self.rows = rows
        self.abreast = abreast
        self.bag_percent = bag_percent
        self.slow_average_fast = slow_average_fast
        self.iterations = iterations
        self.max_workers = os.get_cpu()
        self.boarding_methods = [
            'front-to-back', 
            'back-to-front', 
            'WMA', 
            'front-to-back WMA', 
            'back-to-front WMA', 
            'random', 
            'optimal',
        ]

    def steps_by_method(self):
        """Save a csv file with the results from n simulations of 
        each combination of method and bag percentage.
        """
        print("Boarding by method")
        bag_percentages = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
        parameters = list(product(self.boarding_methods, bag_percentages))[:4]
        
        df = pd.DataFrame()
        for n, (boarding_method, bag_percent) in enumerate(parameters):
            aero = BoardingSim(
                self.rows,
                self.abreast,
                boarding_method,
                bag_percent, 
                self.slow_average_fast,
                self.rows,
            )
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                results = [executor.submit(aero.boarding_steps) for _ in range(self.iterations)]
            data = {
                'boarding_method': boarding_method,
                'bag_percent': bag_percent,
                'steps': results,
            }
            df = df.append(pd.DataFrame(data), ignore_index=True)
            progress_bar(n, len(parameters), "method")
        
        df.to_csv('data2/by_method_data_additional.csv', index=False)
    
    def steps_by_aisles(self):
        """Save a csv file with the results from n simulations of 
        each combination of method and seating configuration.
        """
        print("Boarding by aisles...")
        configurations = [[3,3], [2,2,2]]
        parameters = list(product(self.boarding_methods, configurations))
        n_parameters = len(parameters)

        df = pd.DataFrame()
        for n, (boarding_method, abreast) in enumerate(parameters):
            aero = BoardingSim(
                self.rows, 
                abreast, 
                boarding_method, 
                self.bag_percent,
                self.slow_average_fast,
                self.rows,
            )
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                results = [executor.submit(aero.boarding_steps) for _ in range(self.iterations)]
            data = {
                'boarding_method': boarding_method,
                'configuration': str(abreast),
                'steps': results,
            }
            df = df.append(pd.DataFrame(data), ignore_index=True)
            progress_bar(n, n_parameters, "aisles")

        df.to_csv('data2/by_aisles_data.csv', index=False)
    
    def steps_by_groups(self):
        """Save a csv file with the results from n simulations of 
        each combination of method, bag percentage and number of groups.
        """
        print("Boarding by groups...")
        boarding_methods = ['front-to-back', 'back-to-front', 'front-to-back WMA', 'back-to-front WMA']
        bag_percentages = [0, 0.5, 1]
        n_groups = [1, 5, 10, 15]
        parameters = list(product(boarding_methods, bag_percentages, n_groups))[:4]
        n_parameters = len(parameters)

        df = pd.DataFrame()
        for n, (boarding_method, bag_percent, groups) in enumerate(parameters):
            aero = BoardingSim(
                self.rows, 
                self.abreast, 
                boarding_method, 
                bag_percent,
                self.slow_average_fast,
                groups
            )
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                results = [executor.submit(aero.boarding_steps) for _ in range(self.iterations)]
            data = {
                'boarding_method': boarding_method,
                'bag_percent': bag_percent,
                'n_groups': groups,
                'steps': results,
            }
            df = df.append(pd.DataFrame(data), ignore_index=True)
            progress_bar(n, n_parameters, "groups")
        
        df.to_csv('data2/by_number_groups_data.csv', index=False)