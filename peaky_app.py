import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from peaky_finders.app_utils import get_peak_data, get_forecasts
import peaky_finders.constants as c
from peaky_finders.iso_map import get_iso_map
from peaky_finders.app_utils import create_load_duration
import peaky_finders.iso_layout as l


iso_map = get_iso_map()
peak_data = get_peak_data(c.ISO_LIST)
predictions, load, temperature = get_forecasts(c.ISO_LIST)
load_duration_curves = create_load_duration(peak_data)


TEMPLATE = 'plotly_white'
MONTH = 'February'

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
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H1(children="Welcome to Peaky Finders"), width=5),
            dbc.Col(width=5),
        ], justify='center'),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H4(
                        children=(
                            "To what extent do weather and weekday determine",
                            "total electricity demand on the grid? Click an"
                            "ISO button below to find out.")),
                    html.Div(l.BUTTON_LAYOUT)]), width=7
            ),
            dbc.Col(width=3),
        ], justify="center"),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H4(children="ISO Territory Map"), width=4),
            dbc.Col(width=4)
        ], justify='center'),
        html.Div([
            dcc.Graph(figure=px.choropleth(
                        iso_map,
                        geojson=iso_map.geometry,
                        locations=iso_map.index,
                        color="NAME",
                        projection="mercator",
                        ).update_geos(
                            fitbounds="locations",
                            visible=False).update_layout(
                                height=600,
                                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                            )
                        ) 
        ], style = {'display': 'inline-block', 'width': '90%'})
])


"""NYISO LAYOUT"""
nyiso_layout = l.set_iso_layout(
    iso='nyiso',
    full_name=c.NYISO_FULL_NAME,
    description=c.NYISO_DESCRIPTION,
    month=MONTH,
    mae=c.NYISO_MAE,
    model_description=c.NYISO_MODEL_DESCRIPTION,
    peak_data=peak_data,
    load_duration_curves=load_duration_curves,
)
@app.callback(dash.dependencies.Output('nyiso-content', 'children'),
              [dash.dependencies.Input('nyiso-button', 'value')])


@app.callback(dash.dependencies.Output('nyiso-graph', 'figure'),
             [dash.dependencies.Input('nyiso-dropdown', 'value')])
def plot_nyiso_load_(value):
    return l.plot_load_curve(
        value, iso='nyiso', load=load, predictions=predictions
    )

@app.callback(dash.dependencies.Output("nyiso-scatter", "figure"), 
    [dash.dependencies.Input("nyiso-scatter-dropdown", "value")])
def nyiso_scatter_plot(value):
    return l.plot_scatter(value, iso='nyiso', peak_data=peak_data)


"""PJM LAYOUT"""
pjm_layout = l.set_iso_layout(
    iso='pjm',
    full_name=c.PJM_FULL_NAME,
    description=c.PJM_DESCRIPTION,
    month=MONTH,
    mae=c.PJM_MAE,
    model_description=c.PJM_MODEL_DESCRIPTION,
    peak_data=peak_data,
    load_duration_curves=load_duration_curves,
)
@app.callback(dash.dependencies.Output('pjm-content', 'children'),
              [dash.dependencies.Input('pjm-button', 'value')])


@app.callback(dash.dependencies.Output('pjm-graph', 'figure'),
             [dash.dependencies.Input('pjm-dropdown', 'value')])
def plot_pjm_load_(value):
    return l.plot_load_curve(
        value, iso='pjm', load=load, predictions=predictions
    )

@app.callback(dash.dependencies.Output("pjm-scatter", "figure"), 
    [dash.dependencies.Input("pjm-scatter-dropdown", "value")])
def pjm_scatter_plot(value):
    return l.plot_scatter(value, iso='pjm', peak_data=peak_data)


"""MISO LAYOUT"""
miso_layout = l.set_iso_layout(
    iso='miso',
    full_name=c.MISO_FULL_NAME,
    description=c.MISO_DESCRIPTION,
    month=MONTH,
    mae=c.MISO_MAE,
    model_description=c.MISO_MODEL_DESCRIPTION,
    peak_data=peak_data,
    load_duration_curves=load_duration_curves,
)
@app.callback(dash.dependencies.Output('miso-content', 'children'),
              [dash.dependencies.Input('miso-button', 'value')])


@app.callback(dash.dependencies.Output('miso-graph', 'figure'),
             [dash.dependencies.Input('miso-dropdown', 'value')])
def plot_miso_load_(value):
    return l.plot_load_curve(
        value, iso='miso', load=load, predictions=predictions
    )

@app.callback(dash.dependencies.Output("miso-scatter", "figure"), 
    [dash.dependencies.Input("miso-scatter-dropdown", "value")])
def miso_scatter_plot(value):
    return l.plot_scatter(value, iso='miso', peak_data=peak_data)


"""ISONE LAYOUT"""
isone_layout = l.set_iso_layout(
    iso='isone',
    full_name=c.ISONE_FULL_NAME,
    description=c.ISONE_DESCRIPTION,
    month=MONTH,
    mae=c.ISONE_MAE,
    model_description=c.ISONE_MODEL_DESCRIPTION,
    peak_data=peak_data,
    load_duration_curves=load_duration_curves,
)
@app.callback(dash.dependencies.Output('isone-content', 'children'),
              [dash.dependencies.Input('isone-button', 'value')])


@app.callback(dash.dependencies.Output('isone-graph', 'figure'),
             [dash.dependencies.Input('isone-dropdown', 'value')])
def plot_isone_load_(value):
    return l.plot_load_curve(
        value, iso='isone', load=load, predictions=predictions
    )

@app.callback(dash.dependencies.Output("isone-scatter", "figure"), 
    [dash.dependencies.Input("isone-scatter-dropdown", "value")])
def isone_scatter_plot(value):
    return l.plot_scatter(value, iso='isone', peak_data=peak_data)


"""CAISO LAYOUT"""
caiso_layout = l.set_iso_layout(
    iso='caiso',
    full_name=c.CAISO_FULL_NAME,
    description=c.CAISO_DESCRIPTION,
    month=MONTH,
    mae=c.CAISO_MAE,
    model_description=c.CAISO_MODEL_DESCRIPTION,
    peak_data=peak_data,
    load_duration_curves=load_duration_curves,
)
@app.callback(dash.dependencies.Output('caiso-content', 'children'),
              [dash.dependencies.Input('caiso-button', 'value')])


@app.callback(dash.dependencies.Output('caiso-graph', 'figure'),
             [dash.dependencies.Input('caiso-dropdown', 'value')])
def plot_caiso_load_(value):
    return l.plot_load_curve(
        value, iso='caiso', load=load, predictions=predictions
    )

@app.callback(dash.dependencies.Output("caiso-scatter", "figure"), 
    [dash.dependencies.Input("caiso-scatter-dropdown", "value")])
def caiso_scatter_plot(value):
    return l.plot_scatter(value, iso='caiso', peak_data=peak_data)


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
