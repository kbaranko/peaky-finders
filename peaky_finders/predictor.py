import datetime as dt
from datetime import timedelta
import os
import pickle
from typing import Dict, Tuple

import pandas as pd
import pytz, datetime
from timezonefinderL import TimezoneFinder

from peaky_finders.data_acquisition.train_model import (
    LoadCollector, GEO_COORDS, CATEGORICAL_FEATURES, MONTH_TO_SEASON)
from peaky_finders.training_pipeline import MODEL_OUTPUT_DIR


ISO_LIST = ['NYISO', 'ISONE', 'CAISO', 'PJM', 'MISO']

PEAK_DATA = {
    'NYISO': 'NYISO_01-01-2018_01-01-2020.csv',
    'PJM': 'PJM_01-01-2019_07-28-2020.csv',
    'ISONE': 'ISONE_01-01-2019_07-28-2020.csv',
    'MISO': 'MISO_01-01-2019_07-28-2020.csv',
}

PEAK_DATA_PATH = os.path.join(
    os.path.dirname(__file__), 'training_data')


tz_finder = TimezoneFinder()

class Predictor:

    def __init__(self, iso_name: str) -> None:
        self.iso_name = iso_name
        self.load_collector: LoadCollector = None

    def get_load(self):
        begin = (dt.datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d %H')
        end = pd.datetime.today().strftime('%Y-%m-%d %H')
        self.load_collector = LoadCollector(self.iso_name, begin, end)

    def featurize(self):
        self.load_collector.engineer_features()

    def add_future(self, load: pd.Series) -> pd.Series:
        future = pd.date_range(
            start=load.index[-1],
            end=(load.index[-1] + timedelta(days=1)),
            freq='H').to_frame(name='load_MW')
        tz_finder = TimezoneFinder()
        lon = float(GEO_COORDS[self.iso_name]['lon'])
        lat = float(GEO_COORDS[self.iso_name]['lat'])
        tz_name = tz_finder.timezone_at(lng=lon, lat=lat)
        future['load_MW'] = None
        future.index = future.index.tz_convert(tz_name)
        return future

    def prepare_predictions(self):
        self.get_load()
        load = self.load_collector.load
        future = self.add_future(load)
        all_load = pd.concat([load, future])
        self.load_collector.load = all_load
        self.load_collector.engineer_features()
        model_input = self.load_collector.load.copy()
        for feature in CATEGORICAL_FEATURES:
            dummies = pd.get_dummies(model_input[feature], prefix=feature, drop_first=True)
            model_input = model_input.drop(feature, axis=1)
            model_input = pd.concat([model_input, dummies], axis=1)
        return model_input

    def predict_load(self, model_input: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        model_path = os.path.join(MODEL_OUTPUT_DIR, (f'xg_boost_{self.iso_name}_load_model.pkl'))
        xgb = pickle.load(open(model_path, "rb"))
        if 'holiday_True' not in model_input.columns:
            model_input['holiday_True'] = 0
        X = model_input.drop('load_MW', axis=1).astype(float).dropna()
        predictions = xgb.predict(X)
        X['predicted_load'] = predictions
        return model_input['load_MW'].drop_duplicates(), X['predicted_load']


def predict_all(iso_list: list) -> Tuple[Dict[str, pd.DataFrame]]:
    historical_load = {}
    predicted_load = {}
    for iso in iso_list:
        predictor = Predictor(iso)
        model_input = predictor.prepare_predictions()
        load, predictions = predictor.predict_load(model_input)
        historical_load[iso] = load
        predicted_load[iso] = predictions
    return historical_load, predicted_load

def get_peak_data(iso_list: list) -> Tuple[Dict[str, pd.DataFrame]]:
    peak_data = {}
    for iso in iso_list:
        iso_data = pd.read_csv(os.path.join(PEAK_DATA_PATH, PEAK_DATA[iso]), parse_dates=['timestamp'])
        iso_data['timestamp'] = iso_data['timestamp'].apply(lambda x: x.astimezone(pytz.utc))
        tz_name = tz_finder.timezone_at(lng=float(GEO_COORDS[iso]['lon']), lat=float(GEO_COORDS[iso]['lat']))
        iso_data.index = pd.DatetimeIndex(iso_data['timestamp'])
        iso_data.index = iso_data.index.tz_convert(tz_name)
        basics = iso_data[['load_MW', 'temperature']]
        basics['weekday'] = basics.index.day_name()
        basics['season'] = basics.index.month.map(MONTH_TO_SEASON)
        peak_data[iso] = basics
    return peak_data
