from itertools import product

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.formula.api import smf

class PlotSimulations:
    """Class with methods to read simulations data and produce charts to
    summarise the data.
    """
    def __init__(self, df):
        self.df = df
        self.category_order = [
            'front-to-back', 'back-to-front', 'WMA', 'front-to-back WMA',
            'back-to-front WMA', 'random', 'optimal'
        ]
        
    def plot_steps_by_method(self, filename: str):
        """Plot a boxplot summarising the mean number of steps taken 
        for different boarding methods with different passenger bag 
        percentages and save as a png file.
        """
        df = self.df.copy()
        df = df.sort_values('steps')
        
        colours = ['#003f5c', '#444e86', '#955196', '#dd5182', '#ff6e54', '#ffa600']
        bag_percentages = [1, .8, .6, .4, .2, 0]
        
        fig = go.Figure()

        for percent, colour in zip(bag_percentages, colours):
            fig.add_trace(
                go.Box(
                    x=list(df[df['bag_percent'] == percent]['method']),
                    y=list(df[df['bag_percent'] == percent]['steps']),
                    marker=dict(color=colour),
                    name=str(int(percent*100)),
                    hoverinfo='skip'
                )
            )
            
        fig.update_layout(
            boxmode='group', 
            title=("Distribution of Total Steps Taken to Board by Different "
                   "Boarding Methods<br><sub>For each boarding method, 1,000 "
                   "simulations were run with each passenger bag percentage."),
            legend=dict(
                title="% Passengers<br>with Bag",
                valign='middle',
            ),
            xaxis=dict(
                showline=True,
                linewidth=2,
                linecolor='rgb(100,100,100)',
                categoryarray=self.category_order,
            ),
            yaxis=dict(
                title="Number of Steps",
                showline=True,
                linewidth=2,
                linecolor='rgb(100,100,100)',
                gridwidth=1,
                gridcolor='rgba(100,100,100,0.2)',
            ),
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
    
    def plot_steps_by_no_aisles(self, filename: str):
        """Plot a bar chart summarising the mean number of steps taken 
        for different boarding methods with seatin configurations and 
        save as a png file.
        """
        df = self.df
        df = (
            df.groupby(['configuration', 'method'], as_index=False)
            .agg({'steps': ['mean', 'std']})
        )
        
        colours = ['rgba(0,63,92,{})', 'rgba(255,166,0,{})']
        
        fig = go.Figure()
        
        for config, colour in zip(df['configuration'].unique(), colours):
            fig.add_trace(
                go.Bar(
                    x=list(df[df['configuration'] == config]['method']),
                    y=list(df[df['configuration'] == config][('steps', 'mean')]),
                    marker=dict(
                        color=colour.format(0.7), 
                        line=dict(color=colour.format(1), width=2)
                    ),
                    name=str(config).replace('[', '').replace(']', ''),
                    error_y=dict(
                        array=list(df[df['configuration'] == config][('steps', 'std')])
                    )
                )
            )
            
        fig.update_layout(
            barmode='group', 
            bargroupgap=0.05,
            title=("Mean Steps to Board a Plane by Boarding Method<br><sub>"
                   "For each boarding method, 1,000 simulations were run for "
                   "each seating arrangement.<br>Error bars show the standard "
                   "deviation."), 
            legend=dict(title="Seating arrangement"),
            xaxis=dict(
                linewidth=2, 
                linecolor='rgb(80,80,80)',
                categoryarray=self.category_order,
            ),
            yaxis=dict(
                title="Mean Steps", 
                linewidth=2, 
                linecolor='rgb(80,80,80)', 
                gridwidth=1, 
                gridcolor='rgba(200,200,200,0.5)',
            ),
            margin=dict(t=140),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        
        
    def plot_steps_by_n_groups(self, filename: str):
        """Plot 4 boxplots summarising the mean number of steps taken 
        for different boarding methods with different numbers of groups 
        and passenger bag percentages and save as a png file.
        """
        df = self.df
        df = df.sort_values(['n_groups', 'bag_percent'])
        df['bag_percent']  = [int(n * 100) for n in df['bag_percent']]
        
        methods = ['front-to-back', 'back-to-front', 'front-to-back WMA', 'back-to-front WMA']
        coordinates = list(product(range(1,3), range(1,3)))
        subplot_titles = ['Front-to-back', 'Back-to-front', 'Front-to-back WMA', 'Back-to-front WMA']
        colours = ['#003f5c', '#955196', '#ff6e54']
        offsets = ['0%', '50%', '100%']
        showlegend_list = [True, False, False, False]

        fig = make_subplots(rows=2, cols=2, subplot_titles=subplot_titles)

        for method, coordinate, showlegend in zip(methods, coordinates, showlegend_list):
            plot = df[df['method'] == method].copy()
            for percent, colour, offset in zip(df['bag_percent'].unique(), colours, offsets):
                fig.add_trace(
                    go.Box(
                        x=list(plot[plot['bag_percent'] == percent]['n_groups']),
                        y=list(plot[plot['bag_percent'] == percent]['steps']),
                        marker=dict(color=colour),
                        name=str(percent),
                        hoverinfo='skip',
                        showlegend=showlegend,
                        offsetgroup=offset,
                    ), row=coordinate[0], col=coordinate[1],
                )

        xaxis = dict(
            title=dict(
                text="Groups",
                standoff=1
            ),
            linecolor='rgb(80,80,80)', 
            linewidth=2,
            type='category',
        )
        
        yaxis = dict(
            title=dict(
                text="Mean Steps", 
                standoff=1,
            ),
            linecolor='rgb(80,80,80)', 
            linewidth=2,
            gridwidth=1, 
            gridcolor='rgba(200,200,200,0.5)',
        )

        fig.update_layout(
            boxmode='group',
            title=("Distribution of Total Steps Taken to Board by Different "
                   "Boarding Methods and Number of Boarding Groups<br><sub>"
                   "For each boarding method and number of groups, 1,000 "
                   "simulations are run for each bag percentage."),
            plot_bgcolor='white',
            legend=dict(
                title="% Passengers<br>with Bag",
                traceorder='reversed',
            ),
            margin=dict(t=150),
            xaxis=xaxis,
            xaxis2=xaxis,
            xaxis3=xaxis,
            xaxis4=xaxis,
            yaxis=yaxis,
            yaxis2=yaxis,
            yaxis3=yaxis,
            yaxis4=yaxis,
        )
        
        fig.write_image(filename, height=700, width=1200, scale=2.5)
        
    def plot_regression_by_method(self, filename: str):
        """"""
        df = self.df
        df['bag_percent'] = df['bag_percent'] * 100
        colours = ['red', 'green', 'blue', 'orange', 'lightblue', 'pink', 'purple']

        fig = go.Figure()

        for count, (method, colour) in enumerate(zip(self.category_order, colours)):
            data = df[df['method'] == method].copy()
            results = smf.ols('steps ~ bag_percent', data).fit()
            r_2 = results.rsquared
            m = results.params[1]
            c = results.params[0]

            fig.add_trace(
                go.Scatter(
                    x=[0,100],
                    y=[c, 100*m+c],
                    line=dict(color=colour),
                    mode='lines',
                    name=method,
                    showlegend=False
                )
            )
            text_formula = "$s = {} p + {}$".format(round(m, 2), round(c,2))
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
            title=("Linear OLS Models to Predict the Effect of Changing the "
                   "Bag Percentage on the Number of Boarding Steps<br>for "
                   "Each Boarding Method"),
            plot_bgcolor='white', 
            xaxis=dict(
                title=(r"$\text{Percentage of Passengers with Hand Luggage } "
                       "(p)$"),
                linecolor='black',
                linewidth=2, 
                gridcolor='rgb(240,240,240)',
                gridwidth=1
            ),
            yaxis=dict(
                title=r"$\text{Boarding Steps } (s)$",
                linecolor='black',
                linewidth=2, 
                gridcolor='rgb(240,240,240)', 
                gridwidth=1
            ),
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)
        
    def plot_std_by_method(self, filename: str):
        """"""
        df = (
            self.df
            .groupby(['method', 'bag_percent'], as_index=False)['steps']
            .std()
        )
        df['bag_percent'] = df['bag_percent'] * 100

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
                    x=list(df[df['method'] == method]['bag_percent']),
                    y=list(df[df['method'] == method]['steps']),
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
            title=dict(
                text="Bag %", 
                standoff=0,
            ), 
            linecolor='black', 
            linewidth=2,
        )
        yaxis=dict(
            title=dict(
                text="σ of Steps", 
                standoff=0.
            ), 
            linecolor='black',
            linewidth=2,
            gridcolor='rgb(220,220,220)',
            gridwidth=1,
        )

        fig.update_layout(
            title=("Standard Deviations of Total Boarding Steps by Boarding "
                   "Method and Bag Percentage<br><sub>For each boarding "
                   "method, 1,000 simulations are run with each passenger bag "
                   "percentage."),
            height=600,
            margin=dict(t=140),
            plot_bgcolor='white',
            xaxis=xaxis, 
            xaxis2=xaxis, 
            xaxis3=xaxis,
            xaxis4=xaxis, 
            xaxis5=xaxis,
            xaxis6=xaxis,
            xaxis7=xaxis,
            yaxis=yaxis,
            yaxis2=yaxis,
            yaxis3=yaxis,
            yaxis4=yaxis,
            yaxis5=yaxis,
            yaxis6=yaxis,
            yaxis7=yaxis,
        )
        
        fig.write_image(filename, height=500, width=1200, scale=2.5)