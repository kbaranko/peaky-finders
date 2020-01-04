import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from load_functions import * 

app = dash.Dash()

df = final_forecast(pd.datetime.today().strftime('%Y-%m-%d %H')) 

app.layout = html.Div([
    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': df.index,
                    'y': df['Predicted Load'],
                    'name': 'Load',
                    'mode': 'markers',
                    'marker': {'size': 12}
                },
            ],
            'layout': {
                'clickmode': 'event+select'
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
