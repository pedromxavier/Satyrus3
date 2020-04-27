""" :: Sat Types ::
    ===============
"""
## Standard Library
from sys import intern
from functools import wraps

## Local
from satlib import join
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
    def __new__(cls, head, *tail):
        return tuple.__new__(cls, (head, *tail))

    def __init__(self, head, *tail):
        SatType.__init__(self)
        self._var_stack = None

    def __str__(self):
        return join(' ', self)

    def __repr__(self):
        return f"Expr({join(', ', self)})"

    def __solve__(self):
        raise NotImplementedError('A problem to solve.')

    def __hash__(self):
        """ This hash function identifies uniquely each expression.

        """
        return tuple.__hash__(self)

    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return self[1:]

    @property
    def copy(self):
        return Expr(self.head, *[p.copy for p in self.tail])

    @property
    def var_stack(self):
        if self._var_stack is None:
            self._var_stack = set()
            for value in self.tail:
                if type(value) is Expr:
                    self._var_stack.update(value.var_stack)
                elif type(value) is Var:
                    self._var_stack.add(value)
            return self._var_stack
        else:
            return self._var_stack

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

class Var(SatType, str):

    __ref__ = {} # works as 'intern'

    def __new__(cls, name : str):
        if name not in cls.__ref__:
            obj = str.__new__(cls, name)
            cls.__ref__[name] = obj
        return cls.__ref__[name]

    def __init__(self, name : str):
        SatType.__init__(self)

    def __hash__(self):
        return str.__hash__(self)

    def __repr__(self):
        return f"Var('{self}')"

    def __idx__(self, idx : tuple):
        return Var(f"{self}_{'_'.join(map(str, idx))}")