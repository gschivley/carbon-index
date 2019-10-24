"""
This module is used as a single place to load previously transformed datasets

"""

import pandas as pd

from src.params import DATA_DATE, DATA_PATHS
from src.util import add_facility_location, rename_cols

EF_PATH = DATA_PATHS['inputs'] / 'Final emission factors.csv'
EF = pd.read_csv(EF_PATH, index_col=0)

location_path = DATA_PATHS['transformed_data'] / 'Facility locations_RF.csv'
LOCATION_LABELS = pd.read_csv(location_path)

FACILITY_PATH = (
    DATA_PATHS['eia_compiled']
    / f'facility_gen_fuel_data_{DATA_DATE}.parquet'
)
FACILITY_DF = pd.read_parquet(FACILITY_PATH)


epa_path = (
    DATA_PATHS['epa_emissions']
    / f'epa_emissions_{DATA_DATE}.parquet'
)
EPA_DF = pd.read_parquet(epa_path)
EPA_DF = add_facility_location(EPA_DF, LOCATION_LABELS, labels=['state', 'year'])

STATE_PATH = (
    DATA_PATHS['eia_compiled']
    / f'state_gen_fuel_data_{DATA_DATE}.parquet'
)
EIA_TOTALS = pd.read_parquet(STATE_PATH)
EIA_TOTALS.reset_index(inplace=True)
rename_cols(EIA_TOTALS)
# Remove fuel categories that are duplicated with other categories
EIA_TOTALS = EIA_TOTALS.loc[~EIA_TOTALS['type'].isin(['SPV', 'AOR', 'TSN'])]
