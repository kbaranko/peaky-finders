import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_gif_component as Gif
from load_functions import * 
from forecast_functions import *
from assets import *



df = final_forecast(pd.datetime.today().strftime('%Y-%m-%d %H')) 
df_load = previous_7days_load()

plot_forecast = go.Scatter(x=list(df.index),
                            y=list(df['Predicted Load']),
                            name="Projected",
                            line=dict(color="#e76aeb", width=4, dash='dot')
)

plot_historical = go.Scatter(x=list(df_load.index),
                            y=list(df_load['load_MW']),
                            name="Historical",
                            line=dict(color="#43d9de")
)

data = [plot_forecast]
data_1 = [plot_historical]

layout = dict(title="Projected Load Curve", showlegend=True)
layout_1 = dict(title="7-Day Historical Load Curve", showlegend=True)

fig = dict(data=data, layout=layout)
fig_1 = dict(data=data_1, layout=layout_1)

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
        ], className='six columns'), 
        html.Div([
            dcc.Graph(id='Projected Load Curve',
                    figure=fig),
        ], className='six columns'),
    ], className='row'),
    ])


#if the file name assignmed is main, then we'll actually run our server 
if __name__ == '__main__':
    app.run_server(debug=True)

    