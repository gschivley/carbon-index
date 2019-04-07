import os
from os.path import join, normpath
import pandas as pd

def getParentDir(path, level=1):
    return normpath(join(path, *([".."] * level)))

def rename_cols(df, custom=None):
    'If custom, use the custom dictionary'
    if custom:
        df.rename(columns=custom, inplace=True)
    else:
        # Replace ORISPL_CODE with plant id
        replace_dict = {'ORISPL_CODE': 'plant id'}
        df.rename(columns=replace_dict, inplace=True)

        # Make all columns lowercase
        df.columns = df.columns.str.lower()

    pass

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
