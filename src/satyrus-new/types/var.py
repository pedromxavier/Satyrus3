from .expr import Expr
from ..error import SatValueError
from ..satlib import Source

# pylint:disable=no-self-argument
class Var(Expr, str):
    """
    """
    def __new__(cls, name: str, *, source: Source = None, lexpos: int = None):
        return str.__new__(cls, name)

    def __init__(self, name: str, *, source: Source = None, lexpos: int = None):
        Expr.__init__(self, None, source=source, lexpos=lexpos)

    def _IDX_(s, i: tuple):
        r = str(s)
        while i:
            j, *i = i ## pick first
            if j.is_number:
                if j > 0 and j.is_int:
                    r = f"{r}_{j}"
                else:
                    raise SatValueError(f"Index must be a positive integer, not '{j}'.", target=j)
            else:
                return Expr._IDX_(Var(r), j, *i)
        else:
            return Var(r)