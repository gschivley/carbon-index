# coding: utf-8

# from __future__ import division
import pandas as pd
import os
from os.path import join, abspath, normpath, dirname, split
import numpy as np

os.getcwd()

path = 'Data storage/Facility gen fuels and CO2 2017-05-25.zip'
df = pd.read_csv(path)
df.head()




def add_datetime(df, year='year', month='month'):
    df['datetime'] = pd.to_datetime(df[year].astype(str) + '-' +
                                    df[month].astype(str),
                                    format='%Y-%m')

def add_quarter(df, year='year', month='month'):
    add_datetime(df, year, month)
    df['quarter'] = df['datetime'].dt.quarter


def facility_index(eia_facility, epa, ef, fuel_cat_path):
    """
    Use EIA and EPA data to compile emissions, generation and fuel consumption
    reported by facilities into emissions intensity and generation by fuel
    category. Only facilities from the region of interest should be passed to
    this function.

    inputs:
        eia_facility: (dataframe) monthly generation and fuel consumption as
        reported by facilities to EIA
        epa: (dataframe) monthly CO2 emissions and gross generation as reported
            by facilities to EPA
        ef: (dataframe) emission factors for fuel combustion

    output:
        dataframe: total adjusted CO2 emissions, plus generation and fuel
            consumption by fuel category
    """

    # Calculate total & elec fossil and total CO2 emissions using fuel
    # consumption data.




    return co2_gen


def add_state_data(co2_gen, eia_total, ef):
    """
    Augment facility data with EIA estimates of non-reporting facilities. This
    information is only available at the state level.

    inputs:
        co2_gen: (dataframe) adjusted CO2 emissions, generation, and fuel
            consumption from facilities.
        eia_total: (dataframe) total generation and fuel consumption from all
            facilities (including non-reporting), by state
        ef: (dataframe) emission factors for fuel consumption

    output:
        dataframe: CO2 emission intensity and generation by fuel category
    """


    return index_gen


def co2_calc(fuel, ef):
    """
    Calculate CO2 emissions based on fuel consumption using emission factors
    from EIA/EPA and IPCC

    inputs:
        fuel: (dataframe) should have columns with the fuel type, total
            consumption, and consumption for electricity generation
        ef: (dataframe) emission factors (kg CO2/mmbtu) for each fuel

    output:
        dataframe: CO2 emissions from fuel consumption (total and for
        electricity) at each facility
    """


    return CO2

def add_nerc_data()
