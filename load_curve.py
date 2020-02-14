#Import dash, pandas, plotly, static images, and load forecasting functions
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_gif_component as Gif
from peaky_packages.functions.load_functions import previous_7days_load
from peaky_packages.functions.forecast_functions import final_forecast
from peaky_packages.functions.log_functions import return_values
from assets import *



DF = final_forecast(pd.datetime.today().strftime('%Y-%m-%d %H'))
DF_LOAD = previous_7days_load()
ANSWER = return_values(pd.datetime.today().strftime('%Y-%m-%d %H'))

PLOT_FORECAST = go.Scatter(x=list(DF.index),
                           y=list(DF['Predicted Load']),
                           name="Projected",
                           line=dict(color="#e76aeb", width=4, dash='dot')
                           )

PLOT_HISTORICAL = go.Scatter(x=list(DF_LOAD.index),
                             y=list(DF_LOAD['load_MW']),
                             name="Historical",
                             line=dict(color="#43d9de")
                             )

DATA = [PLOT_FORECAST]
DATA_1 = [PLOT_HISTORICAL]

layout = dict(title="Projected Load Curve", showlegend=True)
layout_1 = dict(title="7-Day Historical Load Curve", showlegend=True)

fig = dict(data=DATA, layout=layout)
fig_1 = dict(data=DATA_1, layout=layout_1)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1(id='title', children='Welcome to Peaky Finders'),
        ], className="six columns"),
        html.Div([
            Gif.GifPlayer(gif='assets/giphy.gif', still='assets/giphy.gif'),
        ], className="six columns"),
        ], className='row'),
    html.Div([
        html.H5(id='drop-down-title', children='Select your ISO'),
        html.Div(
            dcc.Dropdown(
                options=[
                    {'label': 'NYISO', 'value': 'NYISO'},
                    {'label': 'PJM', 'value': 'PJM'},
                    {'label': 'CAISO', 'value': 'CAISO'},
                    ],
                id='select-iso'),
        ),
        ]),
    html.Div([
        html.Div([
            dcc.Graph(id='Historical Load Curve',
                      figure=fig_1),
        ],
                 className='six columns'),
        html.Div([
            dcc.Graph(id='Projected Load Curve',
                      figure=fig),
        ], className='six columns'),
    ], className='row'),
    html.Div([
        html.H5(id='confidence_interval_header', children='Tomorrow\'s Peak Day Forecast:'),
        html.H6(id='confidence_interval', children=ANSWER)
        ]),
    ])


#if the file name assignmed is main, then we'll actually run our server
if __name__ == '__main__':
    app.run_server(debug=True)
 