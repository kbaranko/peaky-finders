import holidays
import os
from typing import Optional, Tuple

from dateutil.relativedelta import relativedelta
import pandas as pd
from pyiso import client_factory
from pyiso.eia_esod import EIAClient
import requests
from timezonefinderL import TimezoneFinder


GEO_COORDS = {
    'NYISO':
        {
            'lat': '40.7128',
            'lon': '-73.935242'
        },
    # NYC Coords (Big Apple)
    'ISONE':
        {
            'lat': '42.3601',
            'lon': '-71.0589'
        },
    # Boston Coords (Beantown)
    'CAISO':
        {
            'lat': '34.0522',
            'lon': '-118.2437'
        },
    # LA Coords (City of Angles)
    'PJM':
        {
            'lat': '39.9526',
            'lon': '-75.1652'
        },
    # Philly Coords (City of Brotherly Love)
    'MISO':
        {
            'lat': '44.9778',
            'lon': '-93.2650',
        },
    # Minneapolis Coords (Twin Cities)
}

MONTH_TO_SEASON = {
    1: 'Winter',
    2: 'Winter',
    3: 'Spring',
    4: 'Spring',
    5: 'Spring',
    6: 'Summer',
    7: 'Summer',
    8: 'Summer',
    9: 'Fall',
    10: 'Fall',
    11: 'Fall',
    12: 'Winter'
}


BASE_URL = 'https://api.darksky.net/forecast'
EXCLUDE = 'flags, minutely, daily, alerts'

LOAD_COLS = ['load_MW', 'timestamp']
EASTERN_TZ = 'US/Eastern'

US_HOLIDAYS = holidays.UnitedStates()
CATEGORICAL_FEATURES = ['weekday', 'hour_of_day', 'holiday']
NUMERICAL_FEATURES = ['temperature', 'load (t-24)']

tz_finder = TimezoneFinder()


class LoadCollector:

    def __init__(self, iso: str, start_date: str, end_date: str):
        """
        Methods to acquire data and engineer weather and temporal features

        Args:
            iso: the iso to forecast ('NYISO', 'ISONE', etc.)
            start_date: the start date of the training & weather data to fetch
            end_date: the end date of the training & weather data to fetch
        """
        self.start_date = start_date
        self.end_date = end_date
        self.iso_name = iso
        self.lat = GEO_COORDS[iso]['lat']
        self.lon = GEO_COORDS[iso]['lon']
        self.iso = self._set_iso(iso)
        self.holidays = holidays.UnitedStates()
        self.load = self.get_historical_load()
        self.model_input = None

    def get_historical_load(self) -> pd.DataFrame:
        """
        Fetches historical load data for the given ISO using WattTime's pyiso
        library. Due to bugs, different ISOs need to use different types of API
        requests. https://pyiso.readthedocs.io/en/latest/intro.html
        """
        if self.iso_name == 'CAISO':
            load = self.get_caiso_load()
        elif self.iso_name == 'MISO' or self.iso_name == 'PJM':
            load = self._get_eia_load()
        else:
            load = pd.DataFrame(
                self.iso.get_load(
                    latest=False,
                    yesterday=False,
                    start_at=self.start_date,
                    end_at=self.end_date)
            )[LOAD_COLS].set_index('timestamp')
        tz_name = tz_finder.timezone_at(
            lng=float(self.lon), lat=float(self.lat)
        )
        load.index = load.index.tz_convert(tz_name)
        return load.resample('H').mean()

    def get_historical_peak_load(self) -> pd.DataFrame:
        """

        """
        daily_peak = self.load.resample('D').max()
        holiday_bool = dict()
        for date, _ in daily_peak.iterrows():
            holiday_bool[date] = self._check_for_holiday(date)
        daily_peak['month'] = daily_peak.index.month_name()
        daily_peak['season'] = daily_peak.index.month.map(MONTH_TO_SEASON)
        daily_peak['weekday'] = daily_peak.index.day_name()
        daily_peak['holiday'] = daily_peak.index.map(holiday_bool)
        return daily_peak

    def _get_eia_load(self) -> pd.DataFrame:
        """
        Uses pyiso EIAClient object to fetch historical load data.
        """
        load = pd.DataFrame(
                self.iso.get_load(
                    latest=True,
                    yesterday=False,
                    start_at=self.start_date,
                    end_at=self.end_date)
            )
        load = load.iloc[::-1]
        return load[LOAD_COLS].set_index('timestamp')

    def get_caiso_load(self) -> pd.DataFrame:
        """
        CAISO EIAClient object requires making monthly requests and therefore
        needs some special preprocessing.
        """
        start_month = pd.Timestamp(self.start_date).month
        end_month = pd.Timestamp(self.end_date).month
        if start_month == end_month:
            months = [pd.Timestamp(self.start_date)]
        else:
            months = pd.date_range(
                self.start_date, self.end_date, freq='MS'
            ).tolist()
        monthly_load = []
        for month in months:
            start, end = self.get_month_day_range(month)
            load = pd.DataFrame(
                self.iso.get_load(
                    latest=False,
                    yesterday=False,
                    start_at=start,
                    end_at=end)
            )[LOAD_COLS].set_index('timestamp')
            monthly_load.append(load)
        return pd.concat(monthly_load)

    @staticmethod
    def get_month_day_range(date: pd.Timestamp) -> Tuple[str, str]:
        """
        Returns the start and end date for the month of 'date'.
        """
        last_day = date + relativedelta(day=1, months=+1, days=-1)
        first_day = date + relativedelta(day=1)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')

    def engineer_features(self):
        """
        For a timeseries of load data, build temperature and temporal features.
        Does not return a value but expands self.load attribute df.
        """
        temperatures = dict()
        holiday_bool = dict()
        for date, _ in self.load.iterrows():
            temperatures[date] = self._get_temperature(date)
            holiday_bool[date] = self._check_for_holiday(date)
        self.load['weekday'] = self.load.index.dayofweek
        self.load['hour_of_day'] = self.load.index.hour
        self.load['temperature'] = self.load.index.map(temperatures)
        self.load['holiday'] = self.load.index.map(holiday_bool)
        self.load['load (t-24)'] = self.load.load_MW.shift(24)

    def engineer_features_lite(self, weather_dict: dict):
        """
        For a time series of load data and time series of weather data, build
        temperature and temporal features. Does not return a value but expands
        self.load attribute df
        """
        holiday_bool = dict()
        for date, _ in self.load.iterrows():
            holiday_bool[date] = self._check_for_holiday(date)
        self.load['weekday'] = self.load.index.dayofweek
        self.load['hour_of_day'] = self.load.index.hour
        self.load['temperature'] = self.load.index.map(pd.Series(weather_dict))
        self.load['holiday'] = self.load.index.map(holiday_bool)
        self.load['load (t-24)'] = self.load.load_MW.shift(24)

    def build_model_input(self):
        """
        One-hot encode categorial features and drop null values. Sets the
        model_input attribute as a feature matrix df.
        """
        featurized_df = self._dummify_categorical_features(self.load.copy())
        self.model_input = featurized_df[featurized_df.notna()]

    @staticmethod
    def _set_iso(iso_name: str):
        """
        Parses iso name and instantiates the correct pyiso object required to
        fetch historical load data.
        """
        if iso_name == 'NYISO':
            iso_engine = client_factory('NYISO')
        elif iso_name == 'ISONE':
            iso_engine = client_factory('ISONE', timeout_seconds=60)
        elif iso_name == 'CAISO':
            iso_engine = client_factory('CAISO')
        elif iso_name == 'ERCOT':
            iso_engine = EIAClient(timeout_seconds=60)
            iso_engine.BA = 'ERCOT'
        elif iso_name == 'PJM':
            iso_engine = EIAClient(timeout_seconds=60)
            iso_engine.BA = 'PJM'
        elif iso_name == 'MISO':
            iso_engine = EIAClient(timeout_seconds=60)
            iso_engine.BA = 'MISO'
        else:
            raise ValueError(f'Peaky Finders does not support {iso_name}')
        return iso_engine

    def _get_temperature(self, date: pd.Timestamp) -> Optional[float or None]:
        """
        Gets a temperature reading for a given date and time (hourly).
        """
        date_input = date.strftime('%s')
        API_KEY = os.environ['DARKSKY_KEY']
        weather_url = f'{BASE_URL}/{API_KEY}/{self.lat},{self.lon},'
        full_url = f'{weather_url}{date_input}?exclude={EXCLUDE}'
        response = requests.get(full_url)
        if response.status_code == 200:
            print(response.status_code)
        else:
            raise ValueError(f'Error getting data from DarkSky API: '
                             f'Response Code {response.status_code}')
        info = response.json()
        current_info = info['currently']
        try:
            temp = current_info['temperature']
        except KeyError:
            temp = None
        return temp

    @staticmethod
    def _check_for_holiday(day: pd.Timestamp) -> bool:
        """
        Determine whether a given day was a holiday.
        """
        if day in US_HOLIDAYS:
            return True
        else:
            return False

    @staticmethod
    def _dummify_categorical_features(load_df: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encode the load df columns that contain categorical features.
        """
        for feature in CATEGORICAL_FEATURES:
            dummies = pd.get_dummies(
                load_df[feature], prefix=feature, drop_first=True
            )
            load_df = load_df.drop(feature, axis=1)
            load_df = pd.concat([load_df, dummies], axis=1)
            load_df = load_df.dropna(axis=0, how='any')
        return load_df
