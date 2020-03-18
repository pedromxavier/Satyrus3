from .expr import Expr

## :: Logical ::
from .symbols.tokens import T_AND, T_OR, T_XOR, T_NOT, T_IMP, T_RIMP, T_IFF

## :: Aritmetical ::
from .symbols.tokens import T_ADD, T_SUB, T_MUL, T_DIV

## :: Comparison ::
from .symbols.tokens import T_EQ, T_LE, T_LT, T_GE, T_GT

## :: Indexing ::
from .symbols.tokens import T_IDX

class SatType(object):

    ## :: Logical ::
    def __and__(self, b):
        return Expr(T_AND, self, b)

    def __rand__(self, b):
        return Expr(T_AND, b, self)

    def __or__(self, b):
        return Expr(T_OR, self, b)

    def __ror__(self, b):
        return Expr(T_OR, b, self)

    def __xor__(self, b):
        return Expr(T_XOR, self, b)

    def __rxor__(self, b):
        return Expr(T_XOR, b, self)

    def __not__(self):
        return Expr(T_NOT, self)

    def __iff__(self, b):
        return Expr(T_IFF, self, b)

    def __imp__(self, b):
        return Expr(T_IMP, self, b)

    def __rimp__(self, b):
        return Expr(T_RIMP, self, b)

    ## :: Comparison ::
    def __eq__(self, b):
        return Expr(T_EQ, self, b)

    def __le__(self, b):
        return Expr(T_LE, self, b)

    def __lt__(self, b):
        return Expr(T_LT, self, b)

    def __ge__(self, b):
        return Expr(T_GE, self, b)

    def __gt__(self, b):
        return Expr(T_GT, self, b)

    ## :: Aritmetic ::
    def __neg__(self):
        return Expr(T_SUB, self)

    def __pos__(self):
        return Expr(T_ADD, self)

    def __mul__(self, b):
        return Expr(T_MUL, self, b)

    def __rmul__(self, b):
        return Expr(T_MUL, b, self)

    def __add__(self, b):
        return Expr(T_ADD, self, b)

    def __radd__(self, b):
        return Expr(T_ADD, b, self)

    def __sub__(self, b):
        return Expr(T_SUB, self, b)

    def __rsub__(self, b):
        return Expr(T_SUB, b, self)

    def __truediv__(self, b):
        return Expr(T_DIV, self, b)

    def __rtruediv__(self, b):
        return Expr(T_DIV, b, self)

    ## :: Indexing ::
    def __idx__(self, b):
        return Expr(T_IDX, self, b)

    ## :: Alias for NOT '~' ::
    def __invert__(self):
        return self.__not__()

    @property
    def copy(self):
        return self

    @property
    def is_expr(self):
        return type(self) is Expr