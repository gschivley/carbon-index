import pandas as pd
import os
import pathlib
from pathlib import Path
from src.Analysis.index import group_fuel_cats
import json

idx = pd.IndexSlice

# Read in a monthly EIA 860 file (operating and retired generators)
data_path = Path('Data storage')
file_path = data_path / 'EIA downloads' / 'november_generator2017.xlsx'
op = pd.read_excel(file_path, sheet_name=0, skiprows=1, skip_footer=1,
                   parse_dates={'op datetime': [14, 15]},
                   na_values=' ')

ret = pd.read_excel(file_path, sheet_name=2, skiprows=1, skip_footer=1,
                   parse_dates={'op datetime': [16, 17],
                                'ret datetime': [14, 15]},
                                na_values=' ')

# Clean up column names and only keep desired columns
op.columns = op.columns.str.strip()
ret.columns = ret.columns.str.strip()

op_cols = [
    'Plant ID', 'Nameplate Capacity (MW)', 'Net Summer Capacity (MW)',
    'Energy Source Code', 'Operating Month', 'Operating Year', 'Status',
    'op datetime'
]

ret_cols = [
    'Plant ID', 'Nameplate Capacity (MW)', 'Net Summer Capacity (MW)',
    'Energy Source Code', 'Operating Month', 'Operating Year',
    'Retirement Month', 'Retirement Year', 'op datetime', 'ret datetime'
]

op = op.loc[:, op_cols]
ret = ret.loc[:, ret_cols]
op.columns = op.columns.str.lower()
ret.columns = ret.columns.str.lower()


# Read in fuel category definitions
state_cat_path = data_path / 'Fuel categories' / 'State_facility.json'
custom_cat_path = data_path / 'Fuel categories' / 'Custom_results.json'
with open(state_cat_path) as json_data:
    state_cats = json.load(json_data)
with open(custom_cat_path) as json_data:
    custom_cats = json.load(json_data)

# state_cats

def reverse_cats(cat_file):
    'Reverse a dict of lists so each item in the list is a key'
    cat_map = {}
    for key, vals in cat_file.items():
        for val in vals:
            cat_map[val] = key
    return cat_map



# Aggregate EIA fuel codes to my final definitions
op['fuel'] = op.loc[:, 'energy source code'].map(reverse_cats(state_cats))
op['fuel category'] = op.loc[:, 'fuel'].map(reverse_cats(custom_cats))

ret['fuel'] = ret.loc[:, 'energy source code'].map(reverse_cats(state_cats))
ret['fuel category'] = ret.loc[:, 'fuel'].map(reverse_cats(custom_cats))

# Load the NERC region each power plant is in
nercs_path = data_path / 'Facility labels' / 'Facility locations_knn.csv'
facility_nerc = pd.read_csv(nercs_path)


# Add NERC regions to each generator
op = op.merge(facility_nerc.loc[:, ['plant id', 'nerc']], on='plant id')
ret = ret.merge(facility_nerc.loc[:, ['plant id', 'nerc']], on='plant id')


# Define iterables to loop over
years = range(2001,2018)
months = range(1,13)
nercs = op['nerc'].dropna().unique()
fuels = op['fuel category'].dropna().unique()

# Create a dataframe with the nerc/fuel/year/month index levels
index = pd.MultiIndex.from_product([nercs, fuels, years, months],
                                   names=['nerc', 'fuel', 'year', 'month'])
op_df_capacity = pd.DataFrame(index=index, columns=['active capacity'])
op_df_capacity.sort_index(inplace=True)

for year in years:
    print(year)

    for month in months:
        dt = pd.to_datetime('{}-{}-01'.format(year, month), yearfirst=True)

        for nerc in nercs:
            # op_dict[dt][nerc] = {}
            for fuel in fuels:

                plants_op = (op.loc[(op['op datetime'] <= dt) &
                                    (op['nerc'] == nerc) &
                                    (op['fuel category'] == fuel),
                                    'net summer capacity (mw)']
                                # .dropna()
                                .sum())

                retired = (ret.loc[(ret['ret datetime'] >= dt) &
                                   (ret['nerc'] == nerc) &
                                   (ret['fuel category'] == fuel),
                                   'net summer capacity (mw)']
                              # .dropna()
                              .sum())

                op_df_capacity.loc[idx[nerc, fuel, year, month], 'active capacity'] = plants_op + retired

# Add datetime from the year and month
op_df_capacity['datetime'] = (pd.to_datetime(
    op_df_capacity.index
                  .get_level_values('year')
                  .astype(str)
    + '-'
    + op_df_capacity.index
                    .get_level_values('month')
                    .astype(str)
    + '-01'))

# Write data to file
out_path = data_path / 'Plant capacity' / 'monthly capacity by fuel.csv'
op_df_capacity.to_csv(out_path)
