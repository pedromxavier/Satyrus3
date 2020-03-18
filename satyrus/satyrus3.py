""" Satyrus III 
"""
import argparse

class Satyrus:

    @classmethod
    def main(cls, *args, **kwargs):
        ...

        with open(cls.fname, 'r') as file:
            source = file.read()

        return source

    @classmethod
    def init(cls, fname):
        cls.fname = fname