import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go


TEMPLATE = 'plotly_white'

BUTTON_LAYOUT = [
    dcc.Link(
        html.Button('HOME', id='home-button', className="mr-1"),
        href='/'),
    dcc.Link(
        html.Button('CAISO', id='caiso-button', className="mr-1"),
        href='/caiso'),
    dcc.Link(
        html.Button('MISO', id='miso-button', className="mr-1"),
        href='/miso'),
    dcc.Link(
        html.Button('PJM', id='pjm-button', className="mr-1"),
        href='/pjm'),
    dcc.Link(
        html.Button('NYISO', id='nyiso-button', className="mr-1"),
        href='/nyiso'),
    dcc.Link(
        html.Button('ISONE', id='isone-button', className="mr-1"),
        href='/isone'),
]


def set_iso_layout(
    iso: str,
    full_name: str,
    description: str,
    month: str,
    mae: float,
    model_description: str,
    peak_data: dict,
    load_duration_curves: dict
):
    layout = html.Div([
        html.Div(id=f'{iso}-content'),
        html.Br(),
        dbc.Row([
            dbc.Col(
                html.Div(BUTTON_LAYOUT), width=4),
            dbc.Col(width=7),
        ], justify='center'),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H1(full_name), width=9),
            dbc.Col(width=2),
        ], justify='center'),
        dbc.Row([
            dbc.Col(
            html.Div(children=description), width=9),
            dbc.Col(width=2)
        ], justify='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(
                html.H3('Model Performance'), width=9
            ),
            dbc.Col(width=2),
        ], justify='center'),
        dbc.Row([
            dbc.Col(
                html.Div(
                    children=f'Mean Absolute Error (MAE) for {month}, 2021: {mae}'
                ), width=9
            ),
            dbc.Col(width=2),
        ], justify='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(
                    dcc.Dropdown(
                        id=f'{iso}-dropdown',
                        options=[
                            {'label': 'Actual', 'value': 'Actual'},
                            {'label': 'Predicted', 'value': 'Predicted'}
                        ],
                        value=['Actual', 'Predicted'],
                        multi=True,
                    ), width=6
            ),
            dbc.Col(width=5),
        ], justify='center'),
        dcc.Graph(id=f'{iso}-graph'),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H3('Training Data'), width=9),
            dbc.Col(width=2)
        ], justify='center'),
        dbc.Row([
            dbc.Col(
                    html.Div(children=model_description), width=9
            ),
            dbc.Col(width=2)
        ], justify='center'),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure=plot_histogram(iso=iso, peak_data=peak_data)
                        ),
                    ]), width=4),
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure=plot_load_duration(
                                iso=iso,
                                load_duration_curves=load_duration_curves
                            ),
                        ),]), width=4),
                dbc.Col(
                    html.Div([
                        dcc.Dropdown(
                            id=f'{iso}-scatter-dropdown',
                            options=[
                                {'label': 'Day of Week', 'value': 'weekday'},
                                {'label': 'Season', 'value': 'season'}
                                ],
                            value='season',
                            multi=False,
                        ),
                        dcc.Graph(id=f'{iso}-scatter')
                    ]
                ), width=4),
            ]
        ),
    ])
    return layout


def plot_load_curve(value, iso: str, load: dict, predictions: dict):
    iso = iso.upper()
    fig = go.Figure()
    if 'Actual' in value:
        fig.add_trace(go.Scatter(
            x=load[iso].index,
            y=load[iso].values,
            name='Actual Load',
            line=dict(color='maroon', width=3)))
    if 'Predicted' in value:
        fig.add_trace(go.Scatter(
            x=predictions[iso].index,
            y=predictions[iso].values,
            name = 'Forecasted Load',
            line=dict(color='darkturquoise', width=3, dash='dash')))
    return fig.update_layout(
        title="System Load: Actual vs. Predicted",
        xaxis_title="Date",
        yaxis_title="Load (MW)",
        template=TEMPLATE
    )


def plot_histogram(iso: str, peak_data: dict):
    iso = iso.upper()
    return px.histogram(
        peak_data[iso],
        x=peak_data[iso]['load_MW'],
        nbins=75,
        marginal="rug",
        title=f"Distribution of {iso} Daily Peaks",
        color_discrete_sequence=['darkturquoise'] 
    ).update_layout(
        template=TEMPLATE,
        xaxis_title='Peak Load (MW)',
        yaxis_title='Number of Days'
    )


def plot_scatter(value, iso: str, peak_data: dict):
    fig = px.scatter(
        peak_data[iso.upper()].dropna(),
        x="load_MW",
        y="temperature", 
        color=value
    )
    return fig.update_layout(
        template=TEMPLATE, title='Peak Load vs. Temperature'
    )

def plot_load_duration(iso: str, load_duration_curves: dict):
    return go.Figure().add_trace(
        go.Scatter(
            x=load_duration_curves[iso.upper()].reset_index().index,
            y=load_duration_curves[iso.upper()].values,
            mode = 'lines',
            fill='tozeroy',
            line=dict(color='maroon', width=3)
        )).update_layout(
            title="Peak Load Sorted by Day (Highest to Lowest)",
            xaxis_title="Number of Days",
            yaxis_title="Load (MW)",
            template=TEMPLATE)

