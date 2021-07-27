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


"""MISO layout constants"""
MISO_FULL_NAME = 'Midcontinent Independent System Operator (MISO)'
MISO_DESCRIPTION = '''
    "Midcontinent Independent System Operator (MISO) is an independent,
    not-for-profit organization that delivers safe, cost-effective 
    electric power across 15 U.S. states and the Canadian province of 
    Manitoba." For more information,
    visit www.misoenergy.org.
'''
MISO_MODEL_DESCRIPTION = '''
    The MISO forecasting model was trained on historical load and weather data
    from 2018-2021. Temperature readings are from Minneapolis.
'''
MISO_MAE = 2382.66


"""ISONE layout constants"""
ISONE_FULL_NAME = 'Independent System Operator of New England (ISONE)'
ISONE_DESCRIPTION = '''
    ISONE is the "independent, not-for-profit corporation responsible 
    for keeping electricity flowing across the six New England states 
    and ensuring that the region has reliable, competitively priced 
    wholesale electricity today and into the future." For more information,
    visit www.iso-ne.com.
'''
ISONE_MODEL_DESCRIPTION = '''
    The ISONE model was trained on historical load and weather data
    from 2018-2021. Temperature readings are from Boston.
'''
ISONE_MAE = 522.43


"""CAISO layout constants"""
CAISO_FULL_NAME = 'California Independent System Operator (CAISO)'
CAISO_DESCRIPTION = '''
    "The California Independent System Operator (ISO) maintains 
    reliability on one of the largest and most modern power grids in 
    the world, and operates a transparent, accessible wholesale energy 
    market."  For more information,
    visit http://www.caiso.com/.
'''
CAISO_MODEL_DESCRIPTION = '''
    The CAISO forecasting model was trained on historical load and weather data
    from 2018-2021. Temperature readings were from Los Angeles.
'''
CAISO_MAE = 455.91
