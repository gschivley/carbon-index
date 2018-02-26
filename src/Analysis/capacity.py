import pandas as pd
import os
import pathlib
from pathlib import Path
from src.Analysis.index import group_fuel_cats
import json

idx = pd.IndexSlice

data_path = Path('Data storage')
file_path = data_path / 'EIA downloads' / 'november_generator2017.xlsx'
state_cat_path = data_path / 'Fuel categories' / 'State_facility.json'
custom_cat_path = data_path / 'Fuel categories' / 'Custom_results.json'
with open(state_cat_path) as json_data:
    state_cats = json.load(json_data)
with open(custom_cat_path) as json_data:
    custom_cats = json.load(json_data)

state_cats

def reverse_cats(cat_file):
    cat_map = {}
    for key, vals in cat_file.items():
        for val in vals:
            cat_map[val] = key
    return cat_map

op = pd.read_excel(file_path, sheet_name=0, skiprows=1, skip_footer=1,
                   parse_dates={'op datetime': [14, 15]},
                   na_values=' ')

ret = pd.read_excel(file_path, sheet_name=2, skiprows=1, skip_footer=1,
                   parse_dates={'op datetime': [16, 17],
                                'ret datetime': [14, 15]},
                                na_values=' ')
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
# op.tail()
op['fuel'] = op.loc[:, 'energy source code'].map(reverse_cats(state_cats))
op['fuel category'] = op.loc[:, 'fuel'].map(reverse_cats(custom_cats))

ret['fuel'] = ret.loc[:, 'energy source code'].map(reverse_cats(state_cats))
ret['fuel category'] = ret.loc[:, 'fuel'].map(reverse_cats(custom_cats))

nercs_path = data_path / 'Facility labels' / 'Facility locations_knn.csv'
facility_nerc = pd.read_csv(nercs_path)

op = op.merge(facility_nerc.loc[:, ['plant id', 'nerc']], on='plant id')
ret = ret.merge(facility_nerc.loc[:, ['plant id', 'nerc']], on='plant id')
ret.head()

op.head()

op_cols = [
    'nameplate capacity (mw)', 'net summer capacity (mw)', 'op datetime',
    'nerc', 'fuel category'
]
ret_cols = [
    'nameplate capacity (mw)', 'net summer capacity (mw)', 'ret datetime',
    'nerc', 'fuel category'
]

op_grouped = op.loc[:, op_cols].groupby(['op datetime', 'nerc', 'fuel category']).sum().reset_index()
ret_grouped = ret.loc[:, ret_cols].groupby(['ret datetime', 'nerc', 'fuel category']).sum().reset_index()

op_grouped.reset_index('op datetime', inplace=True)
op_grouped.loc[(op_grouped['op datetime'] < '2010-02') &
               (op_grouped['op datetime'] >= '2010-01'), :]

ret_grouped.loc[ret_grouped['ret datetime'] >= '2010-01']

op_filled_list = []
ret_filled_list = []
count = 0
for nerc in op_grouped['nerc'].unique():
    for fuel in op_grouped['fuel category'].dropna().unique():
        op_df = (op_grouped.loc[(op_grouped['nerc'] == nerc) &
                           (op_grouped['fuel category'] == fuel), :]
                       .set_index('op datetime')
                       .asfreq('1M', method='pad')
                       .reset_index())

        ret = (ret_grouped.loc[(ret_grouped['nerc'] == nerc) &
                           (ret_grouped['fuel category'] == fuel),
                            ['datetime', 'net summer capacity (mw)']])

        try:
            for tup in ret.itertuples(name=None):
                time = tup[1]
                amt = tup[-1]
                op_df.loc[op_df['op datetime'] <= time, 'net summer capacity (mw)'] += amt
        except:
            count += 1
            pass

        # ret_df = (ret_grouped.loc[(ret_grouped['nerc'] == nerc) &
        #                    (ret_grouped['fuel category'] == fuel), :]
        #                .set_index('ret datetime')
        #                .asfreq('1M', method='pad')
        #                .reset_index())

        op_filled_list.append(op_df)
        # ret_filled_list.append(ret_df)
count
op_filled = pd.concat(op_filled_list)
ret_filled = pd.concat(ret_filled_list)
op_filled.loc[(op_filled['nerc'] =='SPP') &
              (op_filled['fuel category'] =='Natural Gas') &
              (op_filled['op datetime'] > '2005-01-01')].head()

op_grouped.tail()

years = range(2001,2018)
months = range(1,13)
nercs = op['nerc'].dropna().unique()
fuels = op['fuel category'].dropna().unique()
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
op_df_capacity.dropna().tail()

out_path = data_path / 'Plant capacity' / 'monthly capacity by fuel.csv'

op_df_capacity.to_csv(out_path)
