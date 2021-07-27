ISO_LIST = ['NYISO', 'ISONE', 'PJM', 'MISO', 'CAISO']

FORECASTS_PATH = 'https://raw.githubusercontent.com/kbaranko/peaky-finders/master/peaky_finders/forecasts'
"""Github forecast csv files."""

PEAKS_PATH = 'https://raw.githubusercontent.com/kbaranko/peaky-finders/master/peaky_finders/historical_peaks'
"""Github path to peaks csv files """


"""NYISO layout constants."""
NYISO_FULL_NAME = 'New York Independent System Operator (NYISO)'
NYISO_DESCRIPTION = '''
    "The NYISO is the New York Independent System Operator — the organization
    responsible for managing New York’s electric grid and its competitive
    wholesale electric marketplace." For more information, visit
    https://www.nyiso.com/.
'''
NYISO_MODEL_DESCRIPTION = '''
    The NYISO forecasting model was trained on historical load and weather data
    from 2018-2021. Temperature readings are from New York City.
'''
NYISO_MAE = 347.62


"""PJM layout constants"""
PJM_FULL_NAME = 'Pennsylvania, Jersey, Maryland Power Pool (PJM)'
PJM_DESCRIPTION = '''
    "PJM is a regional transmission organization (RTO) that coordinates the
    movement of wholesale electricity in all or parts of 13 states and
    the District of Columbia." For more information, visit https://www.pjm.com.
'''
PJM_MODEL_DESCRIPTION = '''
    The PJM forecasting model was trained on historical load and weather data
    from 2018-2021. Temperature readings are from Philadelphia.
'''
PJM_MAE = 2886.66
