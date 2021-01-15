import argparse
import pickle

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from peaky_finders.data_acquisition.nyiso import NYISO


class Pipeline:

    def __init__(self, iso: str, model: str, start_date: str, end_date: str, save_model_input: bool, save_model_output: bool):
        """
        Args:
            iso: the iso to forecast ('nyiso', 'ercot', etc.)
            model: logistic regression 'log' or xgboost     
        """
        self.iso_name = iso
        self.model = model
        self.start = start_date
        self.end = end_date
        self.iso = None

        self.save_model_input = save_model_input
        self.save_model_output = save_model_output

    def phase_one(self):
        """Data acquisition"""
        self.iso = self._set_iso(self.iso_name, self.start, self.end)

    def phase_two(self):
        """Feature engineering + model preparation """
        self.iso.engineer_features()
        self.iso.build_model_input()
        import pdb; pdb.set_trace()
        if self.save_model_input:
            self.iso.model_input.to_csv(f'/peaky_finders/training_data/{self.iso_name}_{self.start}_{self.end}.csv')

    def phase_three(self):
        """Model training & serialization"""
        y = self.iso.model_input['load_MW']
        X = self.iso.model_input.drop('load_MW', axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        reg = xgb.XGBRegressor()
        reg.fit(X_train, y_train)
        training_preds = reg.predict(X_train)
        val_preds = reg.predict(X_test)
        print('Mean Absolute Error:', mean_absolute_error(y_test, val_preds))  
        print('Root Mean Squared Error:', np.sqrt(mean_squared_error(y_test, val_preds)))
        if self.save_model_output:
            model_name = f'/peaky_finders/models/xg_boost_{self.iso_name}_load_model.pkl'
            pickle.dump(reg, open(model_name, "wb"))

    def execute(self):
        self.phase_one()
        self.phase_two()
        self.phase_three()

    @staticmethod
    def _set_iso(iso: str, start: str, end: str):
        if iso == 'NYISO':
            return NYISO(start, end)
        else:
            print(f'Cannot train model for ISO {iso}')


# python peaky_finders/training_pipeline.py --iso NYISO --model xgboost --start_date 05-01-2020 --end_date 05-28-2020 --save_model_input False --save_model_output False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--iso',
        default='NYISO',
        type=str,
        help='Select ISO for model prediction.'
    )
    parser.add_argument(
        '-m', '--model',
        type=str,
        help='Model to train (xgboost for forecast, log regression for peak.'
    )
    parser.add_argument(
        '-s', '--start_date',
        type=str,
        help='Start date range for model training.')
    parser.add_argument(
        '-e', '--end_date',
        type=str,
        help='End date range for model training.')
    parser.add_argument(
        '-mi', '--save_model_input',
        type=bool,
        help='Save model input (w/ features and scaled.')
    parser.add_argument(
        '-mo', '--save_model_output',
        type=bool,
        help='Save trained model as pickle file.'
    )

    args = parser.parse_args()
    pipeline = Pipeline(
        iso=args.iso, 
        model=args.model, 
        start_date=args.start_date, 
        end_date=args.end_date, 
        save_model_input=args.save_model_input, 
        save_model_output=args.save_model_output
    )
    pipeline.execute()

