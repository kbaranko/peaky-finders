import argparse
import os
import pickle

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from peaky_finders.data_acquisition.train_model import LoadCollector

PEAK_LOAD_DIR = os.path.join(
    os.path.dirname(__file__), 'historical_peaks')
"""Directory to hold peak load csv files."""

def get_historical_peaks(start_date: str, end_date: str, iso: str) -> pd.DataFrame:
    collector = LoadCollector(iso=iso, start_date=start_date, end_date=end_date)
    return collector.get_historical_peak_load()

def set_output_path(start_date: str, end_date: str, iso: str) -> str:
    return os.path.join(
        PEAK_LOAD_DIR, (f'{iso}_peak_load_{start_date}_{end_date}.csv')
    )


"""
CLI demo command:
python peaky_finders/peak_pipeline.py --iso NYISO --start_date 01-01-2019 --end_date 07-28-2020
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--iso',
        default='NYISO',
        type=str,
        help='Select ISO for historical load.'
    )
    parser.add_argument(
        '-s', '--start_date',
        type=str,
        help='Start date range for peak load selection.')
    parser.add_argument(
        '-e', '--end_date',
        type=str,
        help='End date range for peak load selection.')

    args = parser.parse_args()
    historical_peaks = get_historical_peaks(
        iso=args.iso,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    historical_peaks.to_csv(set_output_path(
        start_date=args.start_date,
        end_date=args.end_date,
        iso=args.iso)
    )

