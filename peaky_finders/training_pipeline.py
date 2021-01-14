import pickle

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from peaky_finders.data_acquisition.nyiso import NYISO


class Pipeline:

    def __init__(self, iso: str, model: str, start: str, end: str, save_model_input: bool = False):
        """
        Args:
            iso: the iso to forecast ('nyiso', 'ercot', etc.)
            model: logistic regression 'log' or xgboost     
        """
        self.start = start
        self.end = end
        self.iso_name = iso
        self.iso = None
        self.model = model
        self.save_model_input = save_model_input

    def phase_one(self):
        """Data acquisition"""
        self.iso = self._set_iso(self.iso_name, self.start, self.end)

    def phase_two(self):
        """Feature engineering + model preparation """
        self.iso.engineer_features()
        self.iso.build_model_input()
        if self.save_model_input:
            self.iso.model_input.to_csv(f'training_data/{self.iso_name}_{self.start}_{self.end}.csv')

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
        if self.save_model:
            model_name = f'xg_boost_{self.iso.name}_load_model.pkl'
            pickle.dump(reg, open(file_name, "wb"))

    def execute(self):
        self.phase_one()
        self.phase_two()
        self.phase_three()

    @staticmethod
    def _set_iso(iso: str, start: str, end: str):
        if iso == 'nyiso':
            return NYISO(start, end)
        else:
            print(f'Cannot train model for ISO {iso}')


if __name__ == "__main__":
    pipeline = Pipeline(iso='nyiso', model='load_forecast', start='05-01-2020', end='05-28-2020')
    pipeline.execute()

