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
from sklearn import preprocessing


GEO_COORDS = {
    'NYISO':
        {
            'lat': '40.7128',
            'lon': '-73.935242'
        },
    'ISONE':
        {
            'lat': '42.3601',
            'lon': '-71.0589'
        },
    'CAISO':
        {
            'lat': '34.0522',
            'lon': '-118.2437'
        },
    'ERCOT':
        {
            'lat': '29.7604',
            'lon': '-95.3698'
        },
    'PJM':
        {
            'lat': '39.9526',
            'lon': '-75.1652'
        },
}


BASE_URL = 'https://api.darksky.net/forecast'
EXCLUDE = 'flags, minutely, daily, alerts'
API_KEY = os.environ['DARKSKY_KEY']

LOAD_COLS = ['load_MW', 'timestamp']
EASTERN_TZ = 'US/Eastern'

US_HOLIDAYS = holidays.UnitedStates()
CATEGORICAL_FEATURES = ['weekday', 'hour_of_day', 'holiday']
NUMERICAL_FEATURES = ['temperature', 'load (t-24)']


class LoadCollector:

    def __init__(self, iso: str, start_date: str, end_date: str):
        self.start = start_date
        self.end = end_date
        self.iso = self._set_iso(iso)
        self.holidays = holidays.UnitedStates()
        self.load = self.get_historical_load()
        self.model_input = None
        self.lat = GEO_COORDS[iso]['lat']
        self.lon = GEO_COORDS[iso]['lon']
        self.weather_url = f'{BASE_URL}/{API_KEY}/{self.lat},{self.lon},'

    def get_historical_load(self) -> pd.DataFrame:
        load = pd.DataFrame(
            self.iso.get_load(
                latest=False,
                yesterday=False,
                start_at=self.start,
                end_at=self.end)
            )[LOAD_COLS].set_index('timestamp')
        load.index = load.index.tz_convert(EASTERN_TZ)
        return load.resample('H').mean()

    def engineer_features(self):
        temperatures = dict()
        holiday_bool = dict()
        weekdays = dict()
        for date, _ in self.load.iterrows():
            temperatures[date] = self._get_temperature(date)
            holiday_bool[date] = self._check_for_holiday(date)
        self.load['weekday'] = self.load.index.dayofweek
        self.load['hour_of_day'] = self.load.index.hour
        self.load['temperature'] = self.load.index.map(temperatures)
        self.load['holiday'] = self.load.index.map(holiday_bool)
        self.load['load (t-24)'] = self.load.load_MW.shift(24)

    def build_model_input(self):
        self.model_input = self.dummify_categorical_features(self.load.copy())
        self.model_input = self.standardize_numerical_features(self.model_input)

    @staticmethod
    def _set_iso(iso_name: str):
        if iso_name == 'NYISO':
            iso_engine = client_factory('NYISO')
        elif iso_name == 'ISONE':
            iso_engine = client_factory('ISONE')
        elif iso_name == 'CAISO':
            iso_engine = client_factory('CAISO')
        elif iso_name == 'ERCOT':
            iso_engine = client_factory('ERCOT')
        elif iso_name == 'PJM':
            iso_engine = client_factory('PJM')
        else:
            print(f'Peaky Finders does not support {iso_name} yet!')
        return iso_engine

    def _get_temperature(self, date):
        date_input = date.strftime('%s')
        full_url = f'{self.weather_url}{date_input}?exclude={EXCLUDE}'
        response = requests.get(full_url)
        if response.status_code == 200:
            print(response.status_code)
        else: 
            raise ValueError(f'Error getting data from DarkSky API: '
                            f'Response Code {response.status_code}')
        info = response.json()
        current_info = info['currently']
        return current_info['temperature']

    @staticmethod
    def _check_for_holiday(day):
        if day in US_HOLIDAYS:
            return True
        else:
            return False

    @staticmethod
    def dummify_categorical_features(load_df: pd.DataFrame):
        for feature in CATEGORICAL_FEATURES:
            dummies = pd.get_dummies(load_df[feature], prefix=feature, drop_first=True)
            load_df = load_df.drop(feature, axis=1)
            load_df = pd.concat([load_df, dummies], axis=1)
            load_df = load_df.dropna(axis=0, how='any')
        return load_df

    @staticmethod
    def standardize_numerical_features(load_df: pd.DataFrame):
        z_scaler = preprocessing.StandardScaler()
        load_df[NUMERICAL_FEATURES] = z_scaler.fit_transform(
            load_df[NUMERICAL_FEATURES])
        return load_df
