#!/usr/env/python
""" :: Sat Test ::
    ==============
"""
## Standard Library
import re
from functools import wraps

## Local
from satyrus.sat_core import load, stderr, stdsys
from satyrus.sat_types import SatError

class SatTestError(SatError):
    pass

class SatTest:

    source = load('source.sat')

    locked = {'main', 'source', 'get_tests', 'locked'}

    @classmethod
    def get_tests(cls):
        for name in dir(cls):
            ## Check if the function is a test function.
            if (not re.match(r"\_\_.+\_\_", name)) and (name not in cls.locked):
                yield getattr(cls, name)

    @classmethod
    def parser(cls, *args, **kwargs):
        stdsys << "sat_parser :: SatParser"
        from satyrus.sat_parser import SatParser

        parser = SatParser()

        parser.parse(cls.source)

        if parser.bytecode is None:
            raise SatTestError('Parser bytecode is ´None´')
        
        for line in parser.bytecode:
            print(line)

    @classmethod
    def types(cls, *args, **kwargs):
        stdsys << "sat_types :: Number"
        from satyrus.sat_types import Number

        x = Number('1.20')
        y = Number('-2.7')
        
        print("x =", x)
        print("y =", y)

        print("x + y =", x + y)
        print("x - y =", x - y)
        print("x * y =", x * y)
        print("x / y =", x / y)
        print("x & y =", x & y)

    @classmethod
    def main(cls, *args, **kwargs):
        for callback in cls.get_tests():
            try:
                callback(cls, *args, **kwargs)
                stdsys << ":: Success ::"
            except SatTestError:
                stderr << ':: Failure ::'
            finally:
                print()
