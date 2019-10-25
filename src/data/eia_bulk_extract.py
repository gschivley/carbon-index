"""
Extract facility and state-level data from the EIA bulk data file

"""

import json
import zipfile

import numpy as np
import pandas as pd
import requests
from joblib import Parallel, delayed
from src.util import add_quarter, rename_cols
from src.data.data_extraction import facility_line_to_df, state_line_to_df
from src.params import (
    DATA_DATE,
    DATA_PATHS,
    FOSSIL_EF,
    TOTAL_EF,
    STATES,
)

STATE_GEOS = ['USA-{}'.format(state) for state in STATES]


def download_ELEC(date=DATA_DATE):

    url = 'http://api.eia.gov/bulk/ELEC.zip'

    save_path = DATA_PATHS['eia_bulk'] / 'ELEC_{}.zip'.format(date)
    if not save_path.exists():
        print('Downloading EIA bulk electricity data')
        r = requests.get(url)
        output = open(save_path, 'wb')
        output.write(r.content)
        output.close()


def read_ELEC(date=DATA_DATE):

    print('Reading bulk data file')
    read_path = DATA_PATHS['eia_bulk'] / 'ELEC_{}.zip'.format(date)
    z = zipfile.ZipFile(read_path, 'r')
    with z.open('ELEC.txt') as f:
        raw_txt = f.readlines()

    return raw_txt


def calc_emissions_from_fuels(df):
    """
    Calculate CO2 emissions from fuel consumption and emission factors

    Parameters
    ----------
    df : dataframe
        A df with both total and electric-only fuel consumption values (mmbtu)

    Returns
    -------
    dataframe
        modified dataframe with new columns showing total and fossil CO2
        emissions for both total and electric-only fuel consumption
    """
    # Start with 0 emissions in all rows
    # For fuels where we have an emission factor,
    # replace 0 with the calculated value
    df['all fuel fossil CO2 (kg)'] = 0
    df['elec fuel fossil CO2 (kg)'] = 0
    df['all fuel total CO2 (kg)'] = 0
    df['elec fuel total CO2 (kg)'] = 0
    for fuel in TOTAL_EF.keys():
        # All fuel CO2 emissions
        df.loc[df['fuel'] == fuel, 'all fuel fossil CO2 (kg)'] = \
            df.loc[df['fuel'] == fuel, 'total fuel (mmbtu)'] * FOSSIL_EF[fuel]
        df.loc[df['fuel'] == fuel, 'all fuel total CO2 (kg)'] = \
            df.loc[df['fuel'] == fuel, 'total fuel (mmbtu)'] * TOTAL_EF[fuel]

        # Electric fuel CO2 emissions
        df.loc[df['fuel'] == fuel, 'elec fuel fossil CO2 (kg)'] = \
            df.loc[df['fuel'] == fuel, 'elec fuel (mmbtu)'] * FOSSIL_EF[fuel]
        df.loc[df['fuel'] == fuel, 'elec fuel total CO2 (kg)'] = \
            df.loc[df['fuel'] == fuel, 'elec fuel (mmbtu)'] * TOTAL_EF[fuel]

    # set all negative value to zero
    # Fossil CO2
    df.loc[~(df['all fuel fossil CO2 (kg)'] >= 0),
           'all fuel fossil CO2 (kg)'] = 0
    df.loc[~(df['elec fuel fossil CO2 (kg)'] >= 0),
           'elec fuel fossil CO2 (kg)'] = 0
    # Total CO2
    df.loc[~(df['all fuel total CO2 (kg)'] >= 0),
           'all fuel total CO2 (kg)'] = 0
    df.loc[~(df['elec fuel total CO2 (kg)'] >= 0),
           'elec fuel total CO2 (kg)'] = 0

    return df


def correct_column_type(df):
    df.loc[:, 'lat'] = df.loc[:, 'lat'].astype(float)
    df.loc[:, 'lon'] = df.loc[:, 'lon'].astype(float)
    df.loc[:, 'plant id'] = df.loc[:, 'plant id'].astype(int)

    return df


def single_facility_data(rows, value_name):
    """
    Extract a single type of data for facilities

    Parameters
    ----------
    rows : list
        list of json objects from eia bulk data for a single type of facility
        information (generation, total fuel consumption, or fuel consumption for
        electricity generation)
    value_name : str
        Name of value. Should be one of:
        - generation (MWh)
        - total fuel (mmbtu)
        - elec fuel (mmbtu)

    Returns
    -------
    [type]
        [description]
    """

    facility_df = pd.concat(
        Parallel(n_jobs=-1)
        (delayed(facility_line_to_df)(json.loads(row))
         for row in rows)
    )
    facility_df.reset_index(drop=True, inplace=True)
    facility_df.rename(columns={'value': value_name}, inplace=True)

    facility_df = correct_column_type(facility_df)

    return facility_df


def fill_missing(df):
    """
    The outer merge of two dataframes may have some records that only existed
    in one of the dataframes. In the example below the first 3 records are
    from one df and the 4th record is from the other. We want to save the
    info from common (duplicate) columns and remove the '_x' '_y' from column
    names.

            plant id    lon_x geography_x       lon_y geography_y
    1778209       535      NaN         NaN -121.393336      USA-CA
    1775731     10475      NaN         NaN  -87.423300      USA-IN
    1776576     57996      NaN         NaN -156.318000      USA-HI
    669283      54877 -84.3892      USA-GA         NaN         NaN

    Parameters
    ----------
    df : dataframe
        The result of two merged dataframe (outer merge)

    """
    cols = [col[:-2] for col in df.columns if '_x' in col]

    # Create new column from the _x version,
    # fill missing values from the _y version
    for col in cols:
        df[col] = df.loc[:, col + '_x']
        df.loc[df[col].isnull(), col] = df.loc[df[col].isnull(), col + '_y']

        df.drop([col+'_x', col+'_y'], axis=1, inplace=True)


def extract_all_facility_data(raw_txt, path=None):
    """
    Extract facility generation, total fuel consumption, and fuel consumption
    for electricity generation (CHP facilities) from the EIA bulk data. Combine
    the three datasets into a single dataframe.

    Parameters
    ----------
    raw_txt : list
        list of lines from the ELEC.txt bulk file

    Returns
    -------
    dataframe
        Combined generation, total fuel consumption, and fuel for electricity
        for every generating facility in the US.
    """
    print('Extracting facility data')
    gen_rows = [row for row in raw_txt if b'ELEC.PLANT.GEN' in row
                and b'series_id' in row
                and b'ALL.M' in row
                and b'ALL-' not in row]
    total_fuel_rows = [row for row in raw_txt if b'ELEC.PLANT.CONS_TOT_BTU' in row
                       and b'series_id' in row
                       and b'ALL.M' in row
                       and b'ALL-' not in row]
    eg_fuel_rows = [row for row in raw_txt if b'ELEC.PLANT.CONS_EG_BTU' in row
                    and b'series_id' in row
                    and b'ALL.M' in row
                    and b'ALL-' not in row]

    # Create three dataframes with generation, total fuel consumption,
    # and fuel consumption for electricity generation (CHP facilities)
    facility_gen = single_facility_data(gen_rows, value_name='generation (MWh)')
    facility_all_fuel = single_facility_data(
        total_fuel_rows, value_name='total fuel (mmbtu)'
    )
    facility_eg_fuel = single_facility_data(
        eg_fuel_rows, value_name='elec fuel (mmbtu)'
    )

    # Merge all fuel consumption and generation dataframes
    keep_cols = [
        'fuel', 'generation (MWh)', 'month',
        'plant id', 'prime mover', 'year',
        'geography', 'lat', 'lon', 'last_updated'
    ]
    merge_cols = ['fuel', 'month', 'plant id', 'year']
    gen_total_fuel = facility_all_fuel.merge(
        facility_gen.loc[:, keep_cols], how='outer', on=merge_cols
    )

    fill_missing(gen_total_fuel)

    # Merge the fuel/generation and fuel for electricity dataframes
    keep_cols = [
        'fuel', 'elec fuel (mmbtu)', 'month',
        'plant id', 'prime mover', 'year',
        'geography', 'lat', 'lon', 'last_updated'
    ]
    all_facility_data = gen_total_fuel.merge(
        facility_eg_fuel.loc[:, keep_cols], how='outer', on=merge_cols
    )

    fill_missing(all_facility_data)

    all_facility_data['state'] = all_facility_data.geography.str[-2:]

    drop_cols = ['units', 'series_id', 'geography']
    all_facility_data.drop(drop_cols, axis=1, inplace=True)

    add_quarter(all_facility_data)

    # Add CO2 emissions for each facility - calculated from fuel consumption
    all_facility_data = calc_emissions_from_fuels(all_facility_data)

    rename_cols(all_facility_data)

    if path:
        # all_facility_data.to_csv(path, index=False)
        all_facility_data.to_parquet(path, index=False)
    else:
        return all_facility_data


def single_state_data(rows, value_name):

    dicts = [json.loads(row) for row in rows]
    df = pd.concat([state_line_to_df(x) for x in dicts
                    if x['geography'] in STATE_GEOS])
    if value_name == 'generation (MWh)':
        df.loc[:, 'value'] *= 1000
    else:
        df.loc[:, 'value'] *= 1E6
    # df.loc[:,'units'] = 'megawatthours'
    df.rename(columns={'value': value_name}, inplace=True)
    df.dropna(inplace=True)
    df['state'] = df['geography'].str[-2:]
    df.set_index(['type', 'year', 'month', 'state'], inplace=True)
    df.dropna(inplace=True)

    return df


def combine_state_gen_fuel(gen_df, total_fuel_df, eg_fuel_df):
    """
    Combine generation, total fuel consumption, and fuel consumption for electricity
    generation into a single dataframe. Calculate CO2 emissions from fuel
    consumption and emission factors.

    Parameters
    ----------
    gen_df : dataframe
        Generation (MWh) by state and fuel per month
    total_fuel_df : dataframe
        Total fuel consumption (mmbtu) by state and fuel per month
    eg_fuel_df : dataframe
        Fuel consumption for electricity generation by state and fuel per month

    Returns
    -------
    dataframe
        Wide-form dataframe with columns
        [type, year, month, generation (MWh), total fuel (mmbtu),
         elec fuel (mmbtu), all fuel CO2 (kg), elec fuel CO2 (kg),
         datetime, quarter]
    """
    fuel_df = pd.concat([total_fuel_df, eg_fuel_df['elec fuel (mmbtu)']],
                        axis=1)

    fuel_factors = pd.Series(
        {
            'NG': FOSSIL_EF['NG'],
            'PEL': np.mean([FOSSIL_EF['DFO'], FOSSIL_EF['RFO']]),
            'PC': FOSSIL_EF['PC'],
            'COW': np.mean([FOSSIL_EF['BIT'], FOSSIL_EF['SUB']]),
            'OOG': FOSSIL_EF['OG'],
        }, name='type')

    fuel_df['all fuel CO2 (kg)'] = (fuel_df['total fuel (mmbtu)']
                                    .multiply(fuel_factors, level='type',
                                              fill_value=0))
    fuel_df['elec fuel CO2 (kg)'] = (fuel_df['elec fuel (mmbtu)']
                                     .multiply(fuel_factors, level='type',
                                               fill_value=0))

    fuel_cols = ['total fuel (mmbtu)', 'elec fuel (mmbtu)',
                'all fuel CO2 (kg)', 'elec fuel CO2 (kg)']
    gen_fuel_df = pd.concat([gen_df, fuel_df[fuel_cols]], axis=1)
    gen_fuel_df['generation (MWh)'].fillna(value=0, inplace=True)

    add_quarter(gen_fuel_df)

    drop_cols = [
        'geography',
        'end',
        'f',
        'last_updated',
        'sector',
        'series_id',
        'start',
        'units',
    ]
    gen_fuel_df.drop(drop_cols, axis=1, inplace=True)
    rename_cols(gen_fuel_df)

    return gen_fuel_df


def extract_all_state_data(raw_txt, path=None):
    """
    Extract state-level generation, total fuel consumption, and fuel consumption
    for electricity generation (CHP facilities) from the EIA bulk data. Combine
    the three datasets into a single dataframe.

    Parameters
    ----------
    raw_txt : list
        list of lines from the ELEC.txt bulk file

    Returns
    -------
    dataframe
        Combined generation, total fuel consumption, and fuel for electricity
        for every state in the US.
    """
    print('Extracting state data')
    gen_rows = [row for row in raw_txt if b'ELEC.GEN' in row
                and b'series_id' in row
                and b'-99.M' in row
                and b'ALL' not in row]

    total_fuel_rows = [row for row in raw_txt if b'ELEC.CONS_TOT_BTU' in row
                       and b'series_id' in row
                       and b'-99.M' in row
                       and b'ALL' not in row
                       and b'US-99.m' not in row]

    eg_fuel_rows = [row for row in raw_txt if b'ELEC.CONS_EG_BTU' in row
                    and b'series_id' in row
                    and b'-99.M' in row
                    and b'ALL' not in row
                    and b'US-99.m' not in row]

    gen_df = single_state_data(gen_rows, value_name='generation (MWh)')
    total_fuel_df = single_state_data(
        total_fuel_rows, value_name='total fuel (mmbtu)'
    )
    eg_fuel_df = single_state_data(
        eg_fuel_rows, value_name='elec fuel (mmbtu)'
    )

    gen_fuel_df = combine_state_gen_fuel(gen_df, total_fuel_df, eg_fuel_df)

    if path:
        # gen_fuel_df.to_csv(path)
        gen_fuel_df.to_parquet(path)
    else:
        return gen_fuel_df


def extract_all_bulk_data():
    DATA_PATHS['eia_compiled'].mkdir(parents=True, exist_ok=True)

    download_ELEC()
    raw_txt = read_ELEC()

    facility_path = (
        DATA_PATHS['eia_compiled']
        / 'facility_gen_fuel_data_{}.parquet'.format(DATA_DATE)
    )
    state_path = (
        DATA_PATHS['eia_compiled']
        / 'state_gen_fuel_data_{}.parquet'.format(DATA_DATE)
    )
    national_path = (
        DATA_PATHS['eia_compiled']
        / 'national_gen_fuel_data_{}.parquet'.format(DATA_DATE)
    )

    if not facility_path.exists():
        extract_all_facility_data(
            raw_txt=raw_txt,
            path=facility_path
        )
    state_data = extract_all_state_data(raw_txt=raw_txt)
    national_data = state_data.groupby(['type', 'year', 'month']).sum()
    add_quarter(national_data)

    # state_data.to_csv(state_path)
    # national_data.to_csv(national_path)
    state_data.to_parquet(state_path)
    national_data.to_parquet(national_path)


if __name__ == "__main__":
    extract_all_bulk_data()
