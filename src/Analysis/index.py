# coding: utf-8

from __future__ import division
import pandas as pd
import os
from os.path import join, abspath, normpath, dirname, split
import numpy as np

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




    return co2_gen
    pass


def add_state_data(co2_gen, eia_total, ef):
    """
    Augment facility data with EIA estimates of
    """
