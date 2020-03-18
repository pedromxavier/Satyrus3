from .core import SatType

import decimal
import re

class Number(SatType, decimal.Decimal):

    REGEX = re.compile(r'(\.[0-9]*[1-9])(0+)|(\.0*)$')

    def __hash__(a):
        return hash(str(a))

    def __eq__(a, b):
        try:
            return Number(dcm.Decimal.__eq__(a, b))
        except:
            return BaseSatType.__eq__(a, b)

    def __le__(a, b):
        try:
            return Number(dcm.Decimal.__le__(a, b))
        except:
            return BaseSatType.__le__(a, b)

    def __lt__(a, b):
        try:
            return Number(dcm.Decimal.__lt__(a, b))
        except:
            return BaseSatType.__lt__(a, b)

    def __ge__(a, b):
        try:
            return Number(dcm.Decimal.__ge__(a, b))
        except:
            return BaseSatType.__ge__(a, b)

    def __gt__(a, b):
        try:
            return Number(dcm.Decimal.__gt__(a, b))
        except:
            return BaseSatType.__gt__(a, b)

    def __str__(self):
        return self.REGEX.sub(r'\1', decimal.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

    def __neg__(a):
        try:
            return Number(dcm.Decimal.__neg__(a))
        except:
            return BaseSatType.__neg__(a, b)

    def __pos__(a):
        try:
            return Number(dcm.Decimal.__pos__(a))
        except:
            return BaseSatType.__pos__(a, b)

    def __mul__(a, b):
        try:
            return Number(dcm.Decimal.__mul__(a, b))
        except:
            return BaseSatType.__mul__(a, b)

    def __rmul__(a, b):
        try:
            return Number(dcm.Decimal.__rmul__(a, b))
        except:
            return BaseSatType.__rmul__(a, b)

    def __add__(a, b):
        try:
            return Number(dcm.Decimal.__add__(a, b))
        except:
            return BaseSatType.__add__(a, b)

    def __radd__(a, b):
        try:
            return Number(dcm.Decimal.__radd__(a, b))
        except:
            return BaseSatType.__radd__(a, b)

    def __sub__(a, b):
        try:
            return Number(dcm.Decimal.__sub__(a, b))
        except:
            return BaseSatType.__sub__(a, b)

    def __rsub__(a, b):
        try:
            return Number(dcm.Decimal.__rsub__(a, b))
        except:
            return BaseSatType.__rsub__(a, b)

    def __truediv__(a, b):
        try:
            return Number(dcm.Decimal.__truediv__(a, b))
        except:
            return BaseSatType.__truediv__(a, b)

    def __rtruediv__(a, b):
        try:
            return Number(dcm.Decimal.__rtruediv__(a, b))
        except:
            return BaseSatType.__rtruediv__(a, b)

    def __and__(a, b):
        try:
            return a * b
        except:
            return BaseSatType.__and__(a, b)

    def __or__(a, b):
        try:
            return (a + b) - (a * b)
        except:
            return BaseSatType.__or__(a, b)

    def __xor__(a, b):
        try:
            return (a + b) - (2 * a * b)
        except:
            return BaseSatType.__xor__(a, b)

    def __imp__(a, b):
        try:
            return ~(a & ~b)
        except:
            return BaseSatType.__imp__(a, b)

    def __rimp__(a, b):
        try:
            return ~(~a & b)
        except:
            return BaseSatType.__rimp__(a, b)

    def __iff__(a, b):
        try:
            return (~a & ~b) | (a & b)
        except:
            return BaseSatType.__iff__(a, b)

    def __not__(a):
        try:
            return a.__invert__()
        except:
            return BaseSatType.__not__(a)

    def __invert__(a):
        try:
            return 1 - a
        except:
            return BaseSatType.__invert__(a)

    @property
    def int(a):
        return bool((a - Number(int(a))) == Number.FALSE)

    @property
    def bool(a):
        return a == Number.TRUE or a == Number.FALSE

Number.TRUE  = Number('1')
Number.FALSE = Number('0')