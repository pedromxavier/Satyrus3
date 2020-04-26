#!/usr/env/python
""" :: Sat Test ::
    ==============
"""
## Standard Library
import re
import random
from functools import wraps

## Local
from satyrus.sat_core import load, stderr, stdsys
from satyrus.sat_types.error import SatError

class SatTestError(SatError):
    TITLE = 'Test Error'

class SatTest:

    source = load('source.sat')

    tests = {'parser', 'types'}

    @classmethod
    def get_tests(cls):
        for name in cls.tests:
            yield getattr(cls, name)

    @classmethod
    def parser(cls, *args, **kwargs):
        stdsys << "sat_parser :: SatParser"
        from satyrus.sat_parser import SatParser

        parser = SatParser(cls.source)

        cls.bytecode = parser.parse()

        if cls.bytecode is None:
            raise SatTestError('Parser bytecode is ´None´')
        
        for line in parser.bytecode:
            print(line)

    @classmethod
    def types(cls, *args, **kwargs):
        code = 0

        stdsys << "sat_types :: Number"
        
        ## Module Import
        try:
            from satyrus.sat_types import Number
            stdsys[1] << "Module import OK"
        except:
            stderr[1] << "Module import FAILED"
            return 1

        ## Object Instatiation
        try:
            _x = [random.random() + 0.1 for _ in range(cls.N)]
            _y = [random.random() + 0.1 for _ in range(cls.N)]
            x = [Number(value) for value in _x]  
            y = [Number(value) for value in _y]
            stdsys[1] << "Object Instatiation OK"
        except:
            stderr[1] << "Object Instatiation FAILED"
            return 1

        ## Arithmetic Operators
        try:
            for i in range(cls.N):
                assert cls.is_close((x[i] + y[i]), (_x[i] + _y[i]))
                assert cls.is_close((x[i] - y[i]), (_x[i] - _y[i]))
                assert cls.is_close((x[i] * y[i]), (_x[i] * _y[i]))
                assert cls.is_close((x[i] / y[i]), (_x[i] / _y[i]))
            else:
                stdsys[1] << "Arithmetic Operators OK"
        except:
            stderr[1] << "Arithmetic Operators FAILED"
            code = 1
        
        ## Logical Operators
        try:
            for i in range(cls.N):
                assert cls.is_close((~x[i]), (1 - _x[i]))
                assert cls.is_close((~y[i]), (1 - _y[i]))
                assert cls.is_close((x[i] & y[i]), (_x[i] * _y[i]))
                assert cls.is_close((x[i] | y[i]), (_x[i] + _y[i] - _x[i] * _y[i]))
                assert cls.is_close((x[i] ^ y[i]), (_x[i] + _y[i] - 2 * _x[i] *_y[i]))
            else:
                stdsys[1] << "Logical Operators OK"
        except:
            stderr[1] << "Logical Operators FAILED"
            code = 1

        return code

    @classmethod
    def is_close(x, y, tol=1E-8):
        return abs(float(x) - float(y)) < tol

    @classmethod
    def main(cls, *args, **kwargs):
        for callback in cls.get_tests():
            try:
                if callback(cls, *args, **kwargs):
                    raise SatTestError
                stdsys << ":: Success ::"
            except SatTestError:
                stderr << ':: Failure ::'
            finally:
                print()