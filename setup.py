""" :: Setup ::
    ===========
"""

## Standard Library
import os
import sys

## Local
from install import installer

## Tells installer where we are.
installer.init(os.getcwd())

## This will eventually invoke setuptools.setup(**kwargs)
installer.install()