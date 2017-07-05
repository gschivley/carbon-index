import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from os import listdir
from os.path import isfile, join
import glob
import numpy as np

ai_fns = glob.glob('Annual index*')
mi_fns = glob.glob('Monthly index*')
mg_fns = glob.glob('Monthly gen*')

# get all the filenames to read in and combine data
# Read each file as a dataframe, join them together

df_list = []
for f in ai_fns:
    state = f.split('.')[0][-2:]
    df = pd.read_csv(f)
    df['State'] = state
    df_list.append(df)
full_ai = pd.concat(df_list)
full_ai.reset_index(inplace=True, drop=True)
full_ai.rename(columns={'index (g/kWh)': 'annual index (g/kWh)'}, inplace=True)

df_list = []
for f in mi_fns:
    state = f.split('.')[0][-2:]
    df = pd.read_csv(f)
    df['State'] = state
    df_list.append(df)
full_mi = pd.concat(df_list)
full_mi.reset_index(inplace=True, drop=True)
full_mi.rename(columns={'index (g/kWh)': 'monthly index (g/kWh)'}, inplace=True)
full_mi['datetime'] = pd.to_datetime(full_mi['datetime'])
full_mi.head()
full_ai.head()

df_list = []
for f in mg_fns:
    state = f.split('.')[0][-2:]
    df = pd.read_csv(f)
    df['State'] = state
    df_list.append(df)
full_mg = pd.concat(df_list)
full_mg.reset_index(inplace=True, drop=True)
full_mg['datetime'] = pd.to_datetime(full_mg['datetime'])
monthly_gen = pd.pivot_table(full_mg, index=['State', 'datetime'], values='generation (MWh)', columns='fuel category')
monthly_gen.reset_index(inplace=True, drop=False)
monthly_gen.head()
# full_mg.rename(columns={'index (g/kWh)': 'annual index (g/kWh)'}, inplace=True)
full_mi.dtypes

gen_index = pd.merge(monthly_gen, full_mi[['datetime', 'State', 'monthly index (g/kWh)']], on=['datetime', 'State'])
gen_index.head()

for state in gen_index['State'].unique():
    gen_index.loc[gen_index['State']==state, 'rolling std'] = gen_index.loc[gen_index['State']==state, 'monthly index (g/kWh)'].rolling(window=12).std()
    gen_index.loc[gen_index['State']==state, 'normalized rolling std'] = gen_index.loc[gen_index['State']==state, 'rolling std'] / gen_index.loc[gen_index['State']==state, 'monthly index (g/kWh)'].rolling(window=12).mean()
gen_index.tail()
gen_index.replace(np.nan, 0, inplace=True)

# Not sure if this is needed anymore
index = pd.merge(full_ai, full_mi, on=['year', 'State'], suffixes=('_a', '_m'))
index.head()

# def stdev_fn(annual_avg)
state_df = index.loc[index['State']=='PA']
state_df['monthly index (g/kWh)'].rolling(window=12).std()
for state in index['State'].unique():
    index.loc[index['State']==state, 'rolling std'] = index.loc[index['State']==state, 'monthly index (g/kWh)'].rolling(window=12).std()

index['datetime'] = pd.to_datetime(index['datetime'])
index.dtypes
states = ['CA', 'PA', 'OK', 'TX', 'MD', 'WY']
g = sns.FacetGrid(index.loc[index['State'].isin(states)], col='State', col_wrap=3).map(plt.plot, 'datetime', 'rolling std').add_legend()

g = sns.FacetGrid(index.loc[index['State'].isin(states)], col='State', col_wrap=3).map(plt.scatter, 'change since 2005_m', 'rolling std').add_legend()

# percent of generation from each fuel type
# Change in percent of generation since 2001
fuels = ['Coal', 'Natural Gas', 'Renewables', 'Nuclear', 'Other']
gen_index['Year'] = gen_index['datetime'].dt.year
gen_index['Total gen'] = gen_index.loc[:, fuels].sum(axis=1)
for fuel in fuels:
    # New columns that are being added
    col_percent = 'percent ' + fuel
    col_change = 'change in ' + fuel

    # Calculate percent of generation from each fuel type
    gen_index[col_percent] = gen_index.loc[:, fuel] / gen_index.loc[:, 'Total gen']

    # Percent of fuel in state in 2001 (entire year)
    for state in gen_index['State'].unique():
        percent_fuel_2001 = gen_index.loc[(gen_index['Year'] == 2001) & (gen_index['State'] == state), fuel].sum() / gen_index.loc[(gen_index['Year'] == 2001) & (gen_index['State'] == state), 'Total gen'].sum()

        # Use percent of fuel in 2001 to calculate change for each state/month
        gen_index.loc[gen_index['State'] == state, col_change] = (gen_index.loc[gen_index['State'] == state, col_percent] - percent_fuel_2001) / percent_fuel_2001

percent_fuel_2001
gen_index.head()
gen_index.to_csv('Monthly state gen and index dataset.csv', index=False)

gen_index.dtypes

g = sns.FacetGrid(gen_index.loc[gen_index['State'].isin(states)], col='State', col_wrap=3, hue='Year', sharex=True, palette='Blues').map(plt.scatter, 'percent Renewables', 'rolling std').add_legend()
g = sns.FacetGrid(gen_index.loc[gen_index['State'].isin(states)], col='State', col_wrap=3, hue='Year', sharex=True, palette='Blues').map(plt.scatter, 'percent Renewables', 'normalized rolling std').add_legend()

state_list = []
renew_change_list = []
gas_change_list = []
index_change_list = []
norm_std_index_change_list = []
gen_index.columns
# This is going to be a crude measure - max monthly minus min monthly
for state in gen_index['State'].unique():
    temp_df = gen_index.loc[(gen_index['State'] == state) &
                            (gen_index['Year'] >=2005)]

    renew_change = temp_df['percent Renewables'].max() - temp_df['percent Renewables'].min()

    gas_change = temp_df['percent Natural Gas'].max() - temp_df['percent Natural Gas'].min()

    index_change = temp_df['monthly index (g/kWh)'].max() - temp_df['monthly index (g/kWh)'].min()

    norm_std_index_change = temp_df['normalized rolling std'].max() - temp_df['normalized rolling std'].min()

    state_list.append(state)
    renew_change_list.append(renew_change)
    gas_change_list.append(gas_change)
    index_change_list.append(index_change)
    norm_std_index_change_list.append(norm_std_index_change)

state_change_data = {'State': state_list,
                     'Renewable change': renew_change_list,
                     'Gas change': gas_change_list,
                     'Index change': index_change_list,
                     'Norm std index change': norm_std_index_change_list}
state_change_df = pd.DataFrame(data=state_change_data, columns=['State', 'Renewable change', 'Gas change', 'Index change', 'Norm std index change'])
state_change_df.head()
state_change_df.to_csv('State level changes since 2005.csv', index=False)


# Correlation matrix of variables
state_change_df.corr()
gen_index.loc[gen_index['State'] == state, cols].corr()['percent Renewables'][1]
renew_index_std_corr_list = []
for state in gen_index['State'].unique():
    cols = ['percent Renewables', 'rolling std']
    value = gen_index.loc[gen_index['State'] == state, cols].corr()['percent Renewables'][1]
    renew_index_std_corr_list.append(value)

renew_index_std_corr_list
pd.DataFrame(data={'State':state_list, 'Correlation': renew_index_std_corr_list}).to_csv('State by state renewable and variability correlation.csv', index=False)


g = sns.FacetGrid(gen_index, hue='State', palette='Blues', size=5, aspect=1.5).map(plt.scatter, 'percent Renewables', 'normalized rolling std')

gen_index.loc[gen_index['percent Renewables']>.8]
gen_index.head()
