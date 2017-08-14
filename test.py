from src.Data.make_data import get_annual_plants
import os
import pandas as pd
from src.Analysis.state2nerc import annual

annual_plants = get_annual_plants(2015)
annual_plants.head()

path = '/Users/Home/Documents/GitHub/Index-variability/Data storage/Facility gen fuels and CO2 2017-05-25.zip'
df = pd.read_csv(path)
df['state'] = df['geography'].str[-2]
temp = df.loc[(df['plant id'].isin(annual_plants)) &
                     (df['year'] == 2015)]
annual(df=temp, state='TX')

'reporting frequency' in temp.columns
