import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

from peaky_finders.predictor import predict_all, ISO_LIST

# demo_list = ['nyiso', 'pjm', 'isone']
demo_list = ['nyiso']

load = predict_all(demo_list)


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Peak Load Forecasting App!"

"""Homepage"""
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    ])

index_page = html.Div([
        html.H1(children="Welcome to Peaky Finders"),
        dcc.Link(
            html.Button('HOME', id='home-button', className="mr-1"),
            href='/'),
        dcc.Link(
            html.Button('NYISO', id='nyiso-button', className="mr-1"),
            href='/nyiso'),
        dcc.Link(
            html.Button('PJM', id='pjm-button', className="mr-1"),
            href='/pjm'),
        dcc.Link(
            html.Button('ISONE', id='isone-button', className="mr-1"),
            href='/isone'),
    html.Br()
])

nyiso_layout = html.Div([
    html.Div(id='nyiso-content'),
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    html.H1('NYISO'),
    dcc.Dropdown(
        id='nyiso-dropdown',
        options=[
            {'label': 'Actual', 'value': 'Actual'},
            {'label': 'Predicted', 'value': 'Predicted'}
        ],
        value=['Actual', 'Predicted'],
        multi = True,
    ),
    dcc.Graph(id='nyiso-graph')
    # dcc.Graph(
    #     figure={
    #         "data": [
    #             {
    #                 "x": predictions['nyiso'].index,
    #                 "y": predictions['nyiso']['predicted_load'],
    #                 "type": "lines",
    #             },
    #         ],
    #         "layout": {"title": "Forecasted and Predicted Load for NYISO"},
    #     },
    # ),
    # dcc.Graph(
    #     figure={
    #         "data": [
    #             {
    #                 "x": actual['nyiso'].index,
    #                 "y": actual['nyiso']['load_MW'],
    #                 "type": "lines",
    #             },
    #         ],
    #         "layout": {"title": "Avocados Sold"},
    #     },
    # ),
    # # html.Br(),
    # dcc.Link('Go to Page 2', href='/nyiso'),
    # html.Br(),
    # dcc.Link('Go back to home', href='/'),
])
@app.callback(dash.dependencies.Output('nyiso-content', 'children'),
              [dash.dependencies.Input('nyiso-button', 'value')])



@app.callback(dash.dependencies.Output('nyiso-graph', 'figure'),
             [dash.dependencies.Input('nyiso-dropdown', 'value')])
def plot_nyiso_load_(value):
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load['nyiso'].index,
            y=load['nyiso']['load_MW'],
            name='Historical Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=load['nyiso'].index,
            y=load['nyiso']['predicted_load'],
            name = 'Forecasted Load',
            line=dict(color='aqua', width=3, dash='dash')))
    return fig

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/nyiso':
        return nyiso_layout
    else:
        return index_page




if __name__ == "__main__":
    app.run_server(debug=True)