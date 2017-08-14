# -*- coding: utf-8 -*-

import os
from os.path import join, abspath, normpath, dirname, split
import pandas as pd
from src.util.utils import getParentDir

def get_annual_plants(year,
                      website='https://www.eia.gov/electricity/data/eia923/'):
    """
    Download the EIA-923 file for a given year if it doesn't already exist,
    and extract a list of plant ids for facilities that report annually. This
    function assumes that EIA is continuing to use the same structure for
    links.

    inputs:
        year: (int) year of data to download
        website: (str) the website for EIA-923 data, which is used when
            downloading zip files

    ouputs:
        annual_id: a Pandas Series with plant ids
    """
    from urllib import urlretrieve
    import glob
    import zipfile

    unzip_path = None

    # Get the project top-level path
    ap = abspath(__file__)
    top_path = getParentDir(dirname(ap), level=2)

    # Make folder if it doesn't exist
    path = join(top_path, 'Data storage', 'EIA downloads')
    if not os.path.exists(path):
        os.mkdir(path)

    # Download the 923 zip file if it doesn't exist
    fname = 'f923_{}.zip'.format(year)
    existing_zips = [split(x)[-1] for x in glob.glob(join(path, '*.zip'))]
    save_path = join(path, fname)
    if fname not in existing_zips:
        url = website + 'xls/{}'.format(fname)
        urlretrieve(url, filename=save_path)

    # See if the unzipped folder exists. If not, unzip the file
    unzip_path = join(path, fname.split('.')[0])
    if not os.path.exists(unzip_path):
        # Extract the zipfile into new folder if a filename contains "Final"
        z_file = zipfile.ZipFile(save_path)
        z_names = z_file.namelist()
        if 'Final' in [segment for x in z_names for segment in x.split('_')]:
            z_file.extractall(unzip_path)
        else:
            raise ValueError('Final data is not available for {}'.format(year))

    # Read the sheet "Page 6 Plant Frame" from the appropriate file.
    year_fn = glob.glob(join(unzip_path, '*Schedules_2*'))[0]
    df = pd.read_excel(year_fn, sheetname='Page 6 Plant Frame', header=4)

    # Column names in EIA documents can have line breaks and extra spaces
    df.columns = [col.lower().replace('\n', ' ').strip() for col in df.columns]

    # Get the plant ids for just plants that report annually
    annual_plants = df.loc[df['reporting frequency'] == 'A', 'plant id']
    annual_plants = (annual_plants.drop_duplicates()
                                  .reset_index(drop=True))

    return annual_plants
