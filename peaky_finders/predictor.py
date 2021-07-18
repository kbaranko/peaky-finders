import argparse
import os
import pickle
from typing import Dict

import pandas as pd
from timezonefinderL import TimezoneFinder

from peaky_finders.data_acquisition.train_model import (
    LoadCollector, CATEGORICAL_FEATURES
)
from peaky_finders.training_pipeline import MODEL_OUTPUT_DIR


FORECAST_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), 'forecasts')


tz_finder = TimezoneFinder()


def predict_load(iso_name: str, start: str, end: str):
    load_collector = LoadCollector(iso_name, start, end)
    load_collector.engineer_features()
    load = load_collector.load
    X = engineer_features(load_collector.load.copy())
    xgb = load_model(iso_name)
    X['predicted_load'] = xgb.predict(X[xgb.get_booster().feature_names])
    return pd.concat(
        [load['load_MW'], X['predicted_load'], X['temperature']],
        axis=1).dropna()


def engineer_features(model_input: pd.DataFrame):
    for feature in CATEGORICAL_FEATURES:
        dummies = pd.get_dummies(
            model_input[feature], prefix=feature, drop_first=True
        )
        model_input = model_input.drop(feature, axis=1)
        model_input = pd.concat([model_input, dummies], axis=1)
    if 'holiday_True' not in model_input.columns:
        model_input['holiday_True'] = 0
    X = model_input.drop('load_MW', axis=1).astype(float).dropna()
    weekday_cols = [f'weekday_{i + 1}' for i in range(0,6)]
    if len(set(weekday_cols) - set(X.columns)) > 0:
        for col in list(set(weekday_cols) - set(X.columns)):
            X[col] = 0
    return X


def load_model(iso_name: str):
    model_path = os.path.join(
        MODEL_OUTPUT_DIR,
        f'xg_boost_{iso_name}_load_model.pkl'
    )
    return pickle.load(open(model_path, "rb"))


def save_forecasts(iso_name: str, predictions_df: pd.DataFrame) -> None:
    filename = f'{iso_name}_forecasts.csv'
    predictions_df.to_csv(os.path.join(FORECAST_OUTPUT_DIR, filename))


def predict_all(iso_list: list, start: str, end: str) -> Dict[str, pd.DataFrame]:
    load_dict = {}
    for iso in iso_list:
        load_dict[iso] = predict_load(
            iso_name=iso,
            start=start,
            end=end,
        )
    return load_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--iso',
        default='NYISO',
        type=str,
        help='Select ISO for model prediction.'
    )
    parser.add_argument(
        '-s', '--start_date',
        type=str,
        help='Start date range for model training (Ex: 02-01-2021)')
    parser.add_argument(
        '-e', '--end_date',
        type=str,
        help='End date range for model training (Ex: 02-01-2021)')
    parser.add_argument(
        '-mo', '--save_predictions',
        type=bool,
        help='Save predictions as csv file.'
    )
    args = parser.parse_args()
    load = predict_load(
        iso_name=args.iso,
        start=args.start_date,
        end=args.end_date
    )
    print(load)
    if args.save_predictions:
        save_forecasts(iso_name=args.iso, predictions_df=load)
