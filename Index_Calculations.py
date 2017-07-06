
# coding: utf-8

# # Import cleaned EIA/EPA data and calculate final Emissions Index/Generation by Fuel data
#
# This notebook makes use of data created in the notebooks (nested levels indicate a chain of calculations):
# - EIA Bulk Download - extract facility generation
#     - Emission factors
# - EIA bulk download - non-facility (distributed PV & state-level)
#     - Emission factors
# - Group EPA emissions data by month and quarter
#     - Load EPA Emissions Data

from __future__ import division
import pandas as pd
import os
import numpy as np


# ## Contents
# - [Import data](#Import-cleaned-data)
#     - [EIA facility data](#Facility-generation-and-CO2-emissions)
#     - [Total EIA gen & emissions](#Total-EIA-generation-and-CO2-emissions)
#     - [EPA emissions data](#Load-EPA-data)
# - [Check EIA facility against EIA total](#Check-EIA-facility-data-against-EIA-total-data-(gen-&-CO2))
# - [Adjust EPA facility emissions](#Correct-EPA-facility-emissions)
# - [Difference between EIA facility and total](#Emissions-and-gen-not-captured-by-facilities)
# - [Combine all data (monthly)](#Add-EPA-emissions-back-to-the-EIA-df,-use-EIA-emissions-where-EPA-don't-exist,-add-extra-EIA-emissions-for-state-level-data)
# - [Create plots](#Plots)
#     - [Monthly Index](#Monthly-Index)
#     - [Quarterly Index](#Quarterly-Index)
#     - [Annual Index](#Annual-Index)
#

# ## Import cleaned data
# 1. Facility generation and CO2 emissions
# 2. Total generation and CO2 emissions by fuel
# 3. EPA CO2 emissions



def index_and_generation(facility_path, all_fuel_path,
                         epa_path, emission_factor_path, import_folder,
                         export_folder, export_path_ext, state='USA'):
    """
    Read EIA and EPA data, compile and return the emisions index and generation
    at monthly, quarterly, and annual timeframes.

    inputs:
        state: name of state or geography, used to filter facility data
        facility_path: path to EIA facility data
        all_fuel_path: path to EIA all fuel consumption data
        epa_path: path to epa facilty emissions data
        emission_factor_path: path to fuel combustion emission factors
        export_folder: folder to export files to
        export_path_ext: unique xtension to add to export file names
    """

    # Create some helper functions to add datetime and quarter columns
    def add_datetime(df, year='year', month='month'):
        df['datetime'] = pd.to_datetime(df[year].astype(str) + '-' +
                                        df[month].astype(str),
                                        format='%Y-%m')

    def add_quarter(df, year='year', month='month'):
        add_datetime(df, year, month)
        df['quarter'] = df['datetime'].dt.quarter


    # ### Facility generation and CO2 emissions

    path = os.path.join(import_folder, facility_path)
    eia_facility = pd.read_csv(path, parse_dates=['datetime'],
                               low_memory=False)

    # Filter the facility data to only include the state in question.
    # Only do this if the input state isn't 'USA' (for all states)
    if state != 'USA':
        eia_facility = eia_facility.loc[
                            eia_facility['geography'].str.contains(state)]


    # ### EIA Facility level emissions (consolidate fuels/prime movers)
    # Because EIA tracks all fuel consumption at facilities that might produce both electricity and useful thermal output (CHP), CO<sub>2</sub> emissions can be from one 4 categories:
    # 1. Total fuel consumption for all uses (fossil & non-fossil, electricity & thermal output)
    # 2. Fossil fuel consumption for all uses (electricity only or CHP)
    # 3. Total fuel consumption for electricity only
    # 4. Fossil fuel consumption for electricity only
    #
    # We are interested in Category 4. EPA reports total emissions (Category 1), which need to be adjusted. To do this, we calculate a ratio
    #
    # $$CO_2 \ Ratio = \frac{Category \ 4}{Category \ 1}$$
    #
    # Will will apply the CO<sub>2</sub> ratio factors to EPA data [later in this notebook](#Correct-EPA-facility-emissions).

    cols = ['all fuel fossil CO2 (kg)','elec fuel fossil CO2 (kg)',
            'all fuel total CO2 (kg)','elec fuel total CO2 (kg)',
            'generation (MWh)']
    eia_facility_grouped = eia_facility.groupby(['year',
                                                 'month',
                                                 'plant id'])[cols].sum()
    eia_facility_grouped.reset_index(inplace=True)
    eia_facility_grouped['CO2 ratio'] = eia_facility_grouped['elec fuel fossil CO2 (kg)'] / eia_facility_grouped['all fuel total CO2 (kg)']
    eia_facility_grouped['CO2 ratio'].fillna(0, inplace=True)


    # ### Total EIA generation and CO2 emissions

    path = os.path.join(import_folder, all_fuel_path)
    eia_total = pd.read_csv(path, parse_dates=['datetime'], low_memory=False)

    # #### Consolidate total EIA to monthly gen and emissions
    # Only keep non-overlapping fuel categories so that my totals are correct (e.g. don't keep utility-scale photovoltaic, because it's already counted in utility-scale solar [SUN]).

    keep_types = [u'WWW', u'WND', u'WAS', u'SUN', 'DPV', u'NUC', u'NG',
           u'PEL', u'PC', u'OTH', u'COW', u'OOG', u'HPS', u'HYC', u'GEO']
    keep_cols = ['generation (MWh)', 'total fuel (mmbtu)', 'elec fuel (mmbtu)',
                 'all fuel CO2 (kg)', 'elec fuel CO2 (kg)']
    eia_total_monthly = eia_total.loc[(eia_total['type'].isin(keep_types))].groupby(['type', 'year', 'month'])[keep_cols].sum()

    keep_types = [u'WWW', u'WND', u'WAS', u'TSN', u'NUC', u'NG',
           u'PEL', u'PC', u'OTH', u'COW', u'OOG', u'HPS', u'HYC', u'GEO']

    # ### Load EPA data
    # Check to see if there are multiple rows per facility for a single month

    path = os.path.join(import_folder, epa_path)
    epa = pd.read_csv(path)

    add_quarter(epa, year='YEAR', month='MONTH')


    # Fill nan's with 0
    epa.loc[:,'CO2_MASS (kg)'].fillna(0, inplace=True)


    # ## Correct EPA facility emissions
    # Use the EIA facility adjustment factors to correct for CHP and biomass emissions

    # **Use an inner merge rather than left**
    # Justification: a left merge will retain CO2 emissions from facilities that aren't included in 923. But the generation and emissions for those facilities *are* included in the state-level estimates.

    eia_keep = ['month', 'year', 'all fuel total CO2 (kg)',
                'CO2 ratio', 'plant id']

    epa_adj = epa.merge(eia_facility_grouped[eia_keep],
                        left_on=['ORISPL_CODE', 'YEAR', 'MONTH'],
                        right_on=['plant id', 'year', 'month'], how='inner')

    epa_adj.drop(['month', 'year', 'plant id'], axis=1, inplace=True)
    epa_adj['epa index'] = (epa_adj.loc[:, 'CO2_MASS (kg)'] /
                            epa_adj.loc[:, 'GLOAD (MW)'])

    # ### Adjust CO2 emissions where we have a `CO2 ratio` value
    # Because of the inner merge above, all rows should have a valid CO2 ratio

    # Calaculated with an "inner" merge of the dataframes
    # for year in range(2001, 2017):
    #     total_co2 = epa_adj.loc[epa_adj['YEAR']==year, 'CO2_MASS (kg)'].sum()
    #     union_co2 = epa_adj.loc[(epa_adj['YEAR']==year) &
    #                             ~(epa_adj['CO2 ratio'].isnull()), 'CO2_MASS (kg)'].sum()
    #     missing = total_co2 - union_co2
    #
    #     print year, '{:.3%}'.format(union_co2/total_co2), 'accounted for',            missing/1000, 'metric tons missing'


    # **Look back at this to ensure that I'm correctly accounting for edge cases**
    # - Emissions reported to CEMS under a different code than EIA
    # - Emissions reported to CEMS but not EIA monthly
    # - Incorrect 0 value reported to CEMS

    # Start by setting all adjusted CO2 (`adj CO2 (kg)`) values to the reported CO2 value

    epa_adj['adj CO2 (kg)'] = epa_adj.loc[:, 'CO2_MASS (kg)']


    # If CEMS reported CO2 emissions are 0 but heat inputs are >0 and calculated CO2 emissions are >0, change the adjusted CO2 to NaN. These NaN values will be replaced by the calculated value later. Do the same for low index records (<300 g/kWh). If there is a valid CO2 ratio, multiply the adjusted CO2 column by the CO2 ratio.

    epa_adj.loc[~(epa_adj['CO2_MASS (kg)'] > 0) &
                (epa_adj['HEAT_INPUT (mmBtu)'] > 0) &
                (epa_adj['all fuel total CO2 (kg)'] > 0),
                'adj CO2 (kg)'] = np.nan
    epa_adj.loc[(epa_adj['epa index'] < 300) &
                (epa_adj['HEAT_INPUT (mmBtu)'] > 0) &
                (epa_adj['all fuel total CO2 (kg)'] > 0),
                'adj CO2 (kg)'] = np.nan

    epa_adj.loc[epa_adj['CO2 ratio'].notnull(),
                'adj CO2 (kg)'] *= epa_adj.loc[epa_adj['CO2 ratio'].notnull(),
                                               'CO2 ratio']

    # ## Emissions and gen not captured by facilities
    # Subtract these from the top-line EIA values to get the amount not captured at facilities in each month. EIA natural gas fuel consumption does not include BFG or OG.

    # ### Consolidate facility generation, fuel use, and CO2 emissions

    # OG and BFG are included in Other because I've included OOG in Other below
    # Pet liquids and pet coke are included here because they line up with how the state-level
    # EIA data are reported
    facility_fuel_cats = {'COW' : ['SUB','BIT','LIG', 'WC','SC','RC','SGC'],
                          'NG' : ['NG'],
                          'PEL' : ['DFO', 'RFO', 'KER', 'JF', 'PG', 'WO', 'SGP'],
                          'PC' : ['PC'],
                          'HYC' : ['WAT'],
                          'HPS' : [],
                          'GEO' : ['GEO'],
                          'NUC' : ['NUC'],
                          'OOG' : ['BFG', 'OG', 'LFG'],
                          'OTH' : ['OTH', 'MSN', 'MSW', 'PUR', 'TDF', 'WH'],
                          'SUN' : ['SUN'],
                          'DPV' : [],
                          'WAS' : ['OBL', 'OBS', 'OBG', 'MSB', 'SLW'],
                          'WND' : ['WND'],
                          'WWW' : ['WDL', 'WDS', 'AB', 'BLQ']
                         }


    # Create a new df that groups the facility data into more general fuel types that match up with the EIA generation and fuel use totals.

    eia_facility_fuel = eia_facility.copy()
    for key in facility_fuel_cats.keys():
        eia_facility_fuel.loc[eia_facility_fuel['fuel'].isin(facility_fuel_cats[key]),'type'] = key
    eia_facility_fuel = eia_facility_fuel.groupby(['type', 'year', 'month']).sum()


    # ### Extra generation and fuel use

    iterables = [eia_total_monthly.index.levels[0],
                 range(2001, 2017), range(1, 13)]
    index = pd.MultiIndex.from_product(iterables=iterables,
                                       names=['type', 'year', 'month'])
    eia_extra = pd.DataFrame(index=index,
                             columns=['total fuel (mmbtu)',
                                      'generation (MWh)',
                                      'elec fuel (mmbtu)'])

    idx = pd.IndexSlice

    use_columns = ['total fuel (mmbtu)',
                   'generation (MWh)',
                   'elec fuel (mmbtu)']
    eia_extra = (eia_total_monthly.loc[idx[:, :, :], use_columns] -
                 eia_facility_fuel.loc[idx[:, :, :], use_columns])

    # I have lumped hydro pumped storage in with conventional hydro in the facility data.
    # Because of this, I need to add HPS rows so that the totals will add up correctly.
    # Also need to add DPV because it won't show up otherwise
    eia_extra.loc[idx[['HPS', 'DPV'],:,:], use_columns] = eia_total_monthly.loc[idx[['HPS', 'DPV'],:,:], use_columns]

    # ### Calculate extra electric fuel CO2 emissions

    path = os.path.join(import_folder, emission_factor_path)
    ef = pd.read_csv(path, index_col=0)


    # We need to approximate some of the emission factors because the state-level EIA data is only available in the bulk download at an aggregated level. Natural gas usually makes up the bulk of this extra electric generation/fuel use (consumption not reported by facilities, estimated by EIA), and it is still a single fuel here.

    fuel_factors = {'NG': ef.loc['NG', 'Fossil Factor'],
                    'PEL': ef.loc[['DFO', 'RFO'], 'Fossil Factor'].mean(),
                    'PC': ef.loc['PC', 'Fossil Factor'],
                    'COW': ef.loc[['BIT', 'SUB'], 'Fossil Factor'].mean(),
                    'OOG': ef.loc['OG', 'Fossil Factor']}

    # Start with 0 emissions in all rows
    # For fuels where we have an emission factor, replace the 0 with the calculated value
    eia_extra['all fuel CO2 (kg)'] = 0
    eia_extra['elec fuel CO2 (kg)'] = 0

    for fuel in fuel_factors.keys():
        try:
            eia_extra.loc[idx[fuel, :, :], 'all fuel CO2 (kg)'] = \
                (eia_extra.loc[idx[fuel, :, :], 'total fuel (mmbtu)'] *
                 fuel_factors[fuel])

            eia_extra.loc[idx[fuel, :, :], 'elec fuel CO2 (kg)'] = \
                (eia_extra.loc[idx[fuel, :, :], 'elec fuel (mmbtu)'] *
                 fuel_factors[fuel])
        except:
            print fuel
            pass

    # ## Add EPA facility-level emissions back to the EIA facility df, use EIA emissions where EPA don't exist, add extra EIA emissions for state-level data
    # The dataframes start at a facility level. Extra EIA emissions for estimated state-level data are added after they are aggregated by year/month in the "Monthly Index" section below.

    epa_cols = ['ORISPL_CODE', 'YEAR', 'MONTH', 'adj CO2 (kg)']
    final_co2_gen = eia_facility_grouped.merge(epa_adj.loc[:, epa_cols],
                                               left_on=['plant id',
                                                        'year',
                                                        'month'],
                                               right_on=['ORISPL_CODE',
                                                         'YEAR',
                                                         'MONTH'],
                                               how='left')
    final_co2_gen.drop(['ORISPL_CODE', 'YEAR', 'MONTH'], axis=1, inplace=True)
    final_co2_gen['final CO2 (kg)'] = final_co2_gen['adj CO2 (kg)']
    final_co2_gen.loc[final_co2_gen['final CO2 (kg)'].isnull(),
                                    'final CO2 (kg)'] = \
        final_co2_gen.loc[final_co2_gen['final CO2 (kg)'].isnull(),
                          'elec fuel fossil CO2 (kg)']
    add_quarter(final_co2_gen)

    # ## Final index values

    # Start with some helper functions to convert units and calculate % change from 2005 annual value

    def g2lb(df):
        """
        Convert g/kWh to lb/MWh and add a column to the df
        """
        kg2lb = 2.2046
        df['index (lb/MWh)'] = df['index (g/kWh)'] * kg2lb

    def change_since_2005(df):
        """
        Calculate the % difference from 2005 and add as a column in the df
        """
        # first calculate the index in 2005
        index_2005 = ((df.loc[df['year'] == 2005, 'index (g/kWh)'] *
                       df.loc[df['year'] == 2005, 'generation (MWh)']) /
                      df.loc[df['year'] == 2005,
                             'generation (MWh)'].sum()).sum()

        # Calculated index value in 2005 is 599.8484560355034
        # If the value above is different throw an error
        # if (index_2005 > 601) or (index_2005 < 599.5):
        #     raise ValueError('Calculated 2005 index value', index_2005,
        #                      'is outside expected range. Expected value is 599.848')
        if type(index_2005) != float:
            raise TypeError('index_2005 is', type(index_2005),
                            'rather than a float.')

        df['change since 2005'] = ((df['index (g/kWh)'] - index_2005) /
                                   index_2005)


    # ### Monthly Index
    # Adding generation and emissions not captured in the facility-level data

    monthly_index = final_co2_gen.groupby(['year', 'month'])['generation (MWh)', 'final CO2 (kg)'].sum()
    monthly_index.reset_index(inplace=True)

    # Add extra generation and emissions not captured by facility-level data
    monthly_index.loc[:,'final CO2 (kg)'] += eia_extra.reset_index().groupby(['year', 'month'])['elec fuel CO2 (kg)'].sum().values
    monthly_index.loc[:,'generation (MWh)'] += eia_extra.reset_index().groupby(['year', 'month'])['generation (MWh)'].sum().values
    add_quarter(monthly_index)
    monthly_index['index (g/kWh)'] = monthly_index.loc[:, 'final CO2 (kg)'] / monthly_index.loc[:, 'generation (MWh)']

    change_since_2005(monthly_index)
    g2lb(monthly_index)
    monthly_index.dropna(inplace=True)

    path = os.path.join(export_folder, 'Monthly index'  + export_path_ext + '.csv')
    monthly_index.to_csv(path, index=False)


    # ### Quarterly Index
    # Built up from the monthly index

    quarterly_index = monthly_index.groupby(['year', 'quarter'])['generation (MWh)', 'final CO2 (kg)'].sum()
    quarterly_index.reset_index(inplace=True)
    quarterly_index['index (g/kWh)'] = quarterly_index.loc[:, 'final CO2 (kg)'] / quarterly_index.loc[:, 'generation (MWh)']
    quarterly_index['year_quarter'] = quarterly_index['year'].astype(str) + ' Q' + quarterly_index['quarter'].astype(str)
    change_since_2005(quarterly_index)
    g2lb(quarterly_index)


    path = os.path.join(export_folder, 'Quarterly index'  + export_path_ext + '.csv')
    quarterly_index.to_csv(path, index=False)


    # ### Annual Index


    annual_index = quarterly_index.groupby('year')['generation (MWh)', 'final CO2 (kg)'].sum()
    annual_index.reset_index(inplace=True)

    annual_index['index (g/kWh)'] = annual_index.loc[:, 'final CO2 (kg)'] / annual_index.loc[:, 'generation (MWh)']

    change_since_2005(annual_index)
    g2lb(annual_index)


    path = os.path.join(export_folder, 'Annual index'  + export_path_ext + '.csv')
    annual_index.to_csv(path, index=False)


    # #### Export to Excel file

    # path = os.path.join('..', 'Calculated values', 'US Power Sector CO2 Emissions Intensity.xlsx')
    # writer = pd.ExcelWriter(path)
    #
    # monthly_index.to_excel(writer, sheet_name='Monthly', index=False)
    # quarterly_index.to_excel(writer, sheet_name='Quarterly', index=False)
    # annual_index.to_excel(writer, sheet_name='Annual', index=False)
    # writer.save()


    # ## Generation by fuel


    fuel_cats = {'Coal' : [u'COW'],
                 'Natural Gas' : [u'NG'],
                 'Nuclear' : ['NUC'],
                 'Renewables' : [u'GEO', u'HYC', u'SUN', 'DPV',
                                 u'WAS', u'WND', u'WWW'],
                 'Other' : [u'OOG', u'PC', u'PEL', u'OTH', u'HPS']
                 }
    keep_types = [u'WWW', u'WND', u'WAS', u'SUN', 'DPV', u'NUC', u'NG',
           u'PEL', u'PC', u'OTH', u'COW', u'OOG', u'HPS', u'HYC', u'GEO']

    eia_gen_monthly = eia_total.loc[eia_total['type'].isin(keep_types)].groupby(['type', 'year', 'month']).sum()
    eia_gen_monthly.reset_index(inplace=True)
    eia_gen_monthly.drop(['end', 'sector', 'start'], inplace=True, axis=1)

    for key, values in fuel_cats.iteritems():
        eia_gen_monthly.loc[eia_gen_monthly['type'].isin(values),'fuel category'] = key

    eia_gen_monthly = eia_gen_monthly.groupby(['fuel category', 'year', 'month']).sum()
    eia_gen_monthly.reset_index(inplace=True)

    add_quarter(eia_gen_monthly)

    eia_gen_quarterly = eia_gen_monthly.groupby(['fuel category', 'year', 'quarter']).sum()
    eia_gen_quarterly.reset_index(inplace=True)
    eia_gen_quarterly['year_quarter'] = (eia_gen_quarterly['year'].astype(str) +
                                         ' Q' + eia_gen_quarterly['quarter'].astype(str))
    eia_gen_quarterly.drop('month', axis=1, inplace=True)

    eia_gen_annual = eia_gen_monthly.groupby(['fuel category', 'year']).sum()
    eia_gen_annual.reset_index(inplace=True)
    eia_gen_annual.drop(['month', 'quarter'], axis=1, inplace=True)


    # ### A function to estimate the emissions intensity of each fuel over time, making sure that they add up to the total emissions intensity.

    def generation_index(gen_df, index_df, group_by='year'):
        """
        Calculate the emissions intensity of each fuel in each time period. Use the
        adjusted total emissions from the index dataframe to ensure that the weighted
        sum of fuel emission intensities will equal the total index value.
        """
        final_adj_co2 = index_df.loc[:,'final CO2 (kg)'].copy()

        calc_total_co2 = gen_df.groupby(group_by)['elec fuel CO2 (kg)'].sum().values
    #     calc_total_co2 = calc_total_co2.reset_index()


        for fuel in gen_df['fuel category'].unique():
            try:
                gen_df.loc[gen_df['fuel category'] == fuel, 'adjusted CO2 (kg)'] = (gen_df.loc[gen_df['fuel category'] == fuel, 'elec fuel CO2 (kg)'] / calc_total_co2 * final_adj_co2.values)
            except:
                pass

        gen_df['adjusted index (g/kWh)'] = gen_df['adjusted CO2 (kg)']  /  gen_df['generation (MWh)']
        gen_df['adjusted index (lb/MWh)'] = gen_df['adjusted index (g/kWh)'] * 2.2046


    # Apply the function above to each generation dataframe

    generation_index(eia_gen_annual, annual_index, 'year')

    generation_index(eia_gen_monthly, monthly_index, ['year', 'month'])

    generation_index(eia_gen_quarterly, quarterly_index, 'year_quarter')

    # #### Export files

    path = os.path.join(export_folder, 'Monthly generation'  + export_path_ext + '.csv')
    eia_gen_monthly.to_csv(path, index=False)

    path = os.path.join(export_folder, 'Quarterly generation'  + export_path_ext + '.csv')
    eia_gen_quarterly.to_csv(path, index=False)

    path = os.path.join(export_folder, 'Annual generation'  + export_path_ext + '.csv')
    eia_gen_annual.to_csv(path, index=False)


    # #### Export to Excel file

    # path = os.path.join('..', 'Calculated values', 'US Generation By Fuel Type.xlsx')
    # writer = pd.ExcelWriter(path, engine='xlsxwriter')
    #
    # eia_gen_monthly.to_excel(writer, sheet_name='Monthly', index=False)
    #
    # eia_gen_quarterly.to_excel(writer, sheet_name='Quarterly', index=False)
    #
    # eia_gen_annual.to_excel(writer, sheet_name='Annual', index=False)
    # writer.save()
