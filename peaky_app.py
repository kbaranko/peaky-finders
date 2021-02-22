import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

from peaky_finders.predictor import predict_all, ISO_LIST, get_peak_data


peak_data = get_peak_data(ISO_LIST)
load, predictions = predict_all(ISO_LIST)

NYISO_PEAK = round(
    stats.percentileofscore(
        peak_data['NYISO']['load_MW'],
        predictions['NYISO'].iloc[-24:].values.max()
    ), 2)

PJM_PEAK = round(
    stats.percentileofscore(
        peak_data['PJM']['load_MW'],
        predictions['PJM'].iloc[-24:].values.max()
    ), 2)

ISONE_PEAK = round(
    stats.percentileofscore(
        peak_data['ISONE']['load_MW'],
        predictions['ISONE'].iloc[-24:].values.max()
    ), 2)

MISO_PEAK = round(
    stats.percentileofscore(
        peak_data['MISO']['load_MW'],
        predictions['MISO'].iloc[-24:].values.max()
    ), 2)



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
            html.H4(children="Please select an ISO to get started."),
            html.Div(
                [
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
                    dcc.Link(
                        html.Button('MISO', id='isone-button', className="mr-1"),
                        href='/miso'),
                    dcc.Link(
                        html.Button('CAISO', id='isone-button', className="mr-1"),
                        href='/caiso')
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
        multi=True,
    ),
    dcc.Graph(id='nyiso-graph'),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            peak_data['NYISO'].resample('D').max(),
                            x=peak_data['NYISO'].resample('D').max()['load_MW'],
                            nbins=75,
                            marginal="rug",
                            title=f"Tomorrow's peak is in the {NYISO_PEAK} percentile of historical daily peaks."
                        ).add_vline(x=predictions['NYISO'].iloc[-24:].values.max()
                    ).update_layout(template=TEMPLATE, xaxis_title='Historical Peak Load (MW)')),
                ]
            ), width=6),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='nyiso-scatter-dropdown',
                        options=[
                            {'label': 'Day of Week', 'value': 'weekday'},
                            {'label': 'Season', 'value': 'season'}
                            ],
                        value='season',
                        multi=False,
                    ),
                    dcc.Graph(id='nyiso-scatter')
                ]
            ), width=6),
        ]
    )
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
    return fig.update_layout(
        title="System Load: Historical vs. Predicted",
        xaxis_title="Date",
        yaxis_title="Load (MW)",
        template=TEMPLATE
    )

@app.callback(dash.dependencies.Output("nyiso-scatter", "figure"), 
    [dash.dependencies.Input("nyiso-scatter-dropdown", "value")])
def nyiso_scatter_plot(value):
    fig = px.scatter(
        peak_data['NYISO'].resample('D').max(),
        x="load_MW",
        y="temperature", 
        color=value
    )
    return fig.update_layout(template=TEMPLATE, title='Peak Load vs. Temperature')


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
                    dcc.Graph(
                        figure=px.histogram(
                            peak_data['PJM'].resample('D').max(),
                            x=peak_data['PJM'].resample('D').max()['load_MW'],
                            nbins=75,
                            marginal="rug",
                            title=f"Tomorrow's peak is in the {PJM_PEAK} percentile of historical daily peaks."
                        ).add_vline(x=predictions['PJM'].iloc[-24:].values.max()
                    ).update_layout(template=TEMPLATE, xaxis_title='Historical Peak Load (MW)')),
                ]
            ), width=6),
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
            ), width=6),
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
    return fig.update_layout(
        title="System Load: Historical vs. Predicted",
        xaxis_title="Date",
        yaxis_title="Load (MW)",
        template=TEMPLATE
    )

@app.callback(dash.dependencies.Output("pjm-scatter", "figure"), 
    [dash.dependencies.Input("pjm-scatter-dropdown", "value")])
def pjm_scatter_plot(value):
    fig = px.scatter(
        peak_data['PJM'].resample('D').max(),
        x="load_MW",
        y="temperature", 
        color=value
    )
    return fig.update_layout(template=TEMPLATE, title='Peak Load vs. Temperature')


"""ISONE LAYOUT"""
isone_layout = html.Div([
    html.Div(id='isone-content'),
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    html.H1('ISONE'),
    dcc.Dropdown(
        id='isone-dropdown',
        options=[
            {'label': 'Actual', 'value': 'Actual'},
            {'label': 'Predicted', 'value': 'Predicted'}
        ],
        value=['Actual', 'Predicted'],
        multi=True,
    ),
    dcc.Graph(id='isone-graph'),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            peak_data['ISONE'].resample('D').max(),
                            x=peak_data['ISONE'].resample('D').max()['load_MW'],
                            nbins=75,
                            marginal="rug",
                            title=f"Tomorrow's peak is in the {ISONE_PEAK} percentile of historical daily peaks."
                        ).add_vline(x=predictions['ISONE'].iloc[-24:].values.max()
                    ).update_layout(template=TEMPLATE, xaxis_title='Historical Peak Load (MW)')),
                ]
            ), width=6),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='isone-scatter-dropdown',
                        options=[
                            {'label': 'Day of Week', 'value': 'weekday'},
                            {'label': 'Season', 'value': 'season'}
                            ],
                        value='season',
                        multi=False,
                    ),
                    dcc.Graph(id='isone-scatter')
                ]
            ), width=6),
        ]
    )
])
@app.callback(dash.dependencies.Output('isone-content', 'children'),
              [dash.dependencies.Input('isone-button', 'value')])

@app.callback(dash.dependencies.Output('isone-graph', 'figure'),
             [dash.dependencies.Input('isone-dropdown', 'value')])
def plot_isone_load_(value):
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load['ISONE'].index,
            y=load['ISONE'].values,
            name='Historical Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=predictions['ISONE'].index,
            y=predictions['ISONE'].values,
            name = 'Forecasted Load',
            line=dict(color='royalblue', width=3, dash='dash')))
    return fig.update_layout(
        title="System Load: Historical vs. Predicted",
        xaxis_title="Date",
        yaxis_title="Load (MW)",
        template=TEMPLATE
    )

@app.callback(dash.dependencies.Output("isone-scatter", "figure"), 
    [dash.dependencies.Input("isone-scatter-dropdown", "value")])
def isone_scatter_plot(value):
    fig = px.scatter(
        peak_data['ISONE'].resample('D').max(),
        x="load_MW",
        y="temperature", 
        color=value
    )
    return fig.update_layout(template=TEMPLATE, title='Peak Load vs. Temperature')

"""MISO LAYOUT"""
miso_layout = html.Div([
    html.Div(id='miso-content'),
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    html.H1('MISO'),
    dcc.Dropdown(
        id='miso-dropdown',
        options=[
            {'label': 'Actual', 'value': 'Actual'},
            {'label': 'Predicted', 'value': 'Predicted'}
        ],
        value=['Actual', 'Predicted'],
        multi=True,
    ),
    dcc.Graph(id='miso-graph'),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            peak_data['MISO'].resample('D').max(),
                            x=peak_data['MISO'].resample('D').max()['load_MW'],
                            nbins=75,
                            marginal="rug",
                            title=f"Tomorrow's peak is in the {MISO_PEAK} percentile of historical daily peaks."
                        ).add_vline(x=predictions['MISO'].iloc[-24:].values.max()
                    ).update_layout(template=TEMPLATE, xaxis_title='Historical Peak Load (MW)')),
                ]
            ), width=6),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='miso-scatter-dropdown',
                        options=[
                            {'label': 'Day of Week', 'value': 'weekday'},
                            {'label': 'Season', 'value': 'season'}
                            ],
                        value='season',
                        multi=False,
                    ),
                    dcc.Graph(id='miso-scatter')
                ]
            ), width=6),
        ]
    )
])
@app.callback(dash.dependencies.Output('miso-content', 'children'),
              [dash.dependencies.Input('miso-button', 'value')])

@app.callback(dash.dependencies.Output('miso-graph', 'figure'),
             [dash.dependencies.Input('miso-dropdown', 'value')])
def plotMISO_load_(value):
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load['MISO'].index,
            y=load['MISO'].values,
            name='Historical Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=predictions['MISO'].index,
            y=predictions['MISO'].values,
            name = 'Forecasted Load',
            line=dict(color='royalblue', width=3, dash='dash')))
    return fig.update_layout(
        title="System Load: Historical vs. Predicted",
        xaxis_title="Date",
        yaxis_title="Load (MW)",
        template=TEMPLATE
    )

@app.callback(dash.dependencies.Output("miso-scatter", "figure"), 
    [dash.dependencies.Input("miso-scatter-dropdown", "value")])
def miso_scatter_plot(value):
    fig = px.scatter(
        peak_data['MISO'].resample('D').max(),
        x="load_MW",
        y="temperature", 
        color=value
    )
    return fig.update_layout(template=TEMPLATE, title='Peak Load vs. Temperature')


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/nyiso':
        return nyiso_layout
    elif pathname == '/pjm':
        return pjm_layout
    elif pathname == '/isone':
        return isone_layout
    elif pathname == '/miso':
        return miso_layout
    else:
        return index_page


if __name__ == "__main__":
    app.run_server(debug=False)
