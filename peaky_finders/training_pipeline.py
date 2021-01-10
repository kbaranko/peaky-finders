import pandas as pd

from peaky_finders.data_acquisition.nyiso import NYISO


class Pipeline:

    def __init__(self, iso: str, model: str, start: str, end: str):
        """
        Args:
            iso: the iso to forecast ('nyiso', 'ercot', etc.)
            model: logistic regression 'log' or xgboost     
        """
        self.start = start
        self.end = end
        self.iso = self._set_iso(iso, start, end)
        self.model = model

    def phase_one(self):
        """Data acquisition"""
        # nyiso = NYISO('01-01-2020', '01-01-2021')
        output = pd.DataFrame(self.iso.get_historical_load())
        import pdb; pdb.set_trace()

    def phase_two(self):
        """Feature engineering """

    def phase_three(self):
        """Model training """

    def execute(self):
        self.phase_one()

    @staticmethod
    def _set_iso(iso: str, start: str, end: str):
        if iso == 'nyiso':
            return NYISO(start, end)
        else:
            print(f'Cannot train model for ISO {iso}')


# if __name__ == "__main__":
#     cli()

pipeline = Pipeline(iso='nyiso', model='load_forecast', start='01-01-2020', end='01-03-2020')
pipeline.execute()