import pandas as pd

from peaky_finders.data_acquisition.nyiso import NYISO

[['load_MW', 'timestamp']]

class Pipeline:

    def __init__(self, iso: str, model: str, start: str, end: str):
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

    def phase_one(self):
        """Data acquisition"""
        # nyiso = NYISO('01-01-2020', '01-01-2021')
        self.iso = self._set_iso(self.iso_name, self.start, self.end)

    def phase_two(self):
        """Feature engineering """
        self.iso.engineer_weather_features()
        import pdb; pdb.set_trace()
        self.iso.engineer_datetime_features()

    def phase_three(self):
        """Model training """

    def execute(self):
        self.phase_one()
        self.phase_two()

    @staticmethod
    def _set_iso(iso: str, start: str, end: str):
        if iso == 'nyiso':
            return NYISO(start, end)
        else:
            print(f'Cannot train model for ISO {iso}')


if __name__ == "__main__":
    pipeline = Pipeline(iso='nyiso', model='load_forecast', start='06-01-2020', end='06-02-2020')
    pipeline.execute()

