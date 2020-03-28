#!/usr/env/python
""" :: Satyrus III ::
    =================
"""
## Standard Library
import argparse

## Local
from .sat_core import load

class Satyrus:

    @classmethod
    def main(cls, *args, **kwargs):
        source = load(cls.fname)
        return source

    @classmethod
    def init(cls, fname):
        cls.fname = fname