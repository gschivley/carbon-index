import os
from os.path import join, abspath, normpath, dirname, split
import pandas as pd

def getParentDir(path, level=1):
    return normpath(join(path, *([".."] * level)))
