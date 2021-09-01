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
from plotly.subplots import make_subplots

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
        self.methods = ['random', 'front-to-back', 'back-to-front', 'WMA', 
                        'front WMA', 'reverse WMA', 'optimal']

    def steps_by_method(self):
        """Return a dictionary where the key identifies the method and bag 
        percentage, and the value is a list of the results from the 1,000
        simulations.
        """
        bag_percentages = [0, 0.2, 0.4, 0.6, 0.8, 1]
        parameters = product(bag_percentages, self.methods)
        results = {}

        for (bag_percent, method) in parameters:
            aero = Boarding(self.rows, self.abreast, method, bag_percent, 
                            self.slow_average_fast, self.rows)
            results[method + '_' + str(bag_percent)] = [aero.return_steps()
                                                        for _ in range(100)]

        return results
    
    def steps_by_no_aisles(self):
        """"""
        configurations = [[3,3], [2,2,2]]
        d = {k:{} for k in self.methods}
        for method in self.methods:
            for config in configurations:
                aero = Boarding(self.rows, config, method, 0.5, [.3, .4, .3], self.rows) 
                d[method][str(config)] = [aero.return_steps() for _ in range(100)]
        return d
    
    def steps_by_group_size(self):
        """"""
        n_groups = [1, 3, 6, 9, 12, 15]
        methods = ['front-to-back', 'back-to-front', 'front WMA', 
                   'reverse WMA']
        d = {}
        for method in methods:
            for g in n_groups:
                aero = Boarding(15, [3,3], method, 0.5, [.3,.4,.4], g)
                d[str(g)+'_'+method] = [aero.return_steps() for _ in range(100)]
        df = pd.DataFrame(d).melt()
        df['method'] = [i.split('_')[1] for i in df['variable']]
        df['variable'] = [i.split('_')[0] for i in df['variable']]
        return df

    def create_df_by_method(self):
        """Return a Data Frame from the dictionary of results."""
        results = self.steps_by_method()
        df = pd.DataFrame(results).melt()
        df['bag'] = [int(float(i.split('_', 1)[1])*100) for i in df['variable']]
        df['type'] = [i.split('_')[0] for i in df['variable']]

        order = ['front-to-back', 'back-to-front', 'WMA', 'front WMA',
                 'reverse WMA', 'random', 'optimal']
        df['type'] = pd.Categorical(df['type'], order)
        df = df.sort_values(['type', 'bag'], ascending=[True, False])
            
        return df
    
    def create_df_by_no_aisles(self):
        """"""
        a = self.steps_by_no_aisles()
        df = pd.DataFrame()
        for method in a:
            for arrangement in a[method]:
                for result in a[method][arrangement]:
                    df = df.append({'method': method, 
                                    'seating': str(arrangement), 
                                    'results': result}, 
                                   ignore_index=True)
        
        return df

    def plot_steps_by_method(self, filename):
        """Plot a boxplot summarising the results and save as a png
        file.
        """
        df = self.create_df_by_method()
        
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
    
    def plot_steps_by_no_aisles(self, filename):
        """"""
        df = self.create_df_by_no_aisles()
        df = (df.groupby(['seating', 'method'], as_index=False)
              .agg({'results': ['mean', 'std']})
             )
        
        colours = ['#ff6e54', '#ffa600']
        
        fig = go.Figure()
        
        for arrangement, colour in zip(df['seating'].unique(), colours):
            fig.add_trace(
                go.Bar(
                    x=list(df[df['seating'] == arrangement]['method']),
                    y=list(df[df['seating'] == arrangement][('results', 'mean')]),
                    marker=dict(color=colour),
                    name=str(arrangement).replace('[', '').replace(']', ''),
                    error_y=dict(
                        array=list(df[df['seating'] == arrangement][('results', 'std')])
                    )
                )
            )
            
        fig.update_layout(
            barmode='group', 
            title='Mean Steps to Board a Plane in 1,000 Simulations', 
            legend=dict(title="<b>Seating arrangement</b>"),
            xaxis=dict(
                title="Boarding Method", 
                linewidth=2, 
                linecolor='rgb(80,80,80)',
            ),
            yaxis=dict(
                title="Mean Steps", 
                linewidth=2, 
                linecolor='rgb(80,80,80)', 
                gridwidth=1, 
                gridcolor='rgba(200,200,200,0.5)'
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        
        
    def plot_steps_by_group_size(self, filename):
        """"""
        df = self.steps_by_group_size()
        methods = ['front-to-back', 'back-to-front', 'front WMA',
                   'reverse WMA']
        coordinates = list(product(range(1,3), range(1,3)))
        subplot_titles = ['Front-to-back', 'Back-to-front', 'Front WMA', 
                          'Reverse WMA']
        colours = ['#003f5c', '#444e86', '#955196', '#dd5182']
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=subplot_titles)
        for method, colour, coordinate in zip(methods, colours, coordinates):
            fig.add_trace(
                go.Box(
                    x=list(df[df['method'] == method]['variable']),
                    y=list(df[df['method'] == method]['value']),
                    marker=dict(color=colour),
                    showlegend=False,
                ), row=coordinate[0], col=coordinate[1],
            )


        fig.update_layout(
            title="Mean Boarding Steps for Boarding Methods by Boarding Group Size",
            plot_bgcolor='white',
            xaxis=dict(
                title=dict(text="Groups", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2
            ),
            xaxis2=dict(
                title=dict(text="Groups", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2
            ),
            xaxis3=dict(
                title=dict(text="Groups", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2
            ),
            xaxis4=dict(
                title=dict(text="Groups", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2
            ),
            yaxis=dict(
                title=dict(text="Mean Steps", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2,
                gridwidth=1, 
                gridcolor='rgba(200,200,200,0.5)',
            ),
            yaxis2=dict(
                title=dict(text="Mean Steps", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2,
                gridwidth=1, 
                gridcolor='rgba(200,200,200,0.5)',
            ),
            yaxis3=dict(
                title=dict(text="Mean Steps", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2,
                gridwidth=1, 
                gridcolor='rgba(200,200,200,0.5)',
            ),
            yaxis4=dict(
                title=dict(text="Mean Steps", standoff=1),
                linecolor='rgb(80,80,80)', 
                linewidth=2,
                gridwidth=1, 
                gridcolor='rgba(200,200,200,0.5)',
            )
        )
        fig.write_image(filename, height=500, width=1200, scale=2.5)

        
def main():
    """Initiate the Simulations class and run methods to create the
    boxplot.
    """
    output = input("Choose one of: 'by method', 'by aisles', 'by group size'")
    
    rows = int(input("Number of rows: "))
    abreast= literal_eval(input("Seats per row: "))
    slow_average_fast = literal_eval(
        input("Proportions of slow, average, fast passengers: "))
    filename = input("Filename: ")
    
    aero = Simulations(rows, abreast, slow_average_fast)
    if output == 'by method':
        aero.plot_steps_by_method(filename)
    elif output == 'by aisles':
        aero.plot_steps_by_no_aisles(filename)
    elif output == 'by group size':
        aero.plot_steps_by_group_size(filename)
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()