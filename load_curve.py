import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_gif_component as Gif
from load_functions import * 
from assets import *



df = final_forecast(pd.datetime.today().strftime('%Y-%m-%d %H')) 

plot_forecast = go.Scatter(x=list(df.index),
                            y=list(df['Predicted Load']),
                            name="Projected",
                            line=dict(color="#e76aeb")
)

data = [plot_forecast]

layout = dict(title="Projected Load Curve", showlegend=True)

fig = dict(data=data, layout=layout)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1(id='title', children='Welcome to Peaky Finders'),
            ], className="six columns"),
        Gif.GifPlayer(gif='assets/giphy.gif', still='assets/giphy.gif'),
            ], className="six columns"),
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
                dcc.Graph(id='Load Curve',
                    figure=fig),
        ], className='six columns'), 
        html.Div([
            dcc.Graph(id='Load wave',
                    figure=fig),
        ], className='six columns'),
    ], className='row'),
    ])


#if the file name assignmed is main, then we'll actually run our server 
if __name__ == '__main__':
    app.run_server(debug=True)

    

# app.css.append_css({
#     "external_url": "http://codepen.io/chriddyp/pen/bWLwgP.css"
# })

