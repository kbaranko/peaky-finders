import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

from peaky_finders.predictor import predict_all, ISO_LIST, get_peak_data, get_iso_map

iso_map = get_iso_map()
peak_data = get_peak_data(ISO_LIST)
load, predictions = predict_all(ISO_LIST)

PEAKS_24HR = {
    'NYISO': round(
        stats.percentileofscore(
            peak_data['NYISO']['load_MW'],
            predictions['NYISO'].iloc[-24:].values.max()
        ), 2),
    'PJM': round(
        stats.percentileofscore(
            peak_data['PJM']['load_MW'],
            predictions['PJM'].iloc[-24:].values.max()
        ), 2),
    'ISONE': round(
        stats.percentileofscore(
            peak_data['ISONE']['load_MW'],
            predictions['ISONE'].iloc[-24:].values.max()
        ), 2),
    'MISO': round(
        stats.percentileofscore(
            peak_data['MISO']['load_MW'],
            predictions['MISO'].iloc[-24:].values.max()
        ), 2),
    'CAISO': round(
        stats.percentileofscore(
            peak_data['CAISO']['load_MW'],
            predictions['CAISO'].iloc[-24:].values.max()
        ), 2),
}

NYISO_PEAK = PEAKS_24HR['NYISO']
PJM_PEAK = PEAKS_24HR['PJM']
ISONE_PEAK = PEAKS_24HR['ISONE']
MISO_PEAK = PEAKS_24HR['MISO']
CAISO_PEAK = PEAKS_24HR['CAISO']

iso_map['Forecasted Peak Percentile'] = iso_map['iso'].map(PEAKS_24HR)


TEMPLATE = 'plotly_white'

app = dash.Dash(
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True
)
server = app.server

"""Homepage"""
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    ])

index_page = html.Div([
        html.H1(children="Welcome to Peaky Finders"),
        html.Br(),
        html.Br(),
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
                        html.Button('MISO', id='miso-button', className="mr-1"),
                        href='/miso'),
                    dcc.Link(
                        html.Button('CAISO', id='caiso-button', className="mr-1"),
                        href='/caiso')
                ]
            )]),
        html.Div([
            dcc.Graph(figure=px.choropleth(
                        iso_map,
                        geojson=iso_map.geometry,
                        locations=iso_map.index,
                        color="Forecasted Peak Percentile",
                        projection="mercator",
                        color_continuous_scale = 'Reds',
                        ).update_geos(
                            fitbounds="locations",
                            visible=False).update_layout(
                                height=600,
                                margin={"r":0,"t":0,"l":0,"b":0}
                            )
                        ) 
        ], style = {'display': 'inline-block', 'width': '90%'})
])


"""NYISO LAYOUT"""
nyiso_layout = html.Div([
    html.Div(id='nyiso-content'),
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    html.Br(),
    html.Br(),
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
                            title=f"Tomorrow's peak is in the {NYISO_PEAK} percentile of historical daily peaks.",
                            color_discrete_sequence=['darkturquoise'] 
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
            line=dict(color='darkturquoise', width=3, dash='dash')))
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
    html.Br(),
    html.Br(),
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
                            title=f"Tomorrow's peak is in the {PJM_PEAK} percentile of historical daily peaks.",
                            color_discrete_sequence=['darkturquoise']
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
            line=dict(color='darkturquoise', width=3, dash='dash')))
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
    html.Br(),
    html.Br(),
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
                            title=f"Tomorrow's peak is in the {ISONE_PEAK} percentile of historical daily peaks.",
                            color_discrete_sequence=['darkturquoise']
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
            line=dict(color='darkturquoise', width=3, dash='dash')))
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
    html.Br(),
    html.Br(),
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
                            title=f"Tomorrow's peak is in the {MISO_PEAK} percentile of historical daily peaks.",
                            color_discrete_sequence=['darkturquoise']
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
            line=dict(color='darkturquoise', width=3, dash='dash')))
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


"""CAISO LAYOUT"""
caiso_layout = html.Div([
    html.Div(id='caiso-content'),
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    html.Br(),
    html.Br(),
    html.H1('CAISO'),
    dcc.Dropdown(
        id='caiso-dropdown',
        options=[
            {'label': 'Actual', 'value': 'Actual'},
            {'label': 'Predicted', 'value': 'Predicted'}
        ],
        value=['Actual', 'Predicted'],
        multi=True,
    ),
    dcc.Graph(id='caiso-graph'),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            peak_data['CAISO'].resample('D').max(),
                            x=peak_data['CAISO'].resample('D').max()['load_MW'],
                            nbins=75,
                            marginal="rug",
                            title=f"Tomorrow's peak is in the {CAISO_PEAK} percentile of historical daily peaks.",
                            color_discrete_sequence=['darkturquoise']
                        ).add_vline(x=predictions['CAISO'].iloc[-24:].values.max()
                    ).update_layout(template=TEMPLATE, xaxis_title='Historical Peak Load (MW)')),
                ]
            ), width=6),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='caiso-scatter-dropdown',
                        options=[
                            {'label': 'Day of Week', 'value': 'weekday'},
                            {'label': 'Season', 'value': 'season'}
                            ],
                        value='season',
                        multi=False,
                    ),
                    dcc.Graph(id='caiso-scatter')
                ]
            ), width=6),
        ]
    )
])
@app.callback(dash.dependencies.Output('caiso-content', 'children'),
              [dash.dependencies.Input('caiso-button', 'value')])

@app.callback(dash.dependencies.Output('caiso-graph', 'figure'),
             [dash.dependencies.Input('caiso-dropdown', 'value')])
def plotCAISO_load_(value):
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load['CAISO'].index,
            y=load['CAISO'].values,
            name='Historical Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=predictions['CAISO'].index,
            y=predictions['CAISO'].values,
            name = 'Forecasted Load',
            line=dict(color='darkturquoise', width=3, dash='dash')))
    return fig.update_layout(
        title="System Load: Historical vs. Predicted",
        xaxis_title="Date",
        yaxis_title="Load (MW)",
        template=TEMPLATE
    )

@app.callback(dash.dependencies.Output("caiso-scatter", "figure"), 
    [dash.dependencies.Input("caiso-scatter-dropdown", "value")])
def caiso_scatter_plot(value):
    fig = px.scatter(
        peak_data['CAISO'].resample('D').max().dropna(),
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
    elif pathname == '/caiso':
        return caiso_layout
    else:
        return index_page


if __name__ == "__main__":
    app.run_server(debug=False)
