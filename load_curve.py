import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from load_functions import * 



df = final_forecast(pd.datetime.today().strftime('%Y-%m-%d %H')) 

plot_forecast = go.Scatter(x=list(df.index),
                            y=list(df['Predicted Load']),
                            name="Projected Load Curve",
                            line=dict(color="#e76aeb")
)

data = [plot_forecast]

layout = dict(title="Projected Load Curve", showlegend=True)

fig = dict(data=data, layout=layout)

app = dash.Dash()

app.layout = html.Div([
    html.Label('NYISO Forecasts'),
    html.Div(
        dcc.Graph(id="Load Curve",
                    figure=fig)
    ),
    html.Label('Historical Data'),
    html.Div( 
        dcc.Input(
            id='historical data',
            placeholder='Enter a date range',
            type='text',
            value=''
        )
    ),
    html.Div(
        dcc.Dropdown(
            options=[
                {'label': 'Candelstick', 'value':'Candelstick'},
                {'label': 'Line', 'value':'Line'}
            ]
        )
    )
])

#if the file name assignmed is main, then we'll actually run our server 
if __name__ == '__main__':
    app.run_server(debug=True)
