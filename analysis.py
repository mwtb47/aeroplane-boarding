from ast import literal_eval
from copy import deepcopy
from itertools import product
from random import shuffle
from math import ceil

from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from boarding_simulator import Boarding


class Simulations:
    """Class to run simulations of each boarding method and produce a
    boxplot comparing the performace of each method with different 
    proportions of passengers with bags.
    """
    def __init__(self, rows, abreast, slow_average_fast):
        self.rows = rows
        self.abreast = abreast
        self.slow_average_fast = slow_average_fast

    def run_simulations(self):
        """Return a dictionary where the key identifies the method and bag 
        percentage, and the value is a list of the results from the 1,000
        simulations.
        """
        methods = ['random', 'front-to-back', 'back-to-front', 'front WMA', 
                   'reverse WMA', 'optimal']
        bag_percentages = [0, 0.2, 0.4, 0.6, 0.8, 1]
        parameters = product(bag_percentages, methods)
        results = {}

        for (bag_percent, method) in parameters:
            aero = Boarding(self.rows, self.abreast, method, bag_percent, 
                            self.slow_average_fast)
            results[method + '_' + str(bag_percent)] = [aero.return_steps()
                                                        for _ in range(1000)]

        return results

    def create_df(self):
        """Return a Data Frame from the dictionary of results."""
        results = self.run_simulations()
        df = pd.DataFrame(results).melt()
        df['bag'] = [int(float(i.split('_', 1)[1])*100) for i in df['variable']]
        df['type'] = [i.split('_')[0] for i in df['variable']]

        order = ['front-to-back', 'back-to-front', 'front WMA',
                 'reverse WMA', 'random', 'optimal']
        df['type'] = pd.Categorical(df['type'], order)
        df = df.sort_values(['type', 'bag'], ascending=[True, False])
            
        return df

    def plot_results(self, filename):
        """Plot a boxplot summarising the results and save as a png
        file.
        """
        df = self.create_df()
        
        colours = ['#003f5c', '#444e86', '#955196', '#dd5182', '#ff6e54',
                   '#ffa600']
        
        fig = go.Figure()

        for percent, colour in zip(df['bag'].unique(), colours):
            fig.add_trace(
                go.Box(
                    x=list(df[df['bag'] == percent]['type']),
                    y=list(df[df['bag'] == percent]['value']),
                    marker=dict(color=colour),
                    name=str(percent),
                    hoverinfo='skip'
                )
            )
            
        fig.update_layout(
            boxmode='group', 
            title=("Distribution of Total Steps Taken to Board by Different "
                   "Boarding Methods<br><sub>For each boarding method, 1,000 "
                   "simulations were run with each passenger bag percentage."),
            legend=dict(
                title="% Passengers<br>with Bags",
                valign='middle'
            ),
            xaxis=dict(
                showline=True,
                linewidth=2,
                linecolor='rgb(100,100,100)'
            ),
            yaxis=dict(
                title="Number of Steps",
                showline=True,
                linewidth=2,
                linecolor='rgb(100,100,100)',
                gridwidth=1,
                gridcolor='rgba(100,100,100,0.2)'
            ),
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        

def main():
    """Initiate the Simulations class and run methods to create the
    boxplot.
    """
    rows = int(input("Number of rows: "))
    abreast= int(input("Seats per row: "))
    slow_average_fast = literal_eval(
        input("Proportions of slow, average, fast passengers: "))
    filename = input("Filename: ")
    
    aero = Simulations(rows, abreast, slow_average_fast)
    aero.plot_results(filename)


if __name__ == "__main__":
    main()