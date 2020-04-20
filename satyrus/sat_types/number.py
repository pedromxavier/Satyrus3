""" :: Number ::
    ============
"""
## Standard Library
import decimal
import re
from functools import wraps

## Local
from .main import SatType
from ..sat_core import keep_type
from .symbols.tokens import T_DICT

@keep_type({f"__{name.lower()}__" for name in T_DICT})
class Number(SatType, decimal.Decimal):

    context = decimal.getcontext()
    context.prec = 16

    regex = re.compile(r'(\.[0-9]*[1-9])(0+)|(\.0*)$')

    def __init__(self, value):
        SatType.__init__(self)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.regex.sub(r'\1', decimal.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

    def __int__(self):
        INT = decimal.Decimal.__int__(self)
        if (INT - self) == 0:
            return INT
        else:
            raise TypeError('Number is not an integer.')

    def __and__(self, other):
        return self * other

    def __or__(self, other):
        return (self + other) - (self * other)

    def __xor__(self, other):
        return (self + other) - (2 * self * other)

    def __imp__(self, other):
        return ~(self & ~other)

    def __rimp__(self, other):
        return ~(~self & other)
        
    def __iff__(self, other):
        return (~self & ~other) | (self & other)

    def __not__(self):
        return Number(1) - self

    @classmethod
    def prec(cls, value : int = None):
        if value is None:
            return cls.context.prec
        else:
            cls.context.prec = value

    @property
    def is_int(self):
        return bool((decimal.Decimal.__int__(self) - self) == 0)

    @property
    def as_int(self):
        return int(self)


Number.TRUE = Number('1')
Number.FALSE = Number('0')