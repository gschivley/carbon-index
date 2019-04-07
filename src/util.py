"""
Small helper functions for use throughout the carbon index

"""
import io
import zipfile

import requests
import pandas as pd


def download_unzip(url, unzip_path):
    """
    Download a zip file from url and extract contents to a given path

    Parameters
    ----------
    url : str
        Valid url to download the zip file
    unzip_path : str or path object
        Destination to unzip the data

    """
    r = requests.get(url)
    content_type = r.headers['Content-Type']
    if 'zip' not in content_type and '-stream' not in content_type:
        print(content_type)
        raise ValueError('URL does not point to valid zip file')

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(path=unzip_path)


def download_save(url, save_path):
    """
    Download a file and save it to a given path

    Parameters
    ----------
    url : str
        Valid url to download the zip file
    save_path : str or path object
        Destination to save the file

    """

    r = requests.get(url)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(r.content)


def add_facility_location(df, label_df, labels=[], merge_how='left'):
    """
    Add location info (lat/lon, state, nerc, or other region) to a dataframe
    with plant ids.

    inputs:
        df (df): a dataframe with plant ids
        label_df (df): a dataframe with plant ids and other columns that
            give the location info for the plant
        labels (list): one or more columns to add to the original dataframe
        merge_how (str): type of merge (inner, left, right)
    """

    merge_cols = ['plant id'] + labels

    # columns to merge on
    on = ['plant id']

    if 'year' in label_df.columns:
        on.append('year')

    df = df.merge(label_df.loc[:, merge_cols], on=on, how=merge_how)

    return df


def add_datetime(df, year='year', month='month'):
    """
    Add a datetime column to a dataframe with year and month columns. Year
    and month can also be part of a MultiIndex.

    Parameters
    ----------
    df : dataframe
        Any dataframe with columns of year and month
    year : str, optional
        Name of the year column (the default is 'year')
    month : str, optional
        Name of the month column (the default is 'month')

    Raises
    ------
    IndexError
        [description]

    """
    if type(df.index) is not pd.MultiIndex:
        df['datetime'] = pd.to_datetime(df[year].astype(str) + '-' +
                                        df[month].astype(str),
                                        format='%Y-%m')
    elif year in df.index.names and month in df.index.names:
        year_vals = df.index.get_level_values(year).astype(str)
        month_vals = df.index.get_level_values(month).astype(str)
        df['datetime'] = pd.to_datetime(year_vals + '-' + month_vals,
                                        format='%Y-%m')

    else:
        raise IndexError('MultiIndex without year and month levels')


def add_quarter(df, year='year', month='month'):
    """
    Add a column with the quarter (1 through 4) of year based on datetime
    values

    Parameters
    ----------
    df : dataframe
        Any dataframe with columns of year and month
    year : str, optional
        Name of the year column (the default is 'year')
    month : str, optional
        Name of the month column (the default is 'month')

    """
    if 'datetime' not in df.columns:
        add_datetime(df, year, month)
    df['quarter'] = df['datetime'].dt.quarter


def rename_cols(df, custom=None):
    'If custom, use the custom dictionary'
    if custom:
        df.rename(columns=custom, inplace=True)
    else:
        # Replace ORISPL_CODE with plant id
        replace_dict = {
            'ORISPL_CODE': 'plant id',
            'orispl': 'plant id'
        }
        df.rename(columns=replace_dict, inplace=True)

        # Make all columns lowercase
        df.columns = df.columns.str.lower()
