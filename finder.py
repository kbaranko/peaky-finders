from flask import Flask, render_template
import pandas as pd
import plotly.graph_objs as go
from load_functions import * 
from dash import Dash
import dash_html_components as html
from log_functions import *

app = Flask(__name__)

load = final_forecast_dict(pd.datetime.today().strftime('%Y-%m-%d %H'))
peak = log_forecast_to_dict(pd.datetime.today().strftime('%Y-%m-%d %H'))
answer = return_values(pd.datetime.today().strftime('%Y-%m-%d %H'))

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', load=load, peak=peak, answer=answer)


@app.route("/test")
def test():
    return render_template('test.html', load=load, peak=peak, answer=answer)

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)