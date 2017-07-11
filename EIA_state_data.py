
# coding: utf-8

# # National generation and fuel consumption
# The data in this notebook is generation and consumption by fuel type for the entire US. These values are larger than what would be calculated by summing facility-level data. Note that the fuel types are somewhat aggregated (coal rather than BIT, SUB, LIG, etc). So when we multiply the fuel consumption by an emissions factor there will be some level of error.

# In[34]:

import pandas as pd
import json


def state_total(state, elec_path, emission_factor_path, output_path):
    """
    Read data for a single state from the EIA state-level json file.

    inputs:
        state: Two character state abbreviation - use "US" for national data
        elec_path: file path for the EIA "ELEC.txt" file
        emission_factor_path: path to fuel combustion emission factors
        output_path: output path for the final data csv
    """
    # ## Read ELECT.txt file

    # In[35]:

    # path = os.path.join('2017-05-25 ELEC.txt')
    with open(elec_path, 'rb') as f:
        raw_txt = f.readlines()


    # ## Filter lines to only include total generation and fuel use
    # Only want monthly US data for all sectors
    # - US-99.M
    # - ELEC.GEN, ELEC.CONS_TOT_BTU, ELEC.CONS_EG_BTU
    # - not ALL

    # Fuel codes:
    # - WWW, wood and wood derived fuels
    # - WND, wind
    # - STH, solar thermal
    # - WAS, other biomass
    # - TSN, all solar
    # - SUN, utility-scale solar
    # - NUC, nuclear
    # - NG, natural gas
    # - PEL, petroleum liquids
    # - SPV, utility-scale solar photovoltaic
    # - PC, petroluem coke
    # - OTH, other
    # - COW, coal,
    # - DPV, distributed photovoltaic
    # - OOG, other gases
    # - HPS, hydro pumped storage
    # - HYC, conventional hydroelectric
    # - GEO, geothermal
    # - AOR, other renewables (total)

    # In[36]:

    def line_to_df(line):
        """
        Take in a line (dictionary), returns a dataframe.

        inputs:
            line: line of a JSON file
        """
        for key in ['latlon', 'source', 'copyright', 'description',
                    'geoset_id', 'iso3166', 'name', 'state']:
            line.pop(key, None)

        # Split the series_id up to extract information
        # Example: ELEC.PLANT.GEN.388-WAT-ALL.M
        series_id = line['series_id']
        series_id_list = series_id.split('.')
        # Use the second to last item in list rather than third
        plant_fuel_mover = series_id_list[-2].split('-')
        line['type'] = plant_fuel_mover[0]
        line['sector'] = plant_fuel_mover[2]
        temp_df = pd.DataFrame(line)

        try:
            temp_df['year'] = temp_df.apply(lambda x: x['data'][0][:4],
                                            axis=1).astype(int)
            temp_df['month'] = temp_df.apply(lambda x: x['data'][0][-2:],
                                             axis=1).astype(int)
            temp_df['value'] = temp_df.apply(lambda x: x['data'][1], axis=1)
            temp_df.drop('data', axis=1, inplace=True)
            return temp_df
        except:
            exception_list.append(line)
            pass

    # In[37]:
    # sector_string combines the state with the generation from all sectors
    # (the '99' code) at a monthly level
    sector_string = '-{}-99.M'.format(state)

    exception_list = []
    gen_rows = [row for row in raw_txt if 'ELEC.GEN' in row and 'series_id' in
                row and sector_string in row and 'ALL' not in row]
    total_fuel_rows = [row for row in raw_txt if 'ELEC.CONS_TOT_BTU' in row and
                       'series_id' in row and sector_string in row and 'ALL'
                       not in row]
    eg_fuel_rows = [row for row in raw_txt if 'ELEC.CONS_EG_BTU' in row and
                    'series_id' in row and sector_string in row and 'ALL' not
                    in row]

    # ## All generation by fuel

    # In[38]:

    gen_df = pd.concat([line_to_df(json.loads(row)) for row in gen_rows])


    # Multiply generation values by 1000 and change the units to MWh

    # In[40]:

    gen_df.loc[:, 'value'] *= 1000
    gen_df.loc[:, 'units'] = 'megawatthours'


    # In[41]:

    gen_df['datetime'] = pd.to_datetime(gen_df['year'].astype(str) + '-' +
        gen_df['month'].astype(str), format='%Y-%m')
    gen_df['quarter'] = gen_df['datetime'].dt.quarter
    gen_df.rename_axis({'value':'generation (MWh)'}, axis=1, inplace=True)

    # ## Total fuel consumption

    # In[43]:

    total_fuel_df = pd.concat([line_to_df(json.loads(row)) for row in
                              total_fuel_rows])

    # Multiply generation values by 1,000,000 and change the units to MMBtu

    # In[45]:

    total_fuel_df.loc[:,'value'] *= 1E6
    total_fuel_df.loc[:,'units'] = 'mmbtu'


    # In[46]:

    total_fuel_df['datetime'] = pd.to_datetime(total_fuel_df['year']
                                               .astype(str)
        + '-' + total_fuel_df['month'].astype(str), format='%Y-%m')
    total_fuel_df['quarter'] = total_fuel_df['datetime'].dt.quarter
    total_fuel_df.rename_axis({'value':'total fuel (mmbtu)'}, axis=1,
                              inplace=True)

    # ## Electric generation fuel consumption

    # In[49]:

    eg_fuel_df = pd.concat([line_to_df(json.loads(row)) for row in
                           eg_fuel_rows])

    # Multiply generation values by 1,000,000 and change the units to MMBtu

    # In[51]:

    eg_fuel_df.loc[:,'value'] *= 1E6
    eg_fuel_df.loc[:,'units'] = 'mmbtu'


    # In[52]:

    eg_fuel_df['datetime'] = pd.to_datetime(eg_fuel_df['year'].astype(str) +
                              '-' + eg_fuel_df['month'].astype(str),
                              format='%Y-%m')
    eg_fuel_df['quarter'] = eg_fuel_df['datetime'].dt.quarter
    eg_fuel_df.rename_axis({'value':'elec fuel (mmbtu)'}, axis=1, inplace=True)

    # ## Combine three datasets
    # Need to estimate fuel use for OOG, because EIA doesn't include any (this is only ~2% of OOG fuel for electricity in 2015).

    # In[54]:

    merge_cols = ['type', 'year', 'month']

    fuel_df = total_fuel_df.merge(eg_fuel_df[merge_cols+['elec fuel (mmbtu)']],
                                  how='outer', on=merge_cols)

    # In[56]:

    gen_fuel_df = gen_df.merge(fuel_df[merge_cols+['total fuel (mmbtu)',
                               'elec fuel (mmbtu)']], how='outer',
                               on=merge_cols)

    # ## Add CO<sub>2</sub> emissions
    #
    # The difficulty here is that EIA combines all types of coal fuel consumption together in the bulk download and API. Fortunately the emission factors for different coal types aren't too far off on an energy basis (BIT is 93.3 kg/mmbtu, SUB is 97.2 kg/mmbtu). I'm going to average the BIT and SUB factors rather than trying to do something more complicated. In 2015 BIT represented 45% of coal energy for electricity and SUB represented 48%.
    #
    # Same issue with petroleum liquids. Using the average of DFO and RFO, which were the two largest share of petroleum liquids.

    # In[58]:

    # path = os.path.join('Clean data', 'Final emission factors.csv')
    ef = pd.read_csv(emission_factor_path, index_col=0)

    # ### Match general types with specific fuel codes

    # Fuel codes:
    # - WWW, wood and wood derived fuels
    # - WND, wind
    # - STH, solar thermal
    # - WAS, other biomass
    # - TSN, all solar
    # - SUN, utility-scale solar
    # - NUC, nuclear
    # - NG, natural gas
    # - PEL, petroleum liquids
    # - SPV, utility-scale solar photovoltaic
    # - PC, petroluem coke
    # - OTH, other
    # - COW, coal,
    # - DPV, distributed photovoltaic
    # - OOG, other gases
    # - HPS, hydro pumped storage
    # - HYC, conventional hydroelectric
    # - GEO, geothermal
    # - AOR, other renewables (total)

    # In[61]:

    fuel_factors = {'NG' : ef.loc['NG', 'Fossil Factor'],
                   'PEL': ef.loc[['DFO', 'RFO'], 'Fossil Factor'].mean(),
                   'PC' : ef.loc['PC', 'Fossil Factor'],
                   'COW' : ef.loc[['BIT', 'SUB'], 'Fossil Factor'].mean(),
                   'OOG' : ef.loc['OG', 'Fossil Factor']}

    # In[62]:

    # Start with 0 emissions in all rows
    # For fuels where we have an emission factor, replace the 0 with the calculated value
    gen_fuel_df['all fuel CO2 (kg)'] = 0
    gen_fuel_df['elec fuel CO2 (kg)'] = 0
    for fuel in fuel_factors.keys():
        gen_fuel_df.loc[gen_fuel_df['type']==fuel,'all fuel CO2 (kg)'] =         gen_fuel_df.loc[gen_fuel_df['type']==fuel,'total fuel (mmbtu)'] * fuel_factors[fuel]

        gen_fuel_df.loc[gen_fuel_df['type']==fuel,'elec fuel CO2 (kg)'] =         gen_fuel_df.loc[gen_fuel_df['type']==fuel,'elec fuel (mmbtu)'] * fuel_factors[fuel]

    # ### Export data

    # In[64]:

    # path = os.path.join('Clean data', 'EIA country-wide gen fuel CO2 2017-05-25.csv')
    gen_fuel_df.to_csv(output_path, index=False)
