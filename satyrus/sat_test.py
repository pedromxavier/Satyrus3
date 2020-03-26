#/usr/bin/python3.8
""" :: SATyrus Test File ::
"""
from sat_core import load, stderr
from sat_types import SatError

from functools import wraps

import re

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
    def api(cls, *args, **kwargs):
        return NotImplemented

    @classmethod
    def compiler(cls, *args, **kwargs):
        return NotImplemented

    @classmethod
    def parser(cls, *args, **kwargs):
        from sat_parser import SatParser

        parser = SatParser()

        parser.parse(cls.source)

        if parser.bytecode is None:
            raise SatTestError('Parser bytecode is <None>')
        
        for line in parser.bytecode:
            print(line)

    @classmethod
    def expr(cls, *args, **kwargs):
        return NotImplemented

    @classmethod
    def satyrus(cls, *args, **kwargs):
        return NotImplemented

    @classmethod
    def main(cls, *args, **kwargs):
        for callback in cls.get_tests():
            try:
                answer = callback(cls, *args, **kwargs)
                if answer != NotImplemented:
                    print(answer)
            except SatTestError:
                stderr << ':: Test Failed ::'

if __name__ == '__main__':
    SatTest.main()
