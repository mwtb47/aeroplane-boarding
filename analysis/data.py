from concurrent.futures import ProcessPoolExecutor
from itertools import product
import os

import pandas as pd

from simulation.visualisations import progress_bar
from simulate import BoardingSim


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
        self.iterations = range(iterations)
        self.max_workers = os.cpu_count() - 1
        self.boarding_methods = [
            'front-to-back', 
            'back-to-front', 
            'WMA', 
            'front-to-back WMA', 
            'back-to-front WMA', 
            'random', 
            'optimal',
        ]

    def _run_simulations(
            self,
            job: str,
            rows: int,
            abreast: list,
            boarding_methods: list,
            bag_percent: float | list,
            slow_average_fast: list,
            n_groups: int | list):
        """Perform the specified number of simulations for each combination
        of parameters. Save the results as a csv file.
        """
        parameters = list(product(
            [rows],
            [abreast] if isinstance(abreast[0], int) else abreast,
            boarding_methods,
            [bag_percent] if isinstance(bag_percent, float) else bag_percent,
            [slow_average_fast],
            [n_groups] if isinstance(n_groups, int) else n_groups,
        ))
        n_parameters = len(parameters)

        print(f"\nBoarding by {job}...")
        progress_bar(-1, n_parameters, 'combination', job)

        df = pd.DataFrame()
        for count, (rows, abreast, boarding_method, bag_percent, slow_average_fast, n_groups) in enumerate(parameters):
            aero = BoardingSim(rows, abreast, boarding_method, bag_percent, slow_average_fast, n_groups)
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                results = [executor.submit(aero.boarding_steps).result() for _ in self.iterations]
            data = {
                'configuration': ",".join(str(a) for a in abreast),
                'boarding_method': boarding_method,
                'bag_percent': bag_percent,
                'n_groups': n_groups,
                'steps': results,
            }
            df = pd.concat([df, pd.DataFrame(data)], axis=0)
            progress_bar(count, n_parameters, 'combination', job)
        
        df.to_csv(f'data2/by_{job}_data_additional.csv', index=False)
        print(f"by_{job}_data_additional.csv saved.\n")

    def steps_by_method(self):
        """Save a csv file with the results from n simulations of 
        each combination of method and bag percentage.
        """
        bag_percentages = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
        self._run_simulations(
            "method",
            self.rows,
            self.abreast,
            self.boarding_methods,
            bag_percentages,
            self.slow_average_fast,
            self.rows,
        )
    
    def steps_by_aisles(self):
        """Save a csv file with the results from n simulations of 
        each combination of method and seating configuration.
        """
        configurations = [[3,3], [2,2,2]]
        self._run_simulations(
            "aisles",
            self.rows,
            configurations,
            self.boarding_methods,
            self.bag_percent,
            self.slow_average_fast,
            self.rows,
        )
    
    def steps_by_groups(self):
        """Save a csv file with the results from n simulations of 
        each combination of method, bag percentage and number of groups.
        """
        boarding_methods = ['front-to-back', 'back-to-front', 'front-to-back WMA', 'back-to-front WMA']
        bag_percentages = [0, 0.5, 1]
        n_groups = [1, 3, 6, 9, 12, 15]
        self._run_simulations(
            "groups",
            self.rows,
            self.abreast,
            boarding_methods,
            bag_percentages,
            self.slow_average_fast,
            n_groups,
        )