import io, time, json
import pandas as pd
import urllib
import re
import os
from os.path import join
import numpy as np
import ftplib
from ftplib import FTP
import timeit
import sys
from joblib import Parallel, delayed


src_dir = os.path.join(os.getcwd(), 'src')
sys.path.append(src_dir)
from src.Data.data_extraction import import_clean_epa, import_group_epa


def fetch_cems_data(years, ftp_base, ftp_ext, existing=None, n_jobs=1):
    """
    Get EPA CEMS data one year at a time with consolidation to monthly
    resolution.

    inputs:
        years (list): list of years to download (provide as integers)
        ftp_base (str): base ftp path for logging in
        ftp_ext (str): directory to change into once logged in
        existing (list): If provided, this is a list of filenames and the
            datetime they were last modified on the ftp server. **THIS IS NOT
            IMPLEMENTED YET**

    output:
        cems_df (dataframe): a dataframe with monthly CO2 emissions and gross
            generation for each facility over the years specified
    """
    # Will be concatanating a list of dataframes
    df_list = []

    # Open an ftp connection
    print('Opening ftp connection')
    ftp = FTP(ftp_base)
    ftp.login()
    ftp.cwd(ftp_ext)
    # ftp.cwd('/dmdnload/emissions/hourly/monthly')

    # Loop through years
    for year in years:
        path = '{}/{}/{}'.format(ftp_base, ftp_ext, year)
        year_df = fetch_single_year(year, ftp, path, existing, n_jobs=n_jobs)

        df_list.append(year_df)

    cems_df = pd.concat(df_list)
    cems_df.reset_index(inplace=True, drop=True)

    return cems_df



def fetch_single_year(year, ftp, path, existing=None, n_jobs=1):
    """
    Download one year of EPA CEMS data and convert to monthly
    """
    start_time = timeit.default_timer()

    # Will be concatanating a list of dataframes
    df_list = []
    error_list = []

    year_str = str(year)
    print('Change directory to {}'.format(year_str))
    try:
        ftp.cwd(year_str)
    except ftplib.all_errors as e:
        print(e)

    # Use ftplib to get the list of filenames for the year
    print('Fetch filenames')
    fnames = ftp.nlst()

    # Look for files without _HLD in the name
    name_list = []
    # time_list = []
    print('Find filenames without _HLD')# and time last updated')
    for name in fnames:
        if '_HLD' not in name:
            name_list.append(name)

    print('Downloading data')

    # Make a list of ftp paths
    path_list = ['{}{}/{}'.format('ftp://', path, name) for name in name_list]

    df_list = Parallel(n_jobs=n_jobs)(delayed(fetch_file)
                                      (path, name, start_time)
                                      for path, name in
                                      zip(path_list, name_list))

    year_df = pd.concat(df_list)
    year_df.reset_index(inplace=True, drop=True)
    print(round((timeit.default_timer() - start_time)/60.0,2), 'min total')

    return year_df

def fetch_file(file_path, name, start_time):
    # Eventually this should be passed in as a parameter
    col_name_map = {'CO2_MASS' : 'CO2_MASS (tons)',
                'CO2_RATE' : 'CO2_RATE (tons/mmBtu)',
                'GLOAD' : 'GLOAD (MW)',
                'HEAT_INPUT' : 'HEAT_INPUT (mmBtu)',
                'NOX_MASS' : 'NOX_MASS (lbs)',
                'NOX_RATE' : 'NOX_RATE (lbs/mmBtu)',
                'SLOAD' : 'SLOAD (1000lb/hr)',
                'SLOAD (1000 lbs)' : 'SLOAD (1000lb/hr)',
                'SO2_MASS' : 'SO2_MASS (lbs)',
                'SO2_RATE' : 'SO2_RATE (lbs/mmBtu)'
                }

    # for file_path, name in zip(path_list, name_list):
    if '02' in name:
        print(name)
    try:
        r = urllib.request.urlopen(file_path)

        # This function was meant for already downloaded zip files.
        # It was modified so that passing None would just use the path
        processed_df = import_clean_epa(path=io.BytesIO(r.read()),
                                        name=None,
                                        col_name_map=col_name_map)
        grouped_df = import_group_epa(df=processed_df)
    except:
        print(round((timeit.default_timer() - start_time)/60.0,2), 'min so far')
        print(name)
        r = urllib.request.urlopen(file_path)

        # This function was meant for already downloaded zip files.
        # It was modified so that passing None would just use the path
        processed_df = import_clean_epa(path=io.BytesIO(r.read()),
                                        name=None,
                                        col_name_map=col_name_map)
        grouped_df = import_group_epa(df=processed_df)
        print(name, 'sucessfully downloaded')
    # finally:
    #     print(name, 'could not be downloaded')
    #     pass

    return grouped_df



# Try out process
ftp_path = 'newftp.epa.gov'
ftp_ext = 'dmdnload/emissions/hourly/monthly'

df_2016 = fetch_cems_data(years=[2016], ftp_base=ftp_path,
                    ftp_ext=ftp_ext, n_jobs=-1)


os.getcwd()
path = join(os.getcwd(), 'Data storage', 'Derived data',
            'test download 2017 CEMS.csv')
df.head()


df.to_csv(path)
