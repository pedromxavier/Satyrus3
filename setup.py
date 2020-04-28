""" :: Setup ::
    ===========
"""

## Standard Library
import os
import sys

## Local
from install import installer

installer.init(os.getcwd())
installer.install()