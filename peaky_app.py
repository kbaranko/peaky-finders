import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from peaky_finders.predictor import predict_all, ISO_LIST, get_peak_data

# demo_list = ['nyiso', 'pjm', 'isone']
demo_list = ['PJM']

peak_data = get_peak_data(demo_list)
load, predictions = predict_all(demo_list)


TEMPLATE = 'plotly_white'

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

"""Homepage"""
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    ])

index_page = html.Div([
        html.H1(children="Welcome to Peaky Finders"),
        html.Div([
            html.H2(children="Select an ISO to get started."),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Link(
                            html.Button('HOME', id='home-button', block=True, color='azure'),
                            href='/')),
                    dbc.Col(
                        dcc.Link(
                            html.Button('NYISO', id='nyiso-button', className="mr-1", block=True, color='azure'),
                            href='/nyiso')),
                            
                    dbc.Col(
                        dcc.Link(
                            html.Button('PJM', id='pjm-button', className="mr-1", block=True, color='azure'),
                            href='/pjm')),
                    dbc.Col(
                        dcc.Link(
                            html.Button('ISONE', id='isone-button', className="mr-1", block=True, color='azure'),
                            href='/isone')),
                    dbc.Col(
                        dcc.Link(
                            html.Button('MISO', id='isone-button', className="mr-1", block=True, color='azure'),
                            href='/miso')),
                    dbc.Col(
                        dcc.Link(
                            html.Button('CAISO', id='isone-button', className="mr-1", block=True, color='azure'),
                            href='/caiso'))
                ]
            )
        ]
    )
])


"""NYISO LAYOUT"""

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
])
@app.callback(dash.dependencies.Output('nyiso-content', 'children'),
              [dash.dependencies.Input('nyiso-button', 'value')])


@app.callback(dash.dependencies.Output('nyiso-graph', 'figure'),
             [dash.dependencies.Input('nyiso-dropdown', 'value')])
def plot_nyiso_load_(value):
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load['NYISO'].index,
            y=load['NYISO'].values,
            name='Historical Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=predictions['NYISO'].index,
            y=predictions['NYISO'].values,
            name = 'Forecasted Load',
            line=dict(color='royalblue', width=3, dash='dash')))
    return fig


"""PJM LAYOUT"""

pjm_layout = html.Div([
    html.Div(id='pjm-content'),
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    html.H1('PJM'),
    dcc.Dropdown(
        id='pjm-dropdown',
        options=[
            {'label': 'Actual', 'value': 'Actual'},
            {'label': 'Predicted', 'value': 'Predicted'}
        ],
        value=['Actual', 'Predicted'],
        multi=True,
    ),
    dcc.Graph(id='pjm-graph'),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dcc.Graph(figure=px.histogram(
                        peak_data['PJM'].resample('D').max(),
                        x=peak_data['PJM'].resample('D').max()['load_MW'],
                        nbins=75,
                        marginal="rug",
                            ).add_vline(x=predictions['PJM'].values.max())
                    ),
                ]
            ), md=3),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='pjm-scatter-dropdown',
                        options=[
                            {'label': 'Day of Week', 'value': 'weekday'},
                            {'label': 'Season', 'value': 'season'}
                            ],
                        value='season',
                        multi=False,
                    ),
                    dcc.Graph(id='pjm-scatter')
                ]
            ), md=3),
        ]
    )
])
@app.callback(dash.dependencies.Output('pjm-content', 'children'),
              [dash.dependencies.Input('pjm-button', 'value')])

@app.callback(dash.dependencies.Output('pjm-graph', 'figure'),
             [dash.dependencies.Input('pjm-dropdown', 'value')])
def plot_pjm_load_(value):
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load['PJM'].index,
            y=load['PJM'].values,
            name='Historical Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=predictions['PJM'].index,
            y=predictions['PJM'].values,
            name = 'Forecasted Load',
            line=dict(color='royalblue', width=3, dash='dash')))
    return fig

@app.callback(dash.dependencies.Output("pjm-scatter", "figure"), 
    [dash.dependencies.Input("pjm-scatter-dropdown", "value")])
def update_scatter_plot(value):
    fig = px.scatter(
        peak_data['PJM'].resample('D').max(),
        x="load_MW",
        y="temperature", 
        color=value
    )
    return fig




# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/nyiso':
        return nyiso_layout
    elif pathname == '/pjm':
        return pjm_layout
    else:
        return index_page


if __name__ == "__main__":
    app.run_server(debug=False)