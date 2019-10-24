import pandas as pd
import numpy as np
from ftplib import FTP
from joblib import Parallel, delayed
import timeit
import urllib
import re
import os
from os.path import join
import sys
import io, time, json

from src.params import CEMS_BASE, CEMS_EXT, DATA_PATHS, DATA_DATE, CEMS_YEARS
from src.util import rename_cols

class CEMS():
    def __init__(self, ftp_base, ftp_ext, months=None, states=None):

        self.ftp_base = ftp_base
        self.ftp_ext = ftp_ext
        self.months = months
        self.states = states


    def connect_ftp(self):
        # Open ftp connection and change top-level folder above years
        print('Opening ftp connection')
        self.ftp = FTP(self.ftp_base)
        self.ftp.login()
        self.ftp.cwd(self.ftp_ext)

    def fetch_cems_data(self, years):
        """
        Get EPA CEMS data one year at a time with consolidation to monthly
        resolution.

        inputs:
            years (list): list of years to download (provide as integers)

        output:
            cems_df (dataframe): a dataframe with monthly emissions and gross
                generation for each facility over the years specified
        """
        self.connect_ftp()

        # Loop through years
        df_list = []
        for year in years:
            # Move into the directory for this year
            self.ftp.cwd(str(year))

            # Set folder path for ftp file download
            self.folder_path = '{}/{}/{}'.format(self.ftp_base,
                                             self.ftp_ext,
                                             year)

            # Find file and make ftp path names
            self.find_names()
            self.path_list = ['{}{}/{}'.format('ftp://', self.folder_path, name)
                         for name in self.name_list]
            # self.create_paths()

            # Get data for a single year and do something with it
            df_list.append(self.fetch_single_year(year))

            # Move back out of the directory for this year
            # Reconnect the ftp if there is an error
            try:
                self.ftp.cwd('..')
            except:
                self.connect_ftp()
        all_data = pd.concat(df_list)
        return all_data

    def fetch_single_year(self, year):
        """
        Download one year of EPA CEMS data and convert to monthly
        """
        self.start_time = timeit.default_timer()
        self.year = year

        # error_list = []

        print('Downloading {} data'.format(year))

        df_list = []
        for path, file_name in zip(self.path_list, self.name_list):
            df_list.append(self.fetch_file(path, file_name))

        year_df = pd.concat(df_list)
        print(round((timeit.default_timer() - self.start_time)/60.0,2),
              'min total')

        return year_df


    def fetch_file(self, file_path, name):
        'Call import_clean_epa to download and process a single file'
        try:
            r = urllib.request.urlopen(file_path)

            # This function was meant for already downloaded zip files.
            # It was modified so that passing None would just use the path
            self.processed_df = self.import_clean_epa(path=io.BytesIO(r.read()),
                                            file_name=name,
                                            year=self.year)

        except:
            print(round((timeit.default_timer() - self.start_time)/60.0,2), 'min so far')
            print(name, 'had an error, trying again')
            r = urllib.request.urlopen(file_path)

            # This function was meant for already downloaded zip files.
            # It was modified so that passing None would just use the path
            self.processed_df = self.import_clean_epa(path=io.BytesIO(r.read()),
                                            file_name=name,
                                            year=self.year)
            print(name, 'had an error but was successfully downloaded')

        self.agg_df = self.group_by_plant(self.processed_df)

        return self.agg_df


    def find_names(self):
        '''
        Find file names for a single year and the time they were last modfied.
        If the modified time is not newer than when previously checked (based
        on times stored in the SQL database) then keep it in the download list.

        '''
        self.fnames = self.ftp.nlst()

        self.name_list = [name for name in self.fnames
                          if '_HLD' not in name]

        # if only a select list of months is needed
        # self.months is set in the class __init__
        if self.months:
            self.name_list = [name for name in self.name_list
                              if name[6:8] in self.months]

        # Only if a select list of states is needed
        if self.states:
            self.name_list = [name for name in self.name_list
                              if name[4:6].lower() in self.states]

    def create_paths(self):
        'Create ftp paths for file downloads from file names'

        self.path_list = ['{}{}/{}'.format('ftp://', self.folder_path, name)
                     for name in self.new_name_list]

    def import_clean_epa(self, path, file_name, year):
        """
        Add docstring

        TO ADD:
        convert lb to kg
        tons to kg
        timezone to UTC
        change downstream code once we do these things here
        """
        ## Need to change old file column names to match recent versions
        col_name_map = {'CO2_MASS' : 'CO2_MASS (tons)',
                    'CO2_RATE' : 'CO2_RATE (tons/mmBtu)',
                    'GLOAD' : 'GLOAD (MWh)',
                    'HEAT_INPUT' : 'HEAT_INPUT (mmBtu)',
                    'NOX_MASS' : 'NOX_MASS (tons)',
                    'NOX_RATE' : 'NOX_RATE (tons/mmBtu)',
                    'SLOAD' : 'SLOAD (1000lb/hr)',
                    'SLOAD (1000 lbs)' : 'SLOAD (1000lb/hr)',
                    'SO2_MASS' : 'SO2_MASS (tons)',
                    'SO2_RATE' : 'SO2_RATE (tons/mmBtu)'
                    }


        df_temp = pd.read_csv(path, compression='zip',
                                   low_memory=False)

        # Combine OP_DATE and OP_HOUR into datetime
        date = df_temp.loc[:, 'OP_DATE']
#         hr = df_temp.loc[:, 'OP_HOUR'].astype(str)
        df_temp.loc[:,'dt'] = pd.to_datetime(date, format='%m-%d-%Y')

        # Rename columns to match more recent years
        df_temp.rename(col_name_map, axis=1, inplace=True)

        # Change column names
        final_col_name_map = {
                    'ORISPL_CODE': 'orispl',
                    'CO2_MASS (tons)': 'co2mass_tons',
                    'GLOAD (MWh)': 'gload_mwh',
                    'HEAT_INPUT (mmBtu)': 'heatinput_mmbtu',
                    'NOX_MASS (tons)': 'noxmass_tons',
                    'SO2_MASS (tons)': 'so2mass_tons',
                    }

        df_temp.rename(final_col_name_map, axis=1, inplace=True)
        df_temp.columns = df_temp.columns.str.lower()

        # Convert emissions to SI and drop imperial columns
        self.convert2si(df_temp)

        # Drop columns not needed
        # unit_id only exists from 2011 onward
        keep_cols = [
            'state', 'orispl', 'dt', 'gload_mwh', 'heatinput_mmbtu',
            'co2mass_kg', 'noxmass_kg', 'so2mass_kg'
        ]
        df_temp = df_temp.loc[:, keep_cols]

        return df_temp


    def group_by_plant(self, df):
        'Group to the plant level by month'

        df['month'] = df.dt.dt.month
        df['year'] = df.dt.dt.year
        group_cols = ['year', 'month', 'orispl']
        grouped_df = df.groupby(group_cols, as_index=False).sum()

        return grouped_df


    def convert2si(self, df):
        'Convert imperial units to SI'

        # List of emission types
        emissions = ['co2', 'nox', 'so2']

        # Units that each emission starts in
        start_units = {
            'co2': 'tons',
            'nox': 'tons',
            'so2': 'tons'
        }

        for emiss in emissions:
            # Existing imperial column name and si column name to add
            imperial_col = '{}mass_{}'.format(emiss, start_units[emiss])
            si_col = '{}mass_kg'.format(emiss)

            df[si_col] = self.unit_conversion(
                value=df[imperial_col],
                start_unit=start_units[emiss],
                final_unit='kg')

    def unit_conversion(self, value, start_unit, final_unit):
        """
        Convert a value from one unit to another (e.g. short tons to kg)

        inputs:
            value: numeric or array-like
            start_unit: str (kg, tons, lbs)
            final_unit: str (kg, tons, lbs)

        returns:
            converted_value: numeric or array-like
        """
        # All values are for conversion to kg
        convert_dict = {
            'kg' : 1.,
            'tons' : 907.1847,
            'lbs' : 0.453592
        }

        # Convert inputs to kg, then to final unit type
        kg = value * convert_dict[start_unit]
        converted_value = kg / convert_dict[final_unit]

        return converted_value


def download_cems(years=CEMS_YEARS, months=None, states=None):

    fn = 'epa_emissions_{}.parquet'.format(DATA_DATE)
    path = DATA_PATHS['epa_emissions'] / fn
    if not path.exists():
        DATA_PATHS['epa_emissions'].mkdir(exist_ok=True, parents=True)

        # cems = CEMS(CEMS_BASE, CEMS_EXT, months=months, states=states)
        # df = cems.fetch_cems_data(years)

        df_list = Parallel(n_jobs=-1)(
            delayed(CEMS(CEMS_BASE, CEMS_EXT).fetch_cems_data)([year])
            for year in years
        )
        df = pd.concat(df_list)

        rename_cols(df)
        df.to_parquet(path, index=False)
    else:
        print("CEMS data has already been downloaded")


if __name__ == "__main__":
    download_cems()
