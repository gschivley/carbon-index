%matplotlib inline
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import pathlib
from pathlib import Path
from src.Analysis.index import group_fuel_cats
import json
import calendar
sns.set(style='white')

pd.options.display.max_columns = 500
idx = pd.IndexSlice

# Read in a monthly EIA 860 file (operating and retired generators)
data_path = Path('Data storage')
file_path = data_path / 'EIA downloads' / 'november_generator2017.xlsx'
op = pd.read_excel(file_path, sheet_name='Operating', skiprows=1, skip_footer=1,
                   parse_dates={'op datetime': [14, 15]},
                   na_values=' ')

def bad_month_values(month):
    'Change value to 1 if outside 1-12'

    if month > 12 or month < 1:
        new_month = 1
    else:
        new_month = month
    return new_month

def make_dt_col(df, month_col, year_col):
    months = df[month_col].astype(str)
    years = df[year_col].astype(str)
    dt_string = years + '-' + months + '-' + '01'
    dt = pd.to_datetime(dt_string)
    return dt

ret = pd.read_excel(file_path, sheet_name='Retired', skiprows=1, skip_footer=1,
                    converters={'Operating Month': bad_month_values},
                    # parse_dates={'op datetime': [16, 17],
                    #              'ret datetime': [14, 15]},
                    na_values=' ')


ret['op datetime'] = make_dt_col(ret, 'Operating Month', 'Operating Year')
ret['ret datetime'] = make_dt_col(ret, 'Retirement Month', 'Retirement Year')
ret.head()
# Clean up column names and only keep desired columns
op.columns = op.columns.str.strip()
ret.columns = ret.columns.str.strip()
ret.head()
ret.columns
op_cols = [
    'Plant ID', 'Nameplate Capacity (MW)', 'Net Summer Capacity (MW)',
    'Energy Source Code', 'Prime Mover Code', 'Operating Month',
    'Operating Year', 'op datetime']
# [
#     'Plant ID', 'Nameplate Capacity (MW)', 'Net Summer Capacity (MW)',
#     'Energy Source Code', 'Operating Month', 'Operating Year', 'Status',
#     'op datetime', 'Prime Mover Code'
# ]

ret_cols = [
    'Plant ID', 'Nameplate Capacity (MW)', 'Net Summer Capacity (MW)',
    'Energy Source Code', 'Prime Mover Code', 'Retirement Month',
    'Retirement Year', 'Operating Month', 'Operating Year',
    'op datetime', 'ret datetime']
#     [
#     'Plant ID', 'Nameplate Capacity (MW)', 'Net Summer Capacity (MW)',
#     'Energy Source Code', 'Operating Month', 'Operating Year',
#     'Retirement Month', 'Retirement Year', 'op datetime', 'ret datetime',
#     'Prime Mover Code'
# ]

op = op.loc[:, op_cols]
ret = ret.loc[:, ret_cols]

op.columns = op.columns.str.lower()
ret.columns = ret.columns.str.lower()
op.status.unique()

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

ret.head()
ret.loc[ret['op datetime'].isnull()]
# Fraction of gas from NGCC/peakers by region


# Define iterables to loop over
years = range(2001,2018)
months = range(1,13)
nercs = op['nerc'].dropna().unique()
fuels = op['fuel category'].dropna().unique()

# Create a dataframe with the nerc/fuel/year/month index levels
index = pd.MultiIndex.from_product([nercs, fuels, years, months],
                                   names=['nerc', 'fuel category', 'year', 'month'])
op_df_capacity = pd.DataFrame(index=index, columns=['active capacity', 'possible gen'])
op_df_capacity.sort_index(inplace=True)


index = pd.MultiIndex.from_product([nercs, years, months],
                                   names=['nerc', 'year', 'month'])
op_ng_type = pd.DataFrame(index=index,
                          columns=['ngcc', 'turbine', 'other', 'total',
                                   'ngcc fraction', 'turbine fraction',
                                   'other fraction'])
op_ng_type.sort_index(inplace=True)

def month_hours(year, month):
    days = calendar.monthrange(year, month)[-1]
    return days * 24

# This is slow but it works.
# Find the active and retired capacity for every month
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
                                    'nameplate capacity (mw)']
                                # .dropna()
                                .sum())

                retired = (ret.loc[(ret['ret datetime'] >= dt) &
                                   (ret['op datetime'] <= dt) &
                                   (ret['nerc'] == nerc) &
                                   (ret['fuel category'] == fuel),
                                   'nameplate capacity (mw)']
                              # .dropna()
                              .sum())

                op_df_capacity.loc[idx[nerc, fuel, year, month], 'active capacity'] = plants_op + retired
                op_df_capacity.loc[idx[nerc, fuel, year, month], 'possible gen'] = month_hours(year, month) * (plants_op + retired)

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

op_ngcc = op.loc[(op['fuel category'] == 'Natural Gas') &
                 (op['prime mover code'].isin(['CA', 'CS', 'CT'])), :]
op_turbine = op.loc[(op['fuel category'] == 'Natural Gas') &
                 (op['prime mover code'] == 'GT'), :]
op_other = op.loc[(op['fuel category'] == 'Natural Gas') &
                  (op['prime mover code'].isin(['IC', 'ST'])), :]

ret_ngcc = ret.loc[(ret['fuel category'] == 'Natural Gas') &
                 (ret['prime mover code'].isin(['CA', 'CS', 'CT'])), :]
ret_turbine = ret.loc[(ret['fuel category'] == 'Natural Gas') &
                  (ret['prime mover code'] == 'GT'), :]
ret_other = ret.loc[(ret['fuel category'] == 'Natural Gas') &
                  (ret['prime mover code'].isin(['GT', 'IC', 'ST'])), :]

for year in years:
    print(year)

    for month in months:
        dt = pd.to_datetime('{}-{}-01'.format(year, month), yearfirst=True)

        for nerc in nercs:

            ngcc = (
                op_ngcc.loc[(op_ngcc['op datetime'] <= dt) &
                                    (op_ngcc['nerc'] == nerc),
                                    'nameplate capacity (mw)'].sum()
                + ret_ngcc.loc[(ret_ngcc['ret datetime'] >= dt) &
                                    (ret_ngcc['op datetime'] <= dt) &
                                    (ret_ngcc['nerc'] == nerc),
                                    'nameplate capacity (mw)'].sum()
            )

            turbine = (
                op_turbine.loc[(op_turbine['op datetime'] <= dt) &
                                    (op_turbine['nerc'] == nerc),
                                    'nameplate capacity (mw)'].sum()
                + ret_turbine.loc[(ret_turbine['ret datetime'] >= dt) &
                                    (ret_turbine['op datetime'] <= dt) &
                                    (ret_turbine['nerc'] == nerc),
                                    'nameplate capacity (mw)'].sum()
            )

            other = (
                op_other.loc[(op_other['op datetime'] <= dt) &
                                    (op_other['nerc'] == nerc),
                                    'nameplate capacity (mw)'].sum()
                + ret_other.loc[(ret_other['ret datetime'] >= dt) &
                                    (ret_other['op datetime'] <= dt) &
                                    (ret_other['nerc'] == nerc),
                                    'nameplate capacity (mw)'].sum()
            )
            total = ngcc + turbine + other

            op_ng_type.loc[idx[nerc, year, month], 'total'] = total
            op_ng_type.loc[idx[nerc, year, month], 'ngcc'] = ngcc
            op_ng_type.loc[idx[nerc, year, month], 'turbine'] = turbine
            op_ng_type.loc[idx[nerc, year, month], 'other'] = other

            # try:
            #     op_ng_type.loc[idx[nerc, year, month],
            #                    'ngcc fraction'] = ngcc / total
            #     op_ng_type.loc[idx[nerc, year, month],
            #                    'other fraction'] = other / total
            # except:
            #     print(total)
            #     op_ng_type.loc[idx[nerc, year, month], 'ngcc fraction'] = 0
            #     op_ng_type.loc[idx[nerc, year, month], 'other fraction'] = 0
op_ng_type['ngcc fraction'] = op_ng_type['ngcc'] / op_ng_type['total']
op_ng_type['turbine fraction'] = op_ng_type['turbine'] / op_ng_type['total']
op_ng_type['other fraction'] = op_ng_type['other'] / op_ng_type['total']
op_ng_type.fillna(0, inplace=True)

op_ng_type['datetime'] = (pd.to_datetime(
    op_ng_type.index
                  .get_level_values('year')
                  .astype(str)
    + '-'
    + op_ng_type.index
                    .get_level_values('month')
                    .astype(str)
    + '-01'))

out_path = data_path / 'Plant capacity' / 'monthly natural gas split.csv'
op_ng_type.to_csv(out_path)


op_ng_type_avg = (op_ng_type.reset_index()
                            .groupby(['nerc', 'year'])
                            .mean())
op_ng_type_avg.head()
order = ['FRCC', 'TRE', 'NPCC', 'WECC', 'SERC', 'RFC', 'SPP', 'MRO']
# ['SPP', 'MRO', 'RFC', 'SERC', 'TRE', 'FRCC', 'WECC', 'NPCC']
g = sns.factorplot(x='year', y='ngcc fraction', hue='nerc',
               data=op_ng_type_avg.reset_index(),
               palette='tab10', hue_order=order,
               scale=0.75, aspect=1.4, ci=0).set_xticklabels(rotation=35)

order = ['MRO', 'RFC', 'SERC', 'FRCC', 'SPP', 'WECC', 'NPCC', 'TRE']
g = sns.factorplot(x='year', y='turbine fraction', hue='nerc',
               data=op_ng_type_avg.reset_index(),
               palette='tab10', hue_order=order,
               scale=0.75, aspect=1.4, ci=0).set_xticklabels(rotation=35)

op_ng_type_avg.head()
temp = op_ng_type_avg.reset_index().melt(id_vars=['nerc', 'year'], value_vars=['ngcc fraction', 'turbine fraction', 'other fraction'], var_name='type', value_name='fraction capacity')
temp.head()
temp.loc[(temp['nerc'] == 'TRE') &
         (temp['type'] == 'ngcc fraction')]
temp.loc[(temp['nerc'] == 'SERC') & 
         (temp['type'] == 'ngcc fraction')]


sns.factorplot(x='year', y='fraction capacity', data=temp, hue='nerc',
               row='type', palette='tab10', hue_order=order,
               scale=0.75, aspect=1.4, ci=0).set_xticklabels(rotation=35)
