from .main import SatType

import decimal
import re

decimal.context = decimal.getcontext()
decimal.context.traps[decimal.FloatOperation] = True
decimal.context.prec = 16

class Number(SatType, decimal.Decimal):

    REGEX = re.compile(r'(\.[0-9]*[1-9])(0+)|(\.0*)$')

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, b):
        try:
            return Number(dcm.Decimal.__eq__(self, b))
        except:
            return SatType.__eq__(self, b)

    def __le__(self, b):
        try:
            return Number(dcm.Decimal.__le__(self, b))
        except:
            return SatType.__le__(self, b)

    def __lt__(self, b):
        try:
            return Number(dcm.Decimal.__lt__(self, b))
        except:
            return SatType.__lt__(self, b)

    def __ge__(self, b):
        try:
            return Number(dcm.Decimal.__ge__(self, b))
        except:
            return SatType.__ge__(self, b)

    def __gt__(self, b):
        try:
            return Number(dcm.Decimal.__gt__(self, b))
        except:
            return SatType.__gt__(self, b)

    def __str__(self):
        return self.REGEX.sub(r'\1', decimal.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

    def __neg__(self):
        try:
            return Number(dcm.Decimal.__neg__(self))
        except:
            return SatType.__neg__(self)

    def __pos__(self):
        try:
            return Number(dcm.Decimal.__pos__(self))
        except:
            return SatType.__pos__(self)

    def __mul__(self, b):
        try:
            return Number(dcm.Decimal.__mul__(self, b))
        except:
            return SatType.__mul__(self, b)

    def __rmul__(self, b):
        try:
            return Number(dcm.Decimal.__rmul__(self, b))
        except:
            return SatType.__rmul__(self, b)

    def __add__(self, b):
        try:
            return Number(dcm.Decimal.__add__(self, b))
        except:
            return SatType.__add__(self, b)

    def __radd__(self, b):
        try:
            return Number(dcm.Decimal.__radd__(self, b))
        except:
            return SatType.__radd__(self, b)

    def __sub__(self, b):
        try:
            return Number(dcm.Decimal.__sub__(self, b))
        except:
            return SatType.__sub__(self, b)

    def __rsub__(self, b):
        try:
            return Number(dcm.Decimal.__rsub__(self, b))
        except:
            return SatType.__rsub__(self, b)

    def __truediv__(self, b):
        try:
            return Number(dcm.Decimal.__truediv__(self, b))
        except:
            return SatType.__truediv__(self, b)

    def __rtruediv__(self, b):
        try:
            return Number(dcm.Decimal.__rtruediv__(self, b))
        except:
            return SatType.__rtruediv__(self, b)

    def __and__(self, b):
        try:
            return self * b
        except:
            return SatType.__and__(self, b)

    def __or__(self, b):
        try:
            return (self + b) - (self * b)
        except:
            return SatType.__or__(self, b)

    def __xor__(self, b):
        try:
            return (self + b) - (2 * self * b)
        except:
            return SatType.__xor__(self, b)

    def __imp__(self, b):
        try:
            return ~(self & ~b)
        except:
            return SatType.__imp__(self, b)

    def __rimp__(self, b):
        try:
            return ~(~self & b)
        except:
            return SatType.__rimp__(self, b)

    def __iff__(self, b):
        try:
            return (~self & ~b) | (self & b)
        except:
            return SatType.__iff__(self, b)

    def __not__(self):
        try:
            return self.__invert__()
        except:
            return SatType.__not__(self)

    def __invert__(self):
        try:
            return 1 - self
        except:
            return SatType.__invert__(self)

Number.TRUE = Number('1')
Number.FALSE = Number('0')