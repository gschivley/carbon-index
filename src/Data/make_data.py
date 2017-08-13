# -*- coding: utf-8 -*-

import os
from os.path import join
import pandas as pd
# import zipfile
# # from urllib import urlretrieve, urlopen
# from urllib2 import urlopen
# from cStringIO import StringIO
# import requests


def get_annual_plants(year,
                      website='https://www.eia.gov/electricity/data/eia923/',
                      base_path='~/Documents/Github/index-variability'):
    """
    Download the EIA-923 file for a given year if it doesn't already exist,
    and extract a list of plant ids for facilities that report annually. This
    function assumes that EIA is continuing to use the same structure for
    links.

    inputs:
        year: year of data to download

    ouputs:
        annual_id: a Pandas Series with plant ids
    """
    from urllib import urlretrieve
    import glob
    import zipfile

    # Testing abspath and relpath
    return os.path.abspath(__file__), os.path.relpath(__file__)

    # Make folder if it doesn't exist
    ## How to make this relative to wheever I'm running the function from?
    path = join(os.abspath(base_path), 'Data storage', 'EIA downloads')
    if not os.path.exists(path):
        os.mkdir(path)

    # Download the 923 zip file if it doesn't exist
    fname = 'f923_{}.zip'.format(year)
    existing_zips = glob.glob(path)

    if fname not in existing_zips:
        url = website + 'xls/{}'.format(fname)
        save_path = join(path, fname)
        urlretrieve(url, filename=save_path)

        # Extract the zipfile into new folder if a filename contains "Final"
        z_file = zipfile.ZipFile(save_path)
        z_names = z_file.namelist()
        if 'Final' in [segment for x in names for segment in x.split('_')]:
            unzip_path = join(path, fname.split[0])
            z_file.extractall(unzip_path)
        else:
            raise ValueError('Final data is not available for {}'.format(year))

    # Read the sheet "Page 6 Plant Frame" from the appropriate file.
    year_fn = glob.glob(join(unzip_path, '*Schedules_2*'))

    df = pd.read_excel(year_fn, sheetname='Page 6 Plant Frame', header=4)
    df.columns = [col.lower() for col in df.columns]

    annual_plants = df.loc[df['reporting frequency'] == 'A', 'plant id']
    annual_plants.drop_duplicates(inplace=True)

    return annual_plants
