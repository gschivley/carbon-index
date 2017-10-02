import os
from os.path import join, normpath
import pandas as pd

def getParentDir(path, level=1):
    return normpath(join(path, *([".."] * level)))

def rename_cols(df, custom=None):
    'If custom, use the custom dictionary'
    if custom:
        df.rename(columns=custom)
    else:
        # Make all columns lowercase
        df.columns = df.columns.str.lower()

        # Replace ORISPL_CODE with plant id
        replace_dict = {'ORISPL_CODE': 'plant id'}

        df.rename(columns=replace_dict)
    pass

def test_function():
    print('this is a test function')
