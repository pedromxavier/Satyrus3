from sys import intern
from functools import wraps

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

class Expr(SatType, list):
    """ :: Expr ::
        ==========

        This is one of the core elements of the system. This is used to represent ASTs.
    """
    HASH_SIDE = {}

    RULES = {}

    TABLE = {}

    GROUPS = {}

    FORMATS = {}

    NEED_PAR = set()

    SOLVE_FUNCS = []

    def __init__(self, head, *tail, format=""):
        list.__init__(self, [intern(head), *tail])

        self.format = self._format() if format is None else format

    def __str__(self):
        return self.format.format(*self)

    def __repr__(self):
        return f"Expr({self._format(',')})"

    def __hash__(self):
        side = Expr.HASH_SIDE[self.head]

        if side is None:
            head_hash = hash(self.head)
            tail_hash = sum(hash(p) for p in self.tail)
        elif side is True:
            head_hash = hash(self.head)
            tail_hash = hash(self.tail)
        else:
            head_hash = hash(side)
            tail_hash = hash(self.tail)

        return hash((head_hash, tail_hash))

    def _format(self, glue=" "):
        return glue.join([f"{{{i}}}" for i in range(len(self))])

    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return tuple(self[1:])

    @property
    def copy(self):
        return Expr(self.head, *[p.copy for p in self.tail])

    @classmethod
    def add_solve_func(cls, heads, func):
        @wraps(func)
        def new_func(expr, *args):
            if expr.head in heads:
                return func(expr, *args)
            else:
                return expr
        return new_func

    @classmethod
    def solve_func(cls, heads):
        return lambda func : cls.add_solve_func(heads, func)

    @classmethod
    def add_rule(cls, token, rule):
        @wraps(rule)
        def new_rule(expr):
            return rule(*[p.__solve__() for p in expr.tail])
        cls.RULES[token] = new_rule

    @classmethod
    def rule(cls, token):
        return lambda rule : cls.add_rule(token, rule)

    @staticmethod
    def apply(expr, func, *args, **kwargs):
        if expr.is_expr:
            expr = func(expr, *args, **kwargs)
        else:
            return expr

        if expr.is_expr:
            tail = [Expr.apply(p, func, *args, **kwargs) for p in expr.tail]
            expr = Expr(expr.head, *tail)
            return expr
        else:
            return expr

    @staticmethod
    def back_apply(expr, func, *args, **kwargs):
        if expr.is_expr:
            tail = [Expr.back_apply(p, func, *args, **kwargs) for p in expr.tail]
            expr = Expr(expr.head, *tail)
            return func(expr, *args, **kwargs)
        else:
            return expr

    @staticmethod
    def cmp(A, B):
        return hash(A) == hash(B)

    @staticmethod
    def decode(T):
        return NotImplemented

    @staticmethod
    def encode(expr):
        return NotImplemented

    @staticmethod
    def par(p, q):
        if (q.expr) and (q.head in Expr.NEED_PAR) and (p.group != q.group):
            return f"({q})"
        else:
            return f"{q}"