from src.Data.make_data import get_annual_plants
import os
import pandas as pd
from src.Analysis.state2nerc import annual, add_nerc
import sys
import importlib
import src.Analysis.state2nerc

importlib.reload(src.Analysis.state2nerc)

from src.Analysis.state2nerc import annual, add_nerc
annual_plants = get_annual_plants(2015)
# annual_plants.head()

path = '/Users/Home/Documents/GitHub/Index-variability/Data storage/Facility gen fuels and CO2 2017-05-25.zip'
df = pd.read_csv(path)
df['state'] = df['geography'].str[-2:]
df.state.head()
temp = df.loc[(df['plant id'].isin(annual_plants)) &
                     (df['year'] == 2015)]

temp = add_nerc(temp)
temp.columns

facility_fuel_cats = {'COW': ['SUB', 'BIT', 'LIG', 'WC', 'SC', 'RC', 'SGC'],
                      'NG': ['NG'],
                      'PEL': ['DFO', 'RFO', 'KER', 'JF',
                              'PG', 'WO', 'SGP'],
                      'PC': ['PC'],
                      'HYC': ['WAT'],
                      'HPS': [],
                      'GEO': ['GEO'],
                      'NUC': ['NUC'],
                      'OOG': ['BFG', 'OG', 'LFG'],
                      'OTH': ['OTH', 'MSN', 'MSW', 'PUR', 'TDF', 'WH'],
                      'SUN': ['SUN'],
                      'DPV': [],
                      'WAS': ['OBL', 'OBS', 'OBG', 'MSB', 'SLW'],
                      'WND': ['WND'],
                      'WWW': ['WDL', 'WDS', 'AB', 'BLQ']
                      }
for category in facility_fuel_cats.keys():
    fuels = facility_fuel_cats[category]
    temp.loc[temp['fuel'].isin(fuels),
                    'fuel category'] = category

annual(df=temp, state='TX')
