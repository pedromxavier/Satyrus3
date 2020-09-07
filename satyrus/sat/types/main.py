""" :: Sat Types ::
    ===============
"""
## Standard Library
from sys import intern
from functools import wraps

## Local
from ...satlib import join
from .symbols.tokens import T_DICT

class MetaSatType(type):

    ATTRS = {f"__{name.lower()}__" : T_DICT[name] for name in T_DICT}

    @staticmethod
    def null_func(*args):
        return NotImplemented

    def __new__(cls, name, bases, attrs):
        for name, token in cls.ATTRS.items():
            if name in attrs:
                callback = attrs[name]
            else:
                callback = cls.null_func

            attrs[name] = cls.sat_magic(token, callback)

        return type(name, bases, attrs)

    @classmethod
    def sat_magic(cls, token, callback):
        """
        """
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
        raise NotImplementedError

class Expr(SatType, tuple):
    """ :: Expr ::
        ==========

        This is one of the core elements of the system. This is used to represent ASTs.

        Only basic functionality is implemented here. Context is implemented in `expr.py`
    """
    HASH = {}
    RULES = {}
    TABLE = {}

    GROUPS = {}

    ASSOCIATIVE = set()

    FORMAT_PATTERNS = {}
    FORMAT_FUNCS = {}

    def __new__(cls, head, *tail):
        return tuple.__new__(cls, (head, *tail))

    def __init__(self, head, *tail):
        SatType.__init__(self)
        self._var_stack = None

    def parenthesise(self, child) -> bool:
        if type(child) is not type(self):
            return False
        elif self.head not in self.GROUPS:
            return False
        elif child.head not in self.GROUPS:
            return False
        elif self.GROUPS[self.head] > self.GROUPS[child.head]:
            return True
        else:
            return False

    def __str__(self):
        head = self.head
        tail = [(f"({p})" if self.parenthesise(p) else str(p)) for p in self.tail]
        if head in self.FORMAT_PATTERNS:
            return self.FORMAT_PATTERNS[head].format(head, *tail)
        elif head in self.FORMAT_FUNCS:
            return self.FORMAT_FUNCS[head](head, *tail)
        else:
            return join(" ", [head, *tail])
        

    def __repr__(self):
        return f"Expr({join(', ', self, repr)})"

    def __hash__(self):
        """ This hash function identifies uniquely each expression.
        """
        if self.head in self.HASH:
            return self.HASH[self.head](*self)
        else:
            return tuple.__hash__((self.head, *(hash(p) for p in self.tail)))

    @classmethod
    def rule(cls, token: str):
        def decor(callback):
            cls.RULES[token] = callback
        return decor

    @classmethod
    def solve(cls, expr):
        return cls.apply((lambda item: cls.RULES[expr.head](expr) if type(expr) is cls else expr), expr)

    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return self[1:]

    @property
    def copy(self):
        return Expr(self.head, *[p.copy for p in self.tail])

    @classmethod
    def _associate(cls, expr):
        if expr.head in cls.ASSOCIATIVE:
            tail = []
            for p in expr.tail:
                if type(p) is cls: ## is an expression
                    if p.head == expr.head:
                        tail.extend(p.tail)
                        continue
                tail.append(p)
            return cls(expr.head, *tail)
        else:
            return expr

    @property
    def associate(self):
        return type(self).back_apply(self, self._associate)

    @classmethod
    def transverse(cls, expr, func, *args, **kwargs) -> None:
        """ Transverses expression

            >>> def func(expr, *args, **kwargs):
            ...     ...
            ...     return None
        """
        if type(expr) is cls:
            for p in expr.tail:
                cls.transverse(p, func, *args, **kwargs)
        else:
            func(expr, *args, **kwargs)

    @classmethod
    def seek(cls, expr, func, *args, **kwargs) -> list:
        """ Seeks for tree leaves who satisfy `func`

            >>> def func(expr, *args, **kwargs):
            ...     ...
            ...     return ...
        """
        results = []
        if type(expr) is cls:
            for p in expr.tail:
                results.extend(cls.seek(p, func, *args, **kwargs))
        else:
            if func(expr, *args, **kwargs):
                results.append(expr)
        return results

    @classmethod
    def apply(cls, expr, func, *args, **kwargs):
        """ Forward-applies function `func` to `expr`.

            >>> def func(expr, *args, **kwargs):
            ...    new_expr = ...
            ...    return new_expr
        """
        if type(expr) is cls:
            expr = func(expr, *args, **kwargs)
            if type(expr) is cls:
                tail = [cls.apply(p, func, *args, **kwargs) for p in expr.tail]
                return cls(expr.head, *tail)
            else:
                return expr
        else:
            return expr

    @classmethod
    def back_apply(cls, expr, func, *args, **kwargs):
        """ Back-applies function `func` to `expr`.

            >>> def func(expr, *args, **kwargs):
            ...    new_expr = ...
            ...    return new_expr
        """
        if type(expr) is cls:
            tail = [cls.back_apply(p, func, *args, **kwargs) for p in expr.tail]
            expr = cls(expr.head, *tail)

            ## Apply function to expr.
            return func(expr, *args, **kwargs)
        else:
            return expr

    @classmethod
    def from_tuple(cls, tup: tuple):
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
    def property(cls, func: callable):
        """ >>> @Expr.property
            ... def func(expr):
            ...     ...
            ...     return expr.attr

            >>> e = Expr(...)
            >>> e.func
            e.attr
        """
        setattr(cls, func.__name__, property(func))
        return getattr(cls, func.__name__)

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
        return Var(f"{self}_{join('_', idx)}")