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

#gets current weather information from darksky api 
def get_current_weather(datetime):
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
    currently = info['currently']
    t = currently['time']
    t = str(t)
    t = (pd.to_datetime(t, unit='s'))
    temp = currently['temperature']
    humidity =  currently['humidity'] 
    cloudcover = currently['cloudCover']
    uvindex = currently['uvIndex']
    return temp, humidity, cloudcover, uvindex

#determines if a given day is a US holiday 
us_holidays = holidays.UnitedStates()
def is_holiday(day):
    if day in us_holidays:
        return True
    else:
        return False

#returns day of the week for a given date 
def findDay(date): 
    day = dt.datetime.strptime(date, '%Y-%m-%d %H').weekday() 
    return (calendar.day_name[day])

#formats datetime string to prepare for joins
def format_datetime(row):
    datetime_string = row['timestamp']
    datetime_string = str(datetime_string)
    datetime_string = datetime_string[:19]
    row['timestamp'] = datetime_string
    return row 

#creates ARMA type features  
def prep_V5(df):
    df['load (t-24)'] = df.load_MW.shift(24) 
    df['first seasonal difference'] = df.load_MW.shift(24) - df.load_MW.shift(25) 
    df['prev-day-hour-Std'] = df.load_MW.shift(24).rolling(window=24).std()
    df['prev-day-hour-MA'] = df.load_MW.shift(24).rolling(window=24).mean()
    return df 

#helper function for format hour 
def split(word): 
    return [char for char in word] 

#formats hour for xg boost model
def format_hour(hour):
    hour = split(hour)
    if hour[0] == '0':
        hour = hour[1:]
    elif hour[0] != '0':
        hour = hour 
    z = ''
    hour = z.join(hour)
    hour = hour + '.0'
    return hour

#returns dataframe ready for xg boost model 
def load_forecast_48hr(datetime):
    nyiso = client_factory('NYISO', timeout_seconds=60)
    #weather data
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
        hour = d[11:13]
        hour = format_hour(hour)
        temp = dic['temperature']
        humidity =  dic['humidity'] 
        cloudcover = dic['cloudCover']
        uvindex = dic['uvIndex']
        forecasts.append(tuple([t, temp, humidity, cloudcover, uvindex, weekday, hour, holiday]))
    forecasts = pd.DataFrame(forecasts)
    forecasts.columns = ['timestamp', 'temperature', 'humidity', 'cloudcover', 'uvindex', 'weekday', 'hour', 'holiday']
    #pyiso load data
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
    future = pd.date_range(pd.datetime.today().strftime('%Y-%m-%d %H'), periods = 24, freq ='H')
    future = pd.DataFrame(future)
    future.columns = ['timestamp']
    future = future.set_index('timestamp')
    combine = [df, future]
    total = pd.concat(combine)
    total = prep_V5(total)
    total = total[['load (t-24)', 'first seasonal difference', 'prev-day-hour-Std', 'prev-day-hour-MA']]
    total = total.dropna(axis = 0, how ='any')
    total = total.reset_index()
    result = pd.merge(total,
                 forecasts,
                 on='timestamp', 
                 how='left')
    result = result.dropna(axis = 0, how ='any')
    result = result.set_index('timestamp')
    day_dummies = pd.get_dummies(result['weekday'], prefix='day', drop_first=True)
    hour_dummies = pd.get_dummies(result['hour'], prefix='hour', drop_first=True)
    holiday_dummies = pd.get_dummies(result['holiday'], prefix='holiday', drop_first=True)
    result = result.drop(['weekday', 'hour', 'holiday'], axis=1)
    result = pd.concat([result, day_dummies, hour_dummies, holiday_dummies], axis=1)
    return result

#adds categorical dummy variables 
def add_categorical_dummies(df):
    df['day_Monday'] =0 
    df['day_Tuesday']=0 
    df['day_Wednesday']=0 
    df['day_Thursday']=0 
    df['day_Saturday']=0 
    df['day_Sunday']=0 
    df['hour_1.0'] =0 
    df['hour_2.0']=0 
    df['hour_3.0']=0 
    df['hour_4.0']=0 
    df['hour_5.0']=0 
    df['hour_6.0']=0
    df['hour_7.0'] =0 
    df['hour_8.0']=0 
    df['hour_9.0']=0 
    df['hour_10.0']=0 
    df['hour_11.0']=0 
    df['hour_12.0']=0
    df['hour_13.0'] =0 
    df['hour_14.0']=0 
    df['hour_15.0']=0 
    df['hour_16.0']=0 
    df['hour_17.0']=0 
    df['hour_18.0']=0
    df['hour_19.0']=0 
    df['hour_21.0']=0 
    df['hour_22.0']=0
    df['hour_23.0']=0
    df['holiday_1.0']=0
    if 'day_Monday' in df.columns:
        df['day_Monday'] = 1
    elif 'day_Monday' not in df.columns:
        df['day_Monday'] = 0
    if 'day_Tuesday' in df.columns:
        df['day_Tuesday'] = 1
    elif 'day_Tuesday' not in df.columns:
        df['day_Tuesday'] = 0
    if 'day_Wednesday' in df.columns:
        df['day_Wednesday'] = 1
    elif 'day_Wednesday' not in df.columns:
        df['day_Wednesday'] = 0
    if 'day_Thursday' in df.columns:
        df['day_Thursday'] = 1
    elif 'day_Thursday' not in df.columns:
        df['day_Thursday'] = 0
    if 'day_Saturday' not in df.columns:
        df['day_Saturday'] = 0
    elif 'day_Saturday' not in df.columns:
        df['day_Saturday'] = 0
    if 'day_Sunday' not in df.columns:
        df['day_Sunday'] = 0
    elif 'day_Sunday' not in df.columns:
        df['day_Sunday'] = 0
    if 'hour_1.0' in df.columns:
        df['hour_1.0'] = 1
    elif 'hour_1.0' not in df.columns:
        df['hour_1.0'] = 0
    if 'hour_2.0' in df.columns:
        df['hour_2.0'] = 1
    elif 'hour_2.0' not in df.columns:
        df['hour_2.0'] = 0
    if 'hour_3.0' in df.columns:
        df['hour_3.0'] = 1
    elif 'hour_3.0' not in df.columns:
        df['hour_3.0'] = 0
    if 'hour_4.0' in df.columns:
        df['hour_4.0'] = 1
    elif 'hour_4.0' not in df.columns:
        df['hour_4.0'] = 0
    if 'hour_5.0' not in df.columns:
        df['hour_5.0'] = 0
    elif 'hour_5.0' not in df.columns:
        df['hour_5.0'] = 0
    if 'hour_6.0' not in df.columns:
        df['hour_6.0'] = 0
    elif 'hour_6.0' not in df.columns:
        df['hour_6.0'] = 0
    if 'hour_7.0' in df.columns:
        df['hour_7.0'] = 1
    elif 'hour_7.0' not in df.columns:
        df['hour_7.0'] = 0
    if 'hour_8.0' in df.columns:
        df['hour_8.0'] = 1
    elif 'hour_8.0' not in df.columns:
        df['hour_8.0'] = 0
    if 'hour_9.0' in df.columns:
        df['hour_9.0'] = 1
    elif 'hour_9.0' not in df.columns:
        df['hour_9.0'] = 0
    if 'hour_10.0' in df.columns:
        df['hour_10.0'] = 1
    elif 'hour_10.0' not in df.columns:
        df['hour_10.0'] = 0
    if 'hour_11.0' not in df.columns:
        df['hour_11.0'] = 0
    elif 'hour_11.0' not in df.columns:
        df['hour_11.0'] = 0
    if 'hour_12.0' not in df.columns:
        df['hour_12.0'] = 0
    elif 'hour_12.0' not in df.columns:
        df['hour_12.0'] = 0
    if 'hour_13.0' not in df.columns:
        df['hour_13.0'] = 0
    elif 'hour_13.0' not in df.columns:
        df['hour_13.0'] = 0
    if 'hour_15.0' not in df.columns:
        df['hour_15.0'] = 0
    elif 'hour_15.0' not in df.columns:
        df['hour_15.0'] = 0
    if 'hour_16.0' not in df.columns:
        df['hour_16.0'] = 0
    elif 'hour_16.0' not in df.columns:
        df['hour_16.0'] = 0
    if 'hour_17.0' not in df.columns:
        df['hour_17.0'] = 0
    elif 'hour_17.0' not in df.columns:
        df['hour_17.0'] = 0
    if 'hour_18.0' not in df.columns:
        df['hour_18.0'] = 0
    elif 'hour_18.0' not in df.columns:
        df['hour_18.0'] = 0
    if 'hour_19.0' not in df.columns:
        df['hour_19.0'] = 0
    elif 'hour_19.0' not in df.columns:
        df['hour_19.0'] = 0
    if 'hour_20.0' not in df.columns:
        df['hour_20.0'] = 0
    elif 'hour_20.0' not in df.columns:
        df['hour_20.0'] = 0
    if 'hour_21.0' not in df.columns:
        df['hour_21.0'] = 0
    elif 'hour_21.0' not in df.columns:
        df['hour_21.0'] = 0
    if 'hour_22.0' not in df.columns:
        df['hour_22.0'] = 0
    elif 'hour_22.0' not in df.columns:
        df['hour_22.0'] = 0
    if 'hour_23.0' not in df.columns:
        df['hour_23.0'] = 0
    elif 'hour_23.0' not in df.columns:
        df['hour_23.0'] = 0
    return df 

#prepares forecasts for plotting 
def prepare_predictions(array, df_x):
    df_pred = pd.DataFrame(array)
    df_lets_see = df_x.copy()
    df_lets_see = df_lets_see.reset_index()
    df_lets_see = df_lets_see.join(df_pred)
    df_lets_see = df_lets_see[['timestamp', 0]]
    df_lets_see.columns = ['timestamp', 'Predicted Load']
    df_lets_see = df_lets_see.set_index('timestamp')
    return df_lets_see

#standardize data based on training dataset, get columns in order
def standardize_data(df, master_df):
    df = df[['cloudcover', 'first seasonal difference', 'humidity', 'load (t-24)', 'prev-day-hour-MA', 'prev-day-hour-Std', 'temperature', 'uvindex', 'day_Monday', 'day_Saturday', 'day_Sunday', 'day_Thursday', 'day_Tuesday', 'day_Wednesday', 'hour_1.0', 'hour_2.0', 'hour_3.0', 'hour_4.0', 'hour_5.0', 'hour_6.0', 'hour_7.0', 'hour_8.0', 'hour_9.0', 'hour_10.0', 'hour_11.0', 'hour_12.0', 'hour_13.0', 'hour_14.0', 'hour_15.0', 'hour_16.0', 'hour_17.0', 'hour_18.0', 'hour_19.0', 'hour_20.0', 'hour_21.0', 'hour_22.0', 'hour_23.0', 'holiday_1.0']]
    master_df['timestamp'] = pd.to_datetime(master_df['timestamp'], format='%Y-%m-%d %H:%M')
    master_df = master_df.set_index('timestamp')
    master_df = master_df.drop('load_MW', 1)
    df_combo = [master_df, df]
    df_combo = pd.concat(df_combo)
    df_combo['temperature'] = (df_combo['temperature'] - np.mean(df_combo['temperature'])) / np.sqrt(np.var(df_combo['temperature']))
    df_combo['load (t-24)'] = (df_combo['load (t-24)'] - np.mean(df_combo['load (t-24)'])) / np.sqrt(np.var(df_combo['load (t-24)']))
    df_combo['first seasonal difference'] = (df_combo['first seasonal difference'] - np.mean(df_combo['first seasonal difference'])) / np.sqrt(np.var(df_combo['first seasonal difference']))
    df_combo['prev-day-hour-Std'] = (df_combo['prev-day-hour-Std'] - np.mean(df_combo['prev-day-hour-Std'])) / np.sqrt(np.var(df_combo['prev-day-hour-Std']))
    df_combo['prev-day-hour-MA'] = (df_combo['prev-day-hour-MA'] - np.mean(df_combo['prev-day-hour-MA'])) / np.sqrt(np.var(df_combo['prev-day-hour-MA']))
    df = df_combo[-19:] 
    return df

#outputs dataframe with predictions for the next day hourly NYISO load
def final_forecast(date):
    xgb_model_loaded = pickle.load(open('xg_boost_load_model.pkl', "rb"))
    x_forecast = load_forecast_48hr(pd.datetime.today().strftime('%Y-%m-%d %H'))
    master_df = pd.read_csv('training.csv')
    x_forecast = add_categorical_dummies(x_forecast)
    x = standardize_data(x_forecast, master_df)
    predictions = xgb_model_loaded.predict(x)
    df_pred = pd.DataFrame(predictions)
    forecast = prepare_predictions(predictions, x)
    return forecast 

#outputs dictionary with predictions for the next day hourly NYISO load 
# def final_forecast_dict(date):
#     xgb_model_loaded = pickle.load(open('xg_boost_load_modelV3.pkl', "rb"))
#     x_forecast = load_forecast_48hr(pd.datetime.today().strftime('%Y-%m-%d %H'))
#     master_df = pd.read_csv('training.csv')
#     x_forecast = add_categorical_dummies(x_forecast)
#     x = standardize_data(x_forecast, master_df)
#     predictions = xgb_model_loaded.predict(x)
#     df_pred = pd.DataFrame(predictions)
#     forecast = prepare_predictions(predictions, x)
#     forecast = forecast.to_dict()
#     forecast = forecast['Predicted Load']
#     return forecast 


# #######

# #functions that will gather historical forecast information for the past 7 days, make predictions, and calculate the RMSE of the last 7 days
# def get_nyc_weather_data_for_date(datetime_string, verbose=True):
#     api_key = config.api_key
#     nyc_lat = "40.7128"
#     nyc_long = "-73.935242"
#     url_base = "https://api.darksky.net/forecast"
#     exclude = 'flags,minutely,alerts,daily'    
#     year, month, day = format_date_A(datetime_string)
        
#     datetime = "{}-{}-{}T00:00:00".format(year, month, day)
#     full_url = "{}/{}/{},{},{}?exclude={}".format(url_base, api_key, 
#                                                      nyc_lat, nyc_long, 
#                                                      datetime, exclude)
#     response = requests.get(full_url)
#     if response.status_code == 200:
#         if verbose:
#             print(response.status_code)
#         return response, datetime_string
#     else: 
#         raise ValueError("Error getting data from DarkSky API: Response Code {}".format(response.status_code))
#     return datetime_string, response

# def format_date_A(datetime_string):
#     year = datetime_string[:4]
#     month = datetime_string[5:7]
#     day = datetime_string[8:10]
#     return year, month, day

# def findDay_A(date): 
#     day = dt.datetime.strptime(date, '%Y-%m-%d %H').weekday() 
#     return (calendar.day_name[day]) 
    
# def get_nyc_weather_data_for_date(datetime_string, verbose=True):
#     api_key = config.api_key
#     nyc_lat = "40.7128"
#     nyc_long = "-73.935242"
#     url_base = "https://api.darksky.net/forecast"
#     exclude = 'flags,minutely,alerts,daily'    
#     year, month, day = format_date_A(datetime_string)
        
#     datetime = "{}-{}-{}T00:00:00".format(year, month, day)
#     full_url = "{}/{}/{},{},{}?exclude={}".format(url_base, api_key, 
#                                                      nyc_lat, nyc_long, 
#                                                      datetime, exclude)
#     response = requests.get(full_url)
#     if response.status_code == 200:
#         if verbose:
#             print(response.status_code)
#         return response, datetime_string
#     else: 
#         raise ValueError("Error getting data from DarkSky API: Response Code {}".format(response.status_code))
#     return datetime_string, response

# def standardize_data_7(df, master_df):
#     df = df[['cloudcover', 'first seasonal difference', 'humidity', 'load (t-24)', 'prev-day-hour-MA', 'prev-day-hour-Std', 'temperature', 'uvindex', 'day_Monday', 'day_Saturday', 'day_Sunday', 'day_Thursday', 'day_Tuesday', 'day_Wednesday', 'hour_1.0', 'hour_2.0', 'hour_3.0', 'hour_4.0', 'hour_5.0', 'hour_6.0', 'hour_7.0', 'hour_8.0', 'hour_9.0', 'hour_10.0', 'hour_11.0', 'hour_12.0', 'hour_13.0', 'hour_14.0', 'hour_15.0', 'hour_16.0', 'hour_17.0', 'hour_18.0', 'hour_19.0', 'hour_20.0', 'hour_21.0', 'hour_22.0', 'hour_23.0', 'holiday_1.0']]
#     master_df['timestamp'] = pd.to_datetime(master_df['timestamp'], format='%Y-%m-%d %H:%M')
#     master_df = master_df.set_index('timestamp')
#     master_df = master_df.drop('load_MW', 1)
#     df_combo = [master_df, df]
#     df_combo = pd.concat(df_combo)
#     df_combo['temperature'] = (df_combo['temperature'] - np.mean(df_combo['temperature'])) / np.sqrt(np.var(df_combo['temperature']))
#     df_combo['load (t-24)'] = (df_combo['load (t-24)'] - np.mean(df_combo['load (t-24)'])) / np.sqrt(np.var(df_combo['load (t-24)']))
#     df_combo['first seasonal difference'] = (df_combo['first seasonal difference'] - np.mean(df_combo['first seasonal difference'])) / np.sqrt(np.var(df_combo['first seasonal difference']))
#     df_combo['prev-day-hour-Std'] = (df_combo['prev-day-hour-Std'] - np.mean(df_combo['prev-day-hour-Std'])) / np.sqrt(np.var(df_combo['prev-day-hour-Std']))
#     df_combo['prev-day-hour-MA'] = (df_combo['prev-day-hour-MA'] - np.mean(df_combo['prev-day-hour-MA'])) / np.sqrt(np.var(df_combo['prev-day-hour-MA']))
#     return df


# def get_7day_forecast():
#     start = (dt.datetime.today() - timedelta(7)).strftime('%Y-%m-%d %H')
#     datelist = pd.date_range(start, periods=7).tolist()
#     dates = []
#     for date in datelist:
#         date = str(date)
#         date = date[:10]
#         dates.append(date)
#     total = []
#     for date in dates:
#         response, date = get_nyc_weather_data_for_date(date, verbose=True)
#         info = response.json()
#         hourly = info['hourly']
#         hourly = hourly['data']
#         forecasts = []
#         for i in list(range(len(hourly))):
#             dic = hourly[i] 
#             t = dic['time']
#             t = str(t)
#             t = (pd.to_datetime(t, unit='s'))
#             d = str(t)
#             d = d[:-6]
#             weekday = findDay_A(d)
#             holiday = is_holiday(d)
#             hour = d[11:13]
#             hour = format_hour(hour)
#             temp = dic['temperature']
#             humidity =  dic['humidity'] 
#             cloudcover = dic['cloudCover']
#             uvindex = dic['uvIndex']
#             forecasts.append(tuple([t, temp, humidity, cloudcover, uvindex, weekday, hour, holiday]))
#         forecasts = pd.DataFrame(forecasts)
#         forecasts.columns = ['timestamp', 'temperature', 'humidity', 'cloudcover', 'uvindex', 'weekday', 'hour', 'holiday']
#         total.append(forecasts)
#     df = pd.concat(total)
#     #gather load data
#     nyiso = client_factory('NYISO', timeout_seconds=60)
#     begin = (dt.datetime.today() - timedelta(8)).strftime('%Y-%m-%d %H')
#     end = pd.datetime.today().strftime('%Y-%m-%d %H')
#     df_1 = nyiso.get_load(latest=False, yesterday=False, start_at=begin, end_at=end)
#     df_1 = pd.DataFrame(df_1)
#     df_1 = df_1[['load_MW', 'timestamp']]
#     df_1 = df_1.set_index('timestamp')
#     #df_1.index = df.index.tz_convert('US/Eastern')
#     df_1 = df_1.resample('H').max()
#     df_1 = df_1.reset_index()
#     df_1 = df_1.apply(format_datetime, axis=1)
#     df_1['timestamp'] = pd.to_datetime(df_1['timestamp'], format='%Y-%m-%d %H:%M')
#     df_1 = df_1.set_index('timestamp')
#     df_1 = prep_V5(df_1)
#     df_1 = df_1[['load (t-24)', 'first seasonal difference', 'prev-day-hour-Std', 'prev-day-hour-MA']]
#     df_1 = df_1.dropna(axis = 0, how ='any')
#     df_1 = df_1.reset_index()
#     result = pd.merge(df_1,
#                  df,
#                  on='timestamp', 
#                  how='left')
#     result = result.dropna(axis = 0, how ='any')
#     result = result.set_index('timestamp')
#     day_dummies = pd.get_dummies(result['weekday'], prefix='day', drop_first=True)
#     hour_dummies = pd.get_dummies(result['hour'], prefix='hour', drop_first=True)
#     holiday_dummies = pd.get_dummies(result['holiday'], prefix='holiday', drop_first=True)
#     result = result.drop(['weekday', 'hour', 'holiday'], axis=1)
#     result = pd.concat([result, day_dummies, hour_dummies, holiday_dummies], axis=1)
#     ## load model
#     xgb_model_loaded = pickle.load(open('xg_boost_load_modelV3.pkl', "rb"))
#     master_df = pd.read_csv('training.csv')
#     result = add_categorical_dummies(result)
#     x = standardize_data_7(result, master_df)
#     x = x[['temperature', 'humidity', 'cloudcover', 'uvindex', 'load (t-24)', 'first seasonal difference', 'prev-day-hour-Std', 'prev-day-hour-MA', 'day_Monday', 'day_Saturday', 'day_Sunday', 'day_Thursday', 'day_Tuesday', 'day_Wednesday', 'hour_1.0', 'hour_2.0', 'hour_3.0', 'hour_4.0', 'hour_5.0', 'hour_6.0', 'hour_7.0', 'hour_8.0', 'hour_9.0', 'hour_10.0', 'hour_11.0', 'hour_12.0', 'hour_13.0', 'hour_14.0', 'hour_15.0', 'hour_16.0', 'hour_17.0', 'hour_18.0', 'hour_19.0', 'hour_20.0', 'hour_21.0', 'hour_22.0', 'hour_23.0', 'holiday_1.0']]
#     predictions = xgb_model_loaded.predict(x)
#     x = x.reset_index()
#     df_pred = pd.DataFrame(predictions)
#     df_pred.columns = ['Predicted Load']
#     df_total = pd.concat([x, df_pred], axis=1)
#     df_total = df_total.set_index('timestamp')
#     df_total = df_total['Predicted Load']
#     return df_total