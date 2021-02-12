import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from peaky_finders.predictor import predict_all, ISO_LIST

# demo_list = ['nyiso', 'pjm', 'isone']
demo_list = ['nyiso']

predictions, actual = predict_all(demo_list)


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Peak Load Forecasting App!"

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.H1(children="Welcome to Peaky Finders"),
    html.Div([
        dcc.Link(
            html.Button('NYISO', id='nyiso-button', className="mr-1"),
            href='/nyiso'),
        dcc.Link(
            html.Button('PJM', id='pjm-button', className="mr-1"),
            href='/pjm'),
        dcc.Link(
            html.Button('ISONE', id='isone-button', className="mr-1"),
            href='/isone'),
    ])])

nyiso_layout = html.Div([
    html.Div(id='nyiso-content'),
    html.H1('NYISO'),
    dcc.Graph(
        figure={
            "data": [
                {
                    "x": predictions['nyiso'].index,
                    "y": predictions['nyiso']['predicted_load'],
                    "type": "lines",
                },
            ],
            "layout": {"title": "Forecasted and Predicted Load for NYISO"},
        },
    ),
    dcc.Graph(
        figure={
            "data": [
                {
                    "x": actual['nyiso'].index,
                    "y": actual['nyiso']['load_MW'],
                    "type": "lines",
                },
            ],
            "layout": {"title": "Avocados Sold"},
        },
    ),
    # html.Br(),
    # dcc.Link('Go to Page 2', href='/nyiso'),
    # html.Br(),
    # dcc.Link('Go back to home', href='/'),
])
@app.callback(dash.dependencies.Output('nyiso-content', 'children'),
              [dash.dependencies.Input('nyiso-button', 'value')])


# pjm_layout = html.Div([
#     html.H1('PJM'),
#     dcc.Graph(
#         figure={
#             "data": [
#                 {
#                     "x": predictions['pjm'].index,
#                     "y": predictions['pjm']['predicted_load'],
#                     "type": "lines",
#                 },
#             ],
#             "layout": {"title": "Forecasted and Predicted Load for PJM"},
#         },
#     ),
#     # html.Div(id='nyiso-content'),
#     # html.Br(),
#     # dcc.Link('Go to Page 2', href='/nyiso'),
#     # html.Br(),
#     # dcc.Link('Go back to home', href='/'),
# ])

@app.callback(dash.dependencies.Output('pjm-content', 'children'),
              [dash.dependencies.Input('pjm-dropdown', 'value')])
def pjm_dropdown(value):
    return 'You have selected "{}"'.format(value)


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
    else:
        return index_page




if __name__ == "__main__":
    app.run_server(debug=True)