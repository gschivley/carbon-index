"""
Parameters and settings for the Power Sector Carbon Index
"""

from pathlib import Path
from src import __file__

# Set a unique identifier (e.g. date of analysis) for the results files
DATA_DATE = '2019-09-24'
FINAL_DATA_YEAR = 2019
LAST_ANNUAL_923_YEAR = 2018 # Most recent year of annual (full) 923 release
FINAL_DATA_QUARTER = 2
QUARTER_YEAR = f'{FINAL_DATA_YEAR} Q{FINAL_DATA_QUARTER}'

src_path = Path(__file__).parent
project_path = src_path.parent

DATA_PATHS = {}
DATA_PATHS['data'] = project_path / 'data'
DATA_PATHS['inputs'] = DATA_PATHS['data'] / 'inputs'
DATA_PATHS['raw_data'] = DATA_PATHS['data'] / 'raw_data'
DATA_PATHS['transformed_data'] = DATA_PATHS['data'] / 'transformed_data'
DATA_PATHS['eia923'] = DATA_PATHS['raw_data'] / 'eia923'
DATA_PATHS['eia860'] = DATA_PATHS['raw_data'] / 'eia860'
DATA_PATHS['eia860m'] = DATA_PATHS['raw_data'] / 'eia860m'
DATA_PATHS['eia_bulk'] = DATA_PATHS['raw_data'] / 'eia_bulk'
DATA_PATHS['nercregions'] = DATA_PATHS['raw_data'] / 'nercregions'
DATA_PATHS['eia_compiled'] = DATA_PATHS['transformed_data'] / 'eia_compiled'
DATA_PATHS['epa_emissions'] = DATA_PATHS['transformed_data'] / 'epa_emissions'
DATA_PATHS['nerc_extra'] = DATA_PATHS['transformed_data'] / 'nerc_extra'
DATA_PATHS['results'] = DATA_PATHS['data'] / 'results'
DATA_PATHS['web_files'] = project_path / 'web_files'

#################################################
# Matches of fuel categories
#################################################
STATE_FACILITY_FUELS = {
    "COW": ["SUB", "BIT", "LIG", "WC", "SC", "RC", "SGC"],
    "NG": ["NG"],
    "PEL": ["DFO", "RFO", "KER", "JF",
            "PG", "WO", "SGP"],
    "PC": ["PC"],
    "HYC": ["WAT"],
    "HPS": [],
    "GEO": ["GEO"],
    "NUC": ["NUC"],
    "OOG": ["BFG", "OG"],
    "OTH": ["OTH", "MSN", "MSW", "PUR", "TDF", "WH"],
    "SUN": ["SUN"],
    "DPV": [],
    "WAS": ["OBL", "OBS", "OBG", "MSB", "SLW", "LFG"],
    "WND": ["WND"],
    "WWW": ["WDL", "WDS", "AB", "BLQ"]
}

CUSTOM_FUELS = {
    "Coal": ["COW"],
    "Natural Gas": ["NG"],
    "Nuclear": ["NUC"],
    "Wind": ["WND"],
    "Solar": ["SUN", "DPV"],
    "Hydro": ["HYC"],
    "Other Renewables": ["GEO", "WAS", "WWW"],
    "Other": ["OOG", "PC", "PEL", "OTH", "HPS"]
}

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
    "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
    "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

NERCS = [
    'ASCC', 'SERC', 'SPP', 'WECC', 'NPCC',
    'RFC', 'FRCC', 'HICC', 'MRO', 'TRE',
]

# FTP path info for the EPA CEMS data
CEMS_BASE = 'newftp.epa.gov'
CEMS_EXT = '/dmdnload/emissions/daily/quarterly'
CEMS_YEARS = range(2001, FINAL_DATA_YEAR + 1)


# Emission factors for fuel combustion
# Fossil ef are zero for non-fossil fuels
FOSSIL_EF = {
    'BIT': 93.3,
    'DFO': 73.16,
    'GEO': 7.71,
    'JF': 70.9,
    'KER': 72.3,
    'LIG': 97.7,
    'MSW': 41.69,
    'NG': 53.07,
    'PC': 102.1,
    'PG': 63.07,
    'RC': 93.3,
    'RFO': 78.79,
    'SGC': 93.3,
    'SGP': 73.16,
    'SUB': 97.2,
    'TDF': 85.97,
    'WC': 93.3,
    'WO': 95.25,
    'BFG': 274.32,
    'MSN': 90.7,
    'SC': 93.3,
    'OG': 59.0,
    'AB': 0.0,
    'BLQ': 0.0,
    'LFG': 0.0,
    'MSB': 0.0,
    'NUC': 0.0,
    'OBG': 0.0,
    'OBL': 0.0,
    'OBS': 0.0,
    'OTH': 0.0,
    'PUR': 0.0,
    'SLW': 0.0,
    'SUN': 0.0,
    'WAT': 0.0,
    'WDL': 0.0,
    'WDS': 0.0,
    'WH': 0.0,
    'WND': 0.0
}

TOTAL_EF = {
    'BIT': 93.3,
    'DFO': 73.16,
    'GEO': 7.71,
    'JF': 70.9,
    'KER': 72.3,
    'LIG': 97.7,
    'MSW': 41.69,
    'NG': 53.07,
    'PC': 102.1,
    'PG': 63.07,
    'RC': 93.3,
    'RFO': 78.79,
    'SGC': 93.3,
    'SGP': 73.16,
    'SUB': 97.2,
    'TDF': 85.97,
    'WC': 93.3,
    'WO': 95.25,
    'BFG': 274.32,
    'MSN': 90.7,
    'SC': 93.3,
    'OG': 59.0,
    'AB': 118.17,
    'BLQ': 94.4,
    'LFG': 52.17,
    'MSB': 90.7,
    'NUC': 0.0,
    'OBG': 52.17,
    'OBL': 83.98,
    'OBS': 105.51,
    'OTH': 0.0,
    'PUR': 0.0,
    'SLW': 83.98,
    'SUN': 0.0,
    'WAT': 0.0,
    'WDL': 83.98,
    'WDS': 93.8,
    'WH': 0.0,
    'WND': 0.0
}

EIA_860_NERC_INFO = {
    2012: {'io': DATA_PATHS['eia860'] / 'eia8602012' / 'PlantY2012.xlsx',
           'skiprows': 0,
           'usecols': 'B,J'},
    2013: {'io': DATA_PATHS['eia860'] / 'eia8602013' / '2___Plant_Y2013.xlsx',
           'skiprows': 0,
           'usecols': 'C,L'},
    2014: {'io': DATA_PATHS['eia860'] / 'eia8602014' / '2___Plant_Y2014.xlsx',
           'skiprows': 0,
           'usecols': 'C,L'},
    2015: {'io': DATA_PATHS['eia860'] / 'eia8602015' / '2___Plant_Y2015.xlsx',
           'skiprows': 0,
           'usecols': 'C,L'},
    2016: {'io': DATA_PATHS['eia860'] / 'eia8602016' / '2___Plant_Y2016.xlsx',
           'skiprows': 0,
           'usecols': 'C,L'},
    2017: {'io': DATA_PATHS['eia860'] / 'eia8602017' / '2___Plant_Y2017.xlsx',
           'skiprows': 0,
           'usecols': 'C,L'},
}
