import os
from os.path import join, normpath

def getParentDir(path, level=1):
    return normpath(join(path, *([".."] * level)))
