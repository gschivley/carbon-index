import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from Index_Calculations import index_and_generation
from EIA_state_data import state_total
import os
import glob

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

elec_path = os.path.join('Data storage', '2017-05-25 ELEC.txt')
with open(elec_path, 'rb') as f:
    raw_txt = f.readlines()

for state in states:
    output_path = os.path.join('Data storage',
                               'state gen data', state + ' fuels gen.csv')
    emission_factor_path = os.path.join('Data storage',
                                        'Final emission factors.csv')

    # Creates state-level data from the bulk-download file
    state_total(state, raw_txt, emission_factor_path, output_path)

    # Transforms the state-level gen
    # index_and_generation(facility_path='Facility gen fuels and CO2 '
    #                      '2017-05-25.csv', all_fuel_path=output_path,
    #                      epa_path='Monthly EPA emissions 2017-05-25.csv',
    #                      emission_factor_path='Final emission factors.csv',
    #                      export_folder='final state data', export_path_ext=' '
    #                      + state, state=state)





facility_df = pd.read_csv('Facility gen fuels and CO2 2017-05-25.csv',
                          nrows=10)

facility_df.loc[facility_df['geography'].str.contains('FL')]

state_df = pd.read_csv('EIA country-wide gen fuel CO2 2017-05-25.csv', nrows=100)
PA_df = pd.read_csv('PA fuels gen.csv')
PA_df

PA_quarter_gen = pd.read_csv('Quarterly generation_PA.csv')
PA_quarter_gen.head()
g = sns.FacetGrid(data=PA_quarter_gen, hue='fuel category')
g.map(plt.plot, 'year_quarter', 'generation (MWh)')
