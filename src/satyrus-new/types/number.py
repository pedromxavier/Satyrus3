# Standard Library
import decimal
import numbers
import re

# Local
from .expr import Expr
from ..error import SatValueError


class Number(Expr, decimal.Decimal):
    """"""

    context = decimal.getcontext()
    context.prec = 16

    regex = re.compile(r"(\.[0-9]*[1-9])(0+)|(\.0*)$")

    @classmethod
    def numeric(cls, x: object) -> bool:
        return isinstance(x, numbers.Real)

    def __init__(self, value: numbers.Real):
        pass

    def __str__(self):
        return self.regex.sub(r"\1", decimal.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

    def __abs__(self):
        return Number(decimal.Decimal.__abs__(self))

    def __int__(self):
        return decimal.Decimal.__int__(self)

    def __float__(self):
        return decimal.Decimal.__float__(self)

    ## Comparison
    def _GT_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__gt__(self, other))
        else:
            return NotImplemented

    def _GE_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__ge__(self, other))
        else:
            return NotImplemented

    def _LT_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__lt__(self, other))
        else:
            return NotImplemented

    def _LE_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__le__(self, other))
        else:
            return NotImplemented

    def _EQ_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__eq__(self, other))
        else:
            return NotImplemented

    def _NE_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__ne__(self, other))
        else:
            return NotImplemented

    ## Arithmetic
    def _ADD_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__add__(self, other))
        elif self == Number(0):
            return other
        else:
            return NotImplemented

    def _RADD_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__radd__(self, other))
        elif self == Number(0):
            return other
        else:
            return NotImplemented

    def _SUB_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__sub__(self, other))
        elif self == Number(0):
            return -other
        else:
            return NotImplemented

    def _RSUB_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__rsub__(self, other))
        elif self == Number(0):
            return other
        else:
            return NotImplemented

    def _MUL_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__mul__(self, other))
        elif self == Number(0):
            return Number(0)
        elif self == Number(1):
            return other
        else:
            return NotImplemented

    def _RMUL_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__rmul__(self, other))
        elif self == Number(0):
            return Number(0)
        elif self == Number(1):
            return other
        else:
            return NotImplemented

    def _DIV_(self, other):
        if self.numeric(other):
            if other != Number(0):
                return Number(decimal.Decimal.__truediv__(self, other))
            else:
                raise SatValueError("Division by zero.", target=other)
        elif self == Number(0):
            return Number(0)
        else:
            return NotImplemented

    def _RDIV_(self, other):
        if self == Number(0):
            raise SatValueError("Division by zero.", target=self)
        elif self == Number(1):
            return other
        elif self.numeric(other):
            return Number(decimal.Decimal.__truediv__(other, self))
        else:
            return NotImplemented

    def _MOD_(self, other):
        if self.numeric(other):
            if other != Number(0):
                return Number(decimal.Decimal.__mod__(self, other))
            else:
                raise SatValueError("Division by zero.", target=other)
        elif self == Number(0):
            return Number(0)
        else:
            return NotImplemented

    def _RMOD_(self, other):
        if self == Number("0"):
            raise SatValueError("Division by zero.", target=self)
        elif self.numeric(other):
            return Number(decimal.Decimal.__truediv__(other, self))
        else:
            return NotImplemented

    def _AND_(self, other):
        if self.numeric(other):
            return Number(self._MUL_(other))
        elif self == Number(1):
            return other
        elif self == Number(0):
            return self
        else:
            return NotImplemented

    def _RAND_(self, other):
        if self.numeric(other):
            return Number(other._MUL_(self))
        elif self == Number(1):
            return other
        elif self == Number(0):
            return self
        else:
            return NotImplemented

    def _OR_(self, other):
        if self.numeric(other):
            return Number((self._ADD_(other))._SUB_(self._MUL_(other)))
        elif self == Number(1):
            return self
        elif self == Number(0):
            return other
        else:
            return NotImplemented

    def _ROR_(self, other):
        if self.numeric(other):
            return Number((self._ADD_(other))._SUB_(self._MUL_(other)))
        elif self == Number(1):
            return self
        elif self == Number(0):
            return other
        else:
            return NotImplemented

    def _XOR_(self, other):
        if self.numeric(other):
            return Number(
                (self._ADD_(other))._SUB_(Number("2")._MUL_(self)._MUL_(other))
            )
        else:
            return NotImplemented

    def _RXOR_(self, other):
        if self.numeric(other):
            return Number(
                (self._ADD_(other))._SUB_(Number("2")._MUL_(self)._MUL_(other))
            )
        else:
            return NotImplemented

    def _IMP_(self, other):
        if self.numeric(other):
            return Number((self._NOT_())._OR_(other))
        elif self == Number(0):
            return Number(1)
        elif self == Number(1):
            return other
        else:
            return NotImplemented

    def _RIMP_(self, other):
        if self.numeric(other):
            return Number(self._OR_(other._NOT_()))
        elif self == Number(1):
            return self
        elif self == Number(0):
            return other._NOT_()
        else:
            return NotImplemented

    def _IFF_(self, other):
        if self.numeric(other):
            return Number((self._NOT_())._AND_(other._NOT_())._OR_(self._AND_(other)))
        elif self == Number(1):
            return other
        elif self == Number(0):
            return other._NOT_()
        else:
            return NotImplemented

    def _NOT_(self):
        return Number(Number(1)._SUB_(self))

    def _NEG_(self):
        return Number(decimal.Decimal.__neg__(self))

    ## Aliases
    def __add__(self, other):
        return self._ADD_(other)

    def __sub__(self, other):
        return self._SUB_(other)

    def __neg__(self):
        return self._NEG_()

    def __mul__(self, other):
        return self._MUL_(other)

    def __eq__(self, other):
        return self._EQ_(other)

    def __ne__(self, other):
        return self._NE_(other)

    def __lt__(self, other):
        return self._LT_(other)

    def __le__(self, other):
        return self._LE_(other)

    def __gt__(self, other):
        return self._GT_(other)

    def __ge__(self, other):
        return self._GE_(other)

    @classmethod
    def prec(cls, value: int = None) -> int:
        if value is not None:
            cls.context.prec = value
        return int(cls.context.prec)

    @property
    def is_int(self) -> bool:
        return self == decimal.Decimal.__floordiv__(self, 1)


__all__ = ["Number"]