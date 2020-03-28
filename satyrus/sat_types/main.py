""" :: Sat Types ::
    ===============
"""
## Standard Library
from sys import intern
from functools import wraps

## Local
from .symbols.tokens import T_DICT

class MetaSatType(type):

    ATTRS = {f"__{name.lower()}__" : T_DICT[name] for name in T_DICT}

    @staticmethod
    def null_func(*args):
        return NotImplemented

    def __init__(cls, name, bases, attrs):
        for name, token in cls.ATTRS.items():
            if name in attrs:
                callback = attrs[name]
            else:
                callback = cls.null_func

            attrs[name] = cls.sat_magic(token, callback)

    @classmethod
    def sat_magic(cls, token, callback):
        @wraps(callback)
        def new_callback(*args):
            answer = callback(*args)
            if answer is NotImplemented:
                return Expr(token, *args)
            else:
                return answer
        return new_callback

class SatType(metaclass=MetaSatType):
    """ :: SatType ::
        =============

    """

    ## Alias for __not__.
    def __not__(self):
        return NotImplemented

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
        """
        """
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