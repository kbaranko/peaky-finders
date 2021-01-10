import calendar
import datetime as dt
from datetime import timedelta
import holidays
import math

import json
import numpy as np
import pandas as pd
import pickle
from pyiso import client_factory
import pyiso
# from pyiso import client_factory
import requests


LAT = '40.7128'
LON = '-73.935242'
BASE_URL = 'https://api.darksky.net/forecast'
EXCLUDE = 'flags, minutely, daily, alerts'
# api_key = config.api_key
# FULL_DARKSKY_URL = f'{BASE_URL}/{API_KEY}/{LAT},{LON}?exclude={EXCLUDE}'

class NYISO:

    def __init__(self, start_date: str, end_date: str):
        self.start = start_date
        self.end = end_date
        self.holidays = holidays.UnitedStates()


    def get_temperature(self) -> pd.DataFrame:
        weather_response = requests.get(FULL_DARKSKY_URL)
    
    
    def get_historical_load(self) -> pd.DataFrame:
        nyiso = client_factory('NYISO', timeout_seconds=60)
        return nyiso.get_load(latest=False, yesterday=False, start_at=self.start, end_at=self.end)




    @staticmethod
    def findDay(date):
        day = dt.datetime.strptime(date, '%Y-%m-%d %H').weekday()
        return calendar.day_name[day]