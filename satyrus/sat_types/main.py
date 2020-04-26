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

    def __init__(self):
        self.lexinfo = {
            'lineno' : None,
            'lexpos' : None,
            'chrpos' : None,
            'source' : None,
        }

    @property
    def lineno(self):
        return self.lexinfo['lineno']

    @property
    def lexpos(self):
        return self.lexinfo['lexpos']

    @property
    def chrpos(self):
        return self.lexinfo['chrpos']

    @property
    def source(self):
        return self.lexinfo['source']

    ## Alias for __not__.
    def __not__(self):
        return NotImplemented

    def __invert__(self):
        return self.__not__()

    @classmethod
    def check_type(cls, obj):
        if not isinstance(obj, cls):
            raise TypeError(f'Object of type {type(obj)} found.')

    @property
    def copy(self):
        return self

    @property
    def is_expr(self):
        return type(self) is Expr

    @property
    def is_int(self):
        print(self)
        raise NotImplementedError
    
    @property
    def as_int(self):
        try:
            return int(self)
        except:
            raise NotImplementedError

class Expr(SatType, tuple):
    """ :: Expr ::
        ==========

        This is one of the core elements of the system. This is used to represent ASTs.
    """
    HASH_SIDE = {}

    RULES = {}

    TABLE = {}

    GROUPS = {}

    FORMATS = {}

    FORMAT_FUNCS = {}

    NEED_PAR = set()

    SOLVE_FUNCS = []

    def __new__(cls, head, *tail):
        return tuple.__new__(cls, (head, *tail))

    def __init__(self, head, *tail):
        SatType.__init__(self)

    def __str__(self):
        if self.head in self.FORMAT_FUNCS:
            return self.FORMAT_FUNCS[self.head](self)
        elif self.head in self.FORMATS:
            return self.FORMATS[self.head].format(*self)
        else:
            return self.join(' ').format(*self)

    def __repr__(self):
        return f"Expr({self.join(', ').format(*map(repr, self))})"

    def __solve__(self):
        raise NotImplementedError('A problem to solve.')

    def __hash__(self):
        """ This hash function identifies uniquely each expression.

        """
        return tuple.__hash__(self)

    def join(self, glue=" "):
        return glue.join([f"{{{i}}}" for i in range(len(self))])

    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return self[1:]

    @classmethod
    def _copy_(cls, self):
        return cls(self.head, *[p.copy for p in self.tail])

    @property
    def copy(self):
        return type(self)._copy_(self)

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

    @classmethod
    def apply(cls, func, expr, *args, **kwargs):
        if type(expr) is cls:
            expr = func(expr, *args, **kwargs)
        else:
            return expr

        if type(expr) is cls:
            tail = [cls.apply(func, p, *args, **kwargs) for p in expr.tail]
            expr = cls(expr.head, *tail)
            return expr
        else:
            return expr

    @classmethod
    def back_apply(cls, func, expr, *args, **kwargs):
        if type(expr) is cls:
            tail = [cls.back_apply(func, p, *args, **kwargs) for p in expr.tail]
            expr = cls(expr.head, *tail)
            return func(expr, *args, **kwargs)
        else:
            return expr

    @classmethod
    def from_tuple(cls, tup):
        if type(tup) is tuple:
            return cls(tup[0], *(cls.from_tuple(t) for t in tup[1:]))
        else:
            return tup

    @classmethod
    def to_tuple(cls, expr):
        if type(expr) is cls:
            return tuple(cls.to_tuple(p) for p in expr)
        else:
            return expr

    @classmethod
    def cmp(cls, p, q):
        """ cls.cmp(p, q) -> bool
            Compares both expressions.
        """
        return hash(p) == hash(q)

    @classmethod
    def par(cls, p, q):
        if (type(q) is cls) and (q.head in cls.NEED_PAR) and (p.group != q.group):
            return f"({q})"
        else:
            return f"{q}"