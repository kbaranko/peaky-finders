from pyiso import client_factory
import pandas as pd
import config
import requests
import config
import json
import pandas as pd
import numpy as np
import datetime as dt
import calendar
import holidays
from datetime import date, timedelta
import pickle
import math


#script will only work if 1.config.py file is in main program directory that is importing
#this module and 2. pkl file is in main program directory to run model
us_holidays = holidays.UnitedStates()
def is_holiday(day):
    if day in us_holidays:
        return True
    else:
        return False

#returns day of the week for a given date
def findDay(date):
    day = dt.datetime.strptime(date, '%Y-%m-%d %H').weekday()
    return calendar.day_name[day]

#formats datetime string to prepare for joins
def format_datetime(row):
    datetime_string = row['timestamp']
    datetime_string = str(datetime_string)
    datetime_string = datetime_string[:19]
    row['timestamp'] = datetime_string
    return row

def prepare_predictions_log(array, df_x):
    df_pred = pd.DataFrame(array)
    df_lets_see = df_x.copy()
    df_lets_see = df_lets_see.reset_index()
    df_lets_see = df_lets_see.join(df_pred)
    df_lets_see = df_lets_see[['timestamp', 0]]
    df_lets_see.columns = ['timestamp', 'Peak Day']
    df_lets_see = df_lets_see.set_index('timestamp')
    return df_lets_see

def prep_V6(df):
    df['load (t-1)'] = df.load_MW.shift(1)
    df['first difference'] = df.load_MW.shift(1) - df.load_MW.shift(2)
    return df

def format_datetime_peak_day(row):
    datetime_string = row['timestamp']
    datetime_string = str(datetime_string)
    datetime_string = datetime_string[:11]
    row['timestamp'] = datetime_string
    return row


def load_forecast_48hr_log(datetime):
    nyiso = client_factory('NYISO', timeout_seconds=60)
    api_key = config.api_key
    nyc_lat = "40.7128"
    nyc_long = "-73.935242"
    url_base = "https://api.darksky.net/forecast"
    exclude = 'flags, minutely, daily, alerts'
    full_url = "{}/{}/{},{}?exclude={}".format(url_base, api_key,
                                               nyc_lat, nyc_long, 
                                               exclude)
    response = requests.get(full_url)
    info = response.json()
    hourly = info['hourly']
    hourly = hourly['data']
    forecasts = []
    for i in list(range(len(hourly))):
        dic = hourly[i]
        t = dic['time']
        t = str(t)
        t = (pd.to_datetime(t, unit='s'))
        d = str(t)
        d = d[:-6]
        weekday = findDay(d)
        holiday = is_holiday(d)
        temp = dic['temperature']
        forecasts.append(tuple([t, temp, weekday, holiday]))
    forecasts = pd.DataFrame(forecasts)
    forecasts.columns = ['timestamp', 'temperature', 'weekday', 'holiday']
    begin = (dt.datetime.today() - timedelta(2)).strftime('%Y-%m-%d %H')
    end = pd.datetime.today().strftime('%Y-%m-%d %H')
    df = nyiso.get_load(latest=False, yesterday=False, start_at=begin, end_at=end)
    df = pd.DataFrame(df)
    df = df[['load_MW', 'timestamp']]
    df = df.set_index('timestamp')
    df.index = df.index.tz_convert('US/Eastern')
    df = df.resample('H').max()
    df = df.reset_index()
    df = df.apply(format_datetime, axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M')
    df = df.set_index('timestamp')
    future = pd.date_range(pd.datetime.today().strftime('%Y-%m-%d %H'), periods=24, freq='H')
    future = pd.DataFrame(future)
    future.columns = ['timestamp']
    future = future.set_index('timestamp')
    combine = [df, future]
    total = pd.concat(combine)
    result = pd.merge(total,
                      forecasts,
                      on='timestamp',
                      how='left')
    result = result.set_index('timestamp')
    day_dummies = pd.get_dummies(result['weekday'], prefix='day', drop_first=False)
    holiday_dummies = pd.get_dummies(result['holiday'], prefix='holiday', drop_first=True)
    result = result.drop(['weekday', 'holiday'], axis=1)
    result = pd.concat([result, day_dummies, holiday_dummies], axis=1)
    result = result.resample('D').max()
    result = prep_V6(result)
    result = result.drop('load_MW', 1)
    result = result.dropna(axis=0, how='any')
    return result

def add_categorical_dummies_log(df):
    df['day_Saturday'] = 0
    df['day_Sunday'] = 0
    df['holiday_1.0'] = 0
    if 'day_Saturday' not in df.columns:
        df['day_Saturday'] = 0
    elif 'day_Saturday' not in df.columns:
        df['day_Saturday'] = 0
    if 'day_Sunday' not in df.columns:
        df['day_Sunday'] = 0
    elif 'day_Sunday' not in df.columns:
        df['day_Sunday'] = 0
    return df

def standardize_log_data(df, master_df):
    df = df[['temperature', 'day_Saturday', 'day_Sunday', 'holiday_1.0', 'load (t-1)']]
    master_df = master_df.reset_index()
    master_df['timestamp'] = pd.to_datetime(master_df['timestamp'], format='%Y-%m-%d')
    master_df = master_df.set_index('timestamp')
    master_df = master_df.drop('peak_day', 1)
    df_combo = [master_df, df]
    df_combo = pd.concat(df_combo)
    df_combo['temperature'] = (df_combo['temperature'] - np.mean(df_combo['temperature'])) / np.sqrt(np.var(df_combo['temperature']))
    df_combo['load (t-1)'] = (df_combo['load (t-1)'] - np.mean(df_combo['load (t-1)'])) / np.sqrt(np.var(df_combo['load (t-1)']))
    df = df_combo[-1:]
    df = df.drop('index', 1)
    return df

def log_forecast(date):
    log_model_loaded = pickle.load(open('log_reg_model.pkl', "rb"))
    x_forecast = load_forecast_48hr_log(pd.datetime.today().strftime('%Y-%m-%d %H'))
    master_df = pd.read_csv('log_training.csv')
    x_forecast = add_categorical_dummies_log(x_forecast)
    x_forecast = standardize_log_data(x_forecast, master_df)
    predictions = log_model_loaded.predict(x_forecast)
    df_pred = pd.DataFrame(predictions)
    forecast = prepare_predictions_log(predictions, x_forecast)
    return forecast

def log_forecast_to_dict(date):
    log_model_loaded = pickle.load(open('log_reg_model.pkl', "rb"))
    x_forecast = load_forecast_48hr_log(pd.datetime.today().strftime('%Y-%m-%d %H'))
    master_df = pd.read_csv('log_training.csv')
    x_forecast = add_categorical_dummies_log(x_forecast)
    x_forecast = standardize_log_data(x_forecast, master_df)
    predictions = log_model_loaded.predict(x_forecast)
    df_pred = pd.DataFrame(predictions)
    forecast = prepare_predictions_log(predictions, x_forecast)
    forecast = forecast.reset_index()
    forecast = forecast.apply(format_datetime_peak_day, 1)
    forecast = forecast.set_index('timestamp')
    forecast['Peak Day'] = np.where(forecast['Peak Day'] >= 1, 
                           'There is a good chance', 'Probably Not')
    forecast = forecast.to_dict()
    forecast = forecast['Peak Day']
    return forecast

def prepare_predictions_log(array, df_x):
    df_pred = pd.DataFrame(array)
    df_lets_see = df_x.copy()
    df_lets_see = df_lets_see.reset_index()
    df_lets_see = df_lets_see.join(df_pred)
    df_lets_see = df_lets_see[['timestamp', 0]]
    df_lets_see.columns = ['timestamp', 'Peak Day']
    df_lets_see = df_lets_see.set_index('timestamp')
    return df_lets_see

def peak_confidence(temp, sat, sun, holiday, prev_load):
    e = math.e 
    p = 1/(1 + e**(-1*(2.883978*temp + -1.326981*sat + -1.291990*sun + -0.740864*holiday + 0.759935*prev_load)))
    return p  


def return_values(date):
    log_model_loaded = pickle.load(open('log_reg_model.pkl', "rb"))
    x_forecast = load_forecast_48hr_log(pd.datetime.today().strftime('%Y-%m-%d %H'))
    master_df = pd.read_csv('log_training.csv')
    x_forecast = add_categorical_dummies_log(x_forecast)
    x_forecast = standardize_log_data(x_forecast, master_df)
    sat = x_forecast['day_Saturday'].iloc[0]
    sun = x_forecast['day_Sunday'].iloc[0]
    holiday = x_forecast['holiday_1.0'].iloc[0]
    prev_load = x_forecast['load (t-1)'].iloc[0]
    temp = prev_load = x_forecast['temperature'].iloc[0]
    p = peak_confidence(temp, sat, sun, holiday, prev_load)
    p = round(p, 3)
    p = p * 100
    answer = 'There is a {} percent chance tomorrow will be a peak load day.'
    answer = answer.format(p)
    return answer

if __name__ == '__main__':
    print('log functions imported')
else:
    print('log functions is being imported into another module')
