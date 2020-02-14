#import necessary packages 
from pyiso import client_factory
import pandas as pd
import config
import json
import numpy as np
import datetime as dt
import calendar
import holidays
from datetime import date, timedelta

#formats datetime string to prepare for joins
def format_datetime(row):
    datetime_string = row['timestamp']
    datetime_string = str(datetime_string)
    datetime_string = datetime_string[:19]
    row['timestamp'] = datetime_string
    return row

#gets load info for nyiso  
def previous_7days_load():
    nyiso = client_factory('NYISO', timeout_seconds=60)
    begin = (dt.datetime.today() - timedelta(7)).strftime('%Y-%m-%d %H')
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
    return df

if __name__ == '__main__':
    print('load functions imported')
