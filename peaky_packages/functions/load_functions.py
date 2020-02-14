#import necessary packages
import pandas as pd
import datetime as dt
import calendar
from datetime import date, timedelta
from pyiso import client_factory

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
    DF = nyiso.get_load(latest=False, yesterday=False, start_at=begin, end_at=end)
    DF = pd.DataFrame(DF)
    DF = DF[['load_MW', 'timestamp']]
    DF = DF.set_index('timestamp')
    DF.index = DF.index.tz_convert('US/Eastern')
    DF = DF.resample('H').max()
    DF = DF.reset_index()
    DF = DF.apply(format_datetime, axis=1)
    DF['timestamp'] = pd.to_datetime(DF['timestamp'], format='%Y-%m-%d %H:%M')
    DF = DF.set_index('timestamp')
    return DF

if __name__ == '__main__':
    print('load functions imported')
