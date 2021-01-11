import calendar
import datetime as dt
from datetime import timedelta
import holidays
import math
import os

import json
import numpy as np
import pandas as pd
import pickle
from pyiso import client_factory
import requests


LAT = '40.7128'
LON = '-73.935242'
BASE_URL = 'https://api.darksky.net/forecast'
EXCLUDE = 'flags, minutely, daily, alerts'
API_KEY = os.environ['DARKSKY_KEY']
FULL_DARKSKY_URL = f'{BASE_URL}/{API_KEY}/{LAT},{LON},'
LOAD_COLS = ['load_MW', 'timestamp']
EASTERN_TZ = 'US/Eastern'


class NYISO:

    def __init__(self, start_date: str, end_date: str):
        self.start = start_date
        self.end = end_date
        self.holidays = holidays.UnitedStates()
        self.load = self.get_historical_load()
        self.model_input = None

    def get_historical_load(self) -> pd.DataFrame:
        nyiso = client_factory('NYISO', timeout_seconds=60)
        load = pd.DataFrame(
            nyiso.get_load(
                latest=False,
                yesterday=False,
                start_at=self.start,
                end_at=self.end)
            )[LOAD_COLS].set_index('timestamp')
        load.index = load.index.tz_convert(EASTERN_TZ)
        return load.resample('H').mean()

    def engineer_weather_features(self):
        temperatures = dict()
        for date, _ in self.load.iterrows():
            date_input = date.strftime('%s')
            full_url = f'{FULL_DARKSKY_URL}{date_input}?exclude={EXCLUDE}'
            response = requests.get(full_url)
            if response.status_code == 200:
                    print(response.status_code)
            else: 
                raise ValueError(f'Error getting data from DarkSky API: '
                                f'Response Code {response.status_code}')
            info = response.json()
            current_info = info['currently']
            current_temperature = current_info['temperature']
            temperatures[date] = current_temperature
        import pdb; pdb.set_trace()
        self.load['temperature'] = self.load.index.map(temperatures)

    def engineer_datetime_features(self):
        pass

    @staticmethod
    def findDay(date):
        day = dt.datetime.strptime(date, '%Y-%m-%d %H').weekday()
        return calendar.day_name[day]