from itertools import product
from re import template

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.formula.api as smf


class SimulationPlots:
    """Class with methods to read simulations data and produce charts to
    summarise the data.
    """
    def __init__(self):
        self._create_graph_template()
        self.df_methods = pd.read_csv('data2/by_method_data_additional.csv')
        self.df_aisles = pd.read_csv('data2/by_aisles_data_additional.csv')
        self.df_groups = pd.read_csv('data2/by_groups_data_additional.csv')
        self.category_order = [
            'front-to-back', 'back-to-front', 'WMA', 'front-to-back WMA',
            'back-to-front WMA', 'random', 'optimal'
        ]

    def _create_graph_template(self):
        self.template=dict(
            layout=go.Layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                title=dict(
                    x=0,
                    xref='paper',
                    y=0.92,
                    yref='container',
                    yanchor='top',
                ),
                xaxis=dict(
                    showline=True,
                    linewidth=2,
                    linecolor='rgb(80,80,80)',
                ),
                yaxis=dict(
                    showline=True,
                    linecolor='rgb(80,80,80)',
                    linewidth=2,
                    gridcolor='rgba(200,200,200,0.5)',
                    gridwidth=1,
                )
            )
        )
        
    def plot_steps_by_method(self, filename: str):
        """Plot a boxplot summarising the mean number of steps taken 
        for different boarding methods with different passenger bag 
        percentages and save as a png file.
        """
        n_simulations = self.df_methods.groupby(['boarding_method', 'bag_percent']).size().reset_index(name='size')['size'].iloc[0]
        df = self.df_methods.sort_values('steps')
        
        colours = ['#003f5c', '#444e86', '#955196', '#dd5182', '#ff6e54', '#ffa600']
        bag_percentages = [1, .8, .6, .4, .2, 0]
        
        fig = go.Figure()

        for percent, colour in zip(bag_percentages, colours):
            fig.add_trace(
                go.Box(
                    x=list(df.loc[df.bag_percent == percent, 'boarding_method']),
                    y=list(df.loc[df.bag_percent == percent, 'steps']),
                    marker=dict(color=colour),
                    name=str(int(percent*100)),
                    hoverinfo='skip'
                )
            )
            
        fig.update_layout(
            template=self.template,
            boxmode='group', 
            title=("Distribution of Total Steps Taken to Board by Different "
                   f"Boarding Methods<br><sub>For each boarding method, {n_simulations:,d} "
                   "simulations were run with each passenger bag percentage."),
            legend=dict(
                title="% Passengers<br>with Bag",
                valign='middle',
            ),
            xaxis_categoryarray=self.category_order,
            yaxis_title="Number of Steps",
            height=600,
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        print(f"Graph {filename} saved.")
    
    def plot_steps_by_aisles(self, filename: str):
        """Plot a bar chart summarising the mean number of steps taken 
        for different boarding methods with seatin configurations and 
        save as a png file.
        """
        n_simulations = self.df_aisles.groupby(['configuration', 'boarding_method']).size().reset_index(name='size')['size'].iloc[0]
        df = self.df_aisles
        df = (
            df.groupby(['configuration', 'boarding_method'], as_index=False)
            .agg({'steps': ['mean', 'std']})
        )
        
        colours = ['rgba(0,63,92,{})', 'rgba(255,166,0,{})']
        
        fig = go.Figure()
        
        for config, colour in zip(df.configuration.unique(), colours):
            fig.add_trace(
                go.Bar(
                    x=list(df.loc[df.configuration == config, 'boarding_method']),
                    y=list(df.loc[df.configuration == config, ('steps', 'mean')]),
                    marker=dict(
                        color=colour.format(0.7), 
                        line=dict(color=colour.format(1), width=2)
                    ),
                    name=str(config).replace('[', '').replace(']', ''),
                    error_y=dict(
                        array=list(df.loc[df.configuration == config, ('steps', 'std')]),
                    )
                )
            )
            
        fig.update_layout(
            template=self.template,
            barmode='group', 
            bargroupgap=0.05,
            title=("Mean Steps to Board a Plane by Boarding Method<br><sub>"
                   f"For each boarding method, {n_simulations:,d} simulations "
                   "were run for each seating arrangement.<br>Error bars show "
                   "the standard deviation."), 
            legend=dict(title="Seating arrangement"),
            xaxis_categoryarray=self.category_order,
            yaxis_title="Mean Steps",
            margin=dict(t=120),
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        print(f"Graph {filename} saved.")
        
        
    def plot_steps_by_groups(self, filename: str):
        """Plot 4 boxplots summarising the mean number of steps taken 
        for different boarding methods with different numbers of groups 
        and passenger bag percentages and save as a png file.
        """
        n_simulations = self.df_groups.groupby(['n_groups', 'bag_percent']).size().reset_index(name='size')['size'].iloc[0]
        df = self.df_groups
        df = df.sort_values(['n_groups', 'bag_percent'])
        df['bag_percent']  = [int(n * 100) for n in df['bag_percent']]
        
        methods = ['front-to-back', 'back-to-front', 'front-to-back WMA', 'back-to-front WMA']
        coordinates = list(product(range(1,3), range(1,3)))
        subplot_titles = ['Front-to-back', 'Back-to-front', 'Front-to-back WMA', 'Back-to-front WMA']
        colours = ['#003f5c', 'rgb(20,20,20)', '#955196', 'rgb(20,20,20)', '#ff6e54']
        offsets = ['0%', '33%', '50%', '66%', '100%']
        showlegend_list = [True, False, False, False]

        fig = make_subplots(rows=2, cols=2, subplot_titles=subplot_titles)

        for method, coordinate, showlegend in zip(methods, coordinates, showlegend_list):
            plot = df[df['boarding_method'] == method].copy()
            for percent, colour, offset in zip(df['bag_percent'].unique(), colours, offsets):
                fig.add_trace(
                    go.Box(
                        x=list(plot.loc[plot.bag_percent == percent, 'n_groups']),
                        y=list(plot.loc[plot.bag_percent == percent, 'steps']),
                        marker=dict(color=colour),
                        name=f"{percent}%",
                        hoverinfo='skip',
                        showlegend=showlegend,
                        offsetgroup=offset,
                    ), row=coordinate[0], col=coordinate[1],
                )

        
        xaxis = dict(
            title=dict(text="Groups", standoff=1),
            linecolor='rgb(80,80,80)', 
            linewidth=2,
            type='category',
        )
        
        yaxis = dict(
            title=dict(text="Mean Steps", standoff=1),
            linecolor='rgb(80,80,80)', 
            linewidth=2,
            gridwidth=1, 
            gridcolor='rgba(200,200,200,0.5)',
        )

        fig.update_layout(
            boxmode='group',
            title=("Distribution of Total Steps Taken to Board by Different "
                   "Boarding Methods and Number of Boarding Groups<br><sub>"
                   f"For each boarding method and number of groups, {n_simulations:,d} "
                   "simulations are run for each bag percentage."),
            plot_bgcolor='white',
            legend=dict(title="% Passengers<br>with Bag", traceorder='reversed'),
            margin=dict(t=150),
            xaxis=xaxis, xaxis2=xaxis, xaxis3=xaxis, xaxis4=xaxis,
            yaxis=yaxis, yaxis2=yaxis, yaxis3=yaxis, yaxis4=yaxis,
        )
        
        fig.write_image(filename, height=700, width=1200, scale=2.5)
        print(f"Graph {filename} saved.")
        
    def plot_regression_by_method(self, filename: str):
        """"""
        df = self.df_methods
        df['bag_percent'] = df['bag_percent'] * 100
        colours = ['red', 'green', 'blue', 'orange', 'lightblue', 'pink', 'purple']

        fig = go.Figure()

        for count, (method, colour) in enumerate(zip(self.category_order, colours)):
            data = df[df['boarding_method'] == method].copy()
            results = smf.ols('steps ~ bag_percent', data).fit()
            r_2 = results.rsquared
            m = results.params[1]
            c = results.params[0]

            fig.add_trace(
                go.Scatter(
                    x=[0, 100],
                    y=[c, 100 * m + c],
                    line=dict(color=colour),
                    mode='lines',
                    name=method,
                    showlegend=False
                )
            )
            text_formula = "$s = {} p + {}$".format(round(m, 2), round(c, 2))
            text_r2 = "$R^2 = {}$".format(round(r_2, 2))
            
            # Add a line, similar to a legend, and then add the method 
            # name, formula for the OLS line and the R-squared value.
            fig.add_shape(
                type='line', 
                x0=2, 
                x1=5,
                y0=320 - count * 14, 
                y1=320 - count * 14, 
                line=dict(color=colour)
            )
            fig.add_annotation(
                text=method, 
                x=6, 
                y=320 - count * 14, 
                showarrow=False,
                xanchor='left'
            )
            fig.add_annotation(
                text=text_formula,
                x=18,
                y=320 - count * 14, 
                showarrow=False,
                xanchor='left'
            )
            fig.add_annotation(
                text=text_r2, 
                x=29,
                y=320 - count * 14,
                showarrow=False, 
                xanchor='left'
            )

        fig.update_layout(
            template=self.template,
            title=("Linear OLS Models to Predict the Effect of Changing the "
                   "Bag Percentage on the Number of Boarding Steps<br>for "
                   "Each Boarding Method"),
            xaxis_title=r"$\text{Percentage of Passengers with Hand Luggage } (p)$",
            xaxis_gridcolor='rgb(240,240,240)',
            xaxis_gridwidth=1,
            yaxis_title=r"$\text{Boarding Steps } (s)$",
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        print(f"Graph {filename} saved.")
        
    def plot_std_by_method(self, filename: str):
        """"""
        n_simulations = self.df_methods.groupby(['boarding_method', 'bag_percent']).size().reset_index(name='size')['size'].iloc[0]
        df = (
            self.df_methods
            .groupby(['boarding_method', 'bag_percent'], as_index=False)['steps']
            .std()
        )

        methods = [
            'front-to-back', 
            'back-to-front', 
            'front-to-back WMA', 
            'back-to-front WMA', 
            'WMA',
            'random',
            'optimal',
        ]
        subplot_titles = [method[0].upper() + method[1:] for method in methods]
        colours = ['#003f5c', '#374c80', '#7a5195', '#bc5090', '#ef5675', '#ff764a', '#ffa600']

        fig = make_subplots(
            rows=2,
            cols=4,
            subplot_titles=subplot_titles,
            shared_yaxes=True,
        )
        for count, (method, colour) in enumerate(zip(methods, colours)):
            fig.add_trace(
                go.Bar(
                    x=list(df.loc[df.boarding_method == method, 'bag_percent']),
                    y=list(df.loc[df.boarding_method == method, 'steps']),
                    marker=dict(
                        color=colour, 
                        opacity=0.8, 
                        line=dict(
                            color='black',
                            width=2,
                        )
                    ),
                    showlegend=False,
                ), 
                row=count // 4 + 1,
                col=count % 4 + 1,
            )

        xaxis=dict(
            title=dict(text="Bag %", standoff=0), 
            linecolor='black', 
            linewidth=2,
        )
        yaxis=dict(
            title=dict(text="σ of Steps", standoff=0), 
            linecolor='black',
            linewidth=2,
            gridcolor='rgb(220,220,220)',
            gridwidth=1,
        )

        fig.update_layout(
            title=("Standard Deviations of Total Boarding Steps by Boarding "
                   "Method and Bag Percentage<br><sub>For each boarding "
                   f"method, {n_simulations:,d} simulations are run with "
                   "each passenger bag percentage."),
            height=600,
            margin=dict(t=140),
            plot_bgcolor='white',
            xaxis=xaxis, xaxis2=xaxis, xaxis3=xaxis, xaxis4=xaxis, 
            xaxis5=xaxis, xaxis6=xaxis, xaxis7=xaxis,
            yaxis=yaxis, yaxis2=yaxis, yaxis3=yaxis, yaxis4=yaxis,
            yaxis5=yaxis, yaxis6=yaxis, yaxis7=yaxis,
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        print(f"Graph {filename} saved.")