"""
This module is used as a single place to load previously transformed datasets

"""

import pandas as pd

from src.params import DATA_DATE, DATA_PATHS
from src.util import add_facility_location, rename_cols

def load_ef():
    EF_PATH = DATA_PATHS['inputs'] / 'Final emission factors.csv'
    EF = pd.read_csv(EF_PATH, index_col=0)
    return EF


def load_location_labels():
    location_path = DATA_PATHS['transformed_data'] / "facility_labels" / 'Facility locations_RF.csv'
    LOCATION_LABELS = pd.read_csv(location_path)
    return LOCATION_LABELS


def load_facility_gen_fuel_data():
    FACILITY_PATH = (
        DATA_PATHS['eia_compiled']
        / f'facility_gen_fuel_data_{DATA_DATE}.parquet'
    )
    FACILITY_DF = pd.read_parquet(FACILITY_PATH)
    return FACILITY_DF




def load_epa_data():
    epa_path = (
        DATA_PATHS['epa_emissions']
        / f'epa_emissions_{DATA_DATE}.parquet'
    )
    EPA_DF = pd.read_parquet(epa_path)
    LOCATION_LABELS = load_location_labels()
    LOCATION_LABELS = LOCATION_LABELS.drop_duplicates()
    EPA_DF = add_facility_location(EPA_DF, LOCATION_LABELS, labels=['state', 'year'])
    return EPA_DF


def load_eia_state_gen_data():
    STATE_PATH = (
        DATA_PATHS['eia_compiled']
        / f'state_gen_fuel_data_{DATA_DATE}.parquet'
    )
    EIA_TOTALS = pd.read_parquet(STATE_PATH)
    EIA_TOTALS.reset_index(inplace=True)
    rename_cols(EIA_TOTALS)
    # Remove fuel categories that are duplicated with other categories
    EIA_TOTALS = EIA_TOTALS.loc[~EIA_TOTALS['type'].isin(['SPV', 'AOR', 'TSN'])]
    return EIA_TOTALS