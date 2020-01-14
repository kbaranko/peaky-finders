from pyiso import client_factory
import pandas as pd
import config
import requests
import config
import json
import pandas as pd
import numpy as np
import calendar
import holidays
import datetime as dt
from datetime import date, datetime, timedelta
import pickle 

#used to loop over load dataframe to get weather information for that day
def nyc_weather_data(row, verbose=True):
    row['temperature'] = 0
    row['humidity'] = 0
    row['cloudcover'] = 0
    row['uvindex'] = 0
    temperature = 0
    humidity = 0 
    cloudcover = 0
    uvindex = 0
    string = row['timestamp']
    datetime_string = str(string)
    api_key = config.api_key
    nyc_lat = "40.7128"
    nyc_long = "-73.935242"
    url_base = "https://api.darksky.net/forecast"
    exclude = 'flags,minutely,alerts,hourly,daily'    
    year, month, day, hour = format_datetime(datetime_string)
        
    datetime = "{}-{}-{}T{}:00:00".format(year, month, day, hour)
    full_url = "{}/{}/{},{},{}?exclude={}".format(url_base, api_key, 
                                                     nyc_lat, nyc_long, 
                                                     datetime, exclude)
    response = requests.get(full_url)
    if response.status_code == 200:
        if verbose:
            print(response.status_code)
    else: 
        raise ValueError("Error getting data from DarkSky API: Response Code {}".format(response.status_code))
    info = response.json()
    currently = info['currently']
    try:
        temperature = currently['temperature']
    except:
        temperature = 0
    try:
        humidity = currently['humidity']
    except:
        humidity = 0
    try:
        cloudcover = currently['cloudCover']
    except:
        cloudcover = 0
    try:
        uvindex = currently['uvIndex']
    except:
        unvindex = 0
    row['temperature'] = temperature
    row['humidity'] = humidity
    row['cloudcover'] = cloudcover
    row['uvindex'] = uvindex
    return row

#determines if a given day is a US holiday 
us_holidays = holidays.UnitedStates()
def is_holiday(day):
    if day in us_holidays:
        return True
    else:
        return False

#returns day of the week for a given date 
def findDay(date): 
    day = dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').weekday() 
    return (calendar.day_name[day])
    

#formats datetime string to prepare for joins
def format_datetime(datetime_string):
    year = datetime_string[:4]
    month = datetime_string[5:7]
    day = datetime_string[8:10]
    hour = datetime_string[11:13]
    return year, month, day, hour

#creates weekday, time of day, and holiday variables 
def day_time_holiday(row):
    row['hour_of_day'] = 0
    row['day_of_week'] = 0
    row['holiday'] = 0
    date = row['timestamp']
    holi = is_holiday(date)
    date = str(date)
    date = date[:19]
    day_of_week = findDay(date)
    date = date.split(' ')
    time = date[1]
    time = time.split(':')
    hour = time[0]
    row['hour_of_day'] = hour
    row['day_of_week'] = day_of_week
    row['holiday'] = holi
    return row 

def prep_V5(df):
    df['load (t-24)'] = df.load_MW.shift(24) 
    df['first seasonal difference'] = df.load_MW.shift(24) - df.load_MW.shift(25) 
    df['prev-day-hour-Std'] = df.load_MW.shift(24).rolling(window=24).std()
    df['prev-day-hour-MA'] = df.load_MW.shift(24).rolling(window=24).mean()
    df = df.dropna(axis = 0, how ='any')
    return df 

def missing_values(df):
    df[df['temperature'] == 0] = np.NaN
    df[df['humidity'] == 0] = np.NaN
    df = df.fillna(method='ffill')
    return df 

def get_dummies(df):
    day_dummies = pd.get_dummies(df['day_of_week'], prefix='day', drop_first=True)
    hour_dummies = pd.get_dummies(df['hour_of_day'], prefix='hour', drop_first=True)
    holiday_dummies = pd.get_dummies(df['holiday'], prefix='holiday', drop_first=True)
    df = df.drop(['day_of_week', 'hour_of_day', 'holiday'], axis=1)
    df = pd.concat([df, day_dummies, hour_dummies, holiday_dummies], axis=1)
    df = df.dropna(axis = 0, how ='any')
    return df

def standardize(df):
    df['temperature'] = (df['temperature'] - np.mean(df['temperature'])) / np.sqrt(np.var(df['temperature']))
    df['load (t-24)'] = (df['load (t-24)'] - np.mean(df['load (t-24)'])) / np.sqrt(np.var(df['load (t-24)']))
    df['first seasonal difference'] = (df['first seasonal difference'] - np.mean(df['first seasonal difference'])) / np.sqrt(np.var(df['first seasonal difference']))
    df['prev-day-hour-Std'] = (df['prev-day-hour-Std'] - np.mean(df['prev-day-hour-Std'])) / np.sqrt(np.var(df['prev-day-hour-Std']))
    df['prev-day-hour-MA'] = (df['prev-day-hour-MA'] - np.mean(df['prev-day-hour-MA'])) / np.sqrt(np.var(df['prev-day-hour-MA']))
    return df

#returns dataframe of historical load data 
def get_nyiso_data(begin, end):
    nyiso = client_factory('NYISO', timeout_seconds=60)
    df = nyiso.get_load(latest=False, yesterday=False, start_at=begin, end_at=end)
    df = pd.DataFrame(df)
    df = df[['load_MW', 'timestamp']]
    df = df.set_index('timestamp')
    df.index = df.index.tz_convert('US/Eastern')
    df = df.resample('H').max()
    df = df.reset_index()
    return df

def get_features(df):
    df = df.apply(nyc_weather_data, axis=1)
    df = df.apply(day_time_holiday, axis=1)
    df = df.set_index('timestamp')
    return df


#after combining csvs, run standardize and get 
def prep_nyiso_data(df):
    df = missing_values(df)
    df = get_dummies(df)
    df = standardize(df)
    return df


