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

app = dash.Dash(__name__, static_folder='static')

app.layout = html.Div([
    
    html.Div(
        html.Img(src='/Users/kylebaranko/Final_Project/peaky_flask/peaky-finders/static/Logo-1.14.20-TW.png'), 
        className='banner'),

    html.Div(
        dcc.Graph(id="Load Curve",
                    figure=fig),
    )
])

# app.css.append_css({

#     "external_url: http://codepen.io/chriddyp/pen/bWLwgP.css"
# })

#if the file name assignmed is main, then we'll actually run our server 
if __name__ == '__main__':
    app.run_server(debug=True)
