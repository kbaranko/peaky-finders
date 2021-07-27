import os
from typing import Dict, List

import pandas as pd
import pytz
from timezonefinderL import TimezoneFinder

import peaky_finders.constants as c
from peaky_finders.data_acquisition.train_model import GEO_COORDS


PEAK_DATA_PATH = os.path.join(
    os.path.dirname(__file__), 'historical_peaks')

tz_finder = TimezoneFinder()


def get_forecasts(iso_list: List[str]):
    """
    Reads a csv of forecasted load, actual load, and temperature for each ISO
    and returns as a tz-aware pd.Series.
    """
    predictions = {}
    historical_load = {}
    temperature = {}
    for iso in iso_list:
        path = f'{c.FORECASTS_PATH}/{iso}_forecasts.csv'
        iso_data = pd.read_csv(path, parse_dates=['timestamp'])
        iso_data['timestamp'] = iso_data['timestamp'].apply(
            lambda x: x.astimezone(pytz.utc)
        )
        tz_name = tz_finder.timezone_at(
            lng=float(GEO_COORDS[iso]['lon']),
            lat=float(GEO_COORDS[iso]['lat'])
        )
        iso_data.index = pd.DatetimeIndex(iso_data['timestamp'])
        iso_data.index = iso_data.index.tz_convert(tz_name)
        historical_load[iso] = iso_data['load_MW']
        predictions[iso] = iso_data['predicted_load']
        temperature[iso] = iso_data['temperature']
    return predictions, historical_load, temperature


def create_load_duration(
    peak_data: Dict[str, pd.DataFrame]
) -> Dict[str, pd.Series]:
    """
    Creates a load duration curve for each ISO by sorting historical peak data.
    """
    load_duration_curves = {}
    for iso in c.ISO_LIST:
        load_duration_curves[iso] = pd.Series(
            peak_data[iso]['load_MW'].values
        ).sort_values(ascending=False)
    return load_duration_curves


def get_peak_data(iso_list: list) -> Dict[str, pd.DataFrame]:
    """
    Reads a csv of historical peak load data for the ISO list.
    """
    peak_data = {}
    for iso in iso_list:
        iso_data = pd.read_csv(
            f'{c.PEAKS_PATH}/{iso}_historical_peaks.csv',
            parse_dates=['timestamp']
        )
        iso_data['timestamp'] = iso_data['timestamp'].apply(
            lambda x: x.astimezone(pytz.utc)
        )
        tz_name = tz_finder.timezone_at(
            lng=float(GEO_COORDS[iso]['lon']),
            lat=float(GEO_COORDS[iso]['lat'])
        )
        iso_data.index = pd.DatetimeIndex(iso_data['timestamp'])
        iso_data.index = iso_data.index.tz_convert(tz_name)
        peak_data[iso] = iso_data
    return peak_data
