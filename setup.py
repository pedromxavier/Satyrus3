""" :: Setup ::
    ===========
"""

## Standard Library
import os

## Local
from install import installer

installer.init(os.getcwd())
installer.install()