""" :: Sat Types ::
    ===============
"""
## Standard Library
import decimal
import re
from sys import intern
from functools import wraps

## Local
from ...satlib import join, keep_type
from .error import SatValueError
from .symbols.tokens import T_DICT, T_IDX, T_AND, T_OR, T_MUL, T_ADD, T_SUB

class MetaSatType(type):

    ATTRS = {f"__{name.lower()}__" : T_DICT[name] for name in T_DICT}

    regex = re.compile(r"__r[a-zA-Z]+__")

    @staticmethod
    def null_func(*args):
        return NotImplemented

    def __new__(cls, name, bases, attrs):
        for name, token in cls.ATTRS.items():
            if name in attrs:
                callback = attrs[name]
            else:
                callback = cls.null_func

            attrs[name] = cls.magic(token, callback, swap=(cls.regex.match(name) is not None))

        return type(name, bases, attrs)

    @classmethod
    def magic(cls, token, callback, swap=False):
        """
        """
        @wraps(callback)
        def new_callback(*args):
            answer = callback(*args)
            if answer is NotImplemented:
                if swap:
                    return Expr(token, *args[::-1])
                else:
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

    NEUTRAL = {}
    NULL = {}

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
    def calc(cls, expr):
        """
        """
        return cls.back_apply(expr, (lambda item: cls.RULES[item.head](*item.tail) if (type(item) is cls) else item))

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
    def _simplify(cls, expr):
        if type(expr) is Expr and expr.head in cls.ASSOCIATIVE:
            tail = []
            for p in expr.tail:
                if type(p) is Number:
                    if p == cls.NULL[expr.head]: ## null element
                        return cls.NULL[expr.head]
                    elif p == cls.NEUTRAL[expr.head]:
                        continue
                    else:
                        tail.append(p)
                else:
                    tail.append(p)

            if len(tail) == 0:
                return cls.NULL[expr.head]

            elif len(tail) == 1:
                return expr.tail[0]

            else:
                return cls(expr.head, *tail)
        else:
            return expr


    @classmethod
    def simplify(cls, expr):
        if type(expr) is cls:
            return cls.back_apply(expr, cls._simplify)
        else:
            return expr

    @classmethod
    def associate(cls, expr):
        if type(expr) is cls:
            return cls.back_apply(expr, cls._associate)
        else:
            return expr

    @classmethod
    def _associate(cls, expr):
        if type(expr) is Expr and expr.head in cls.ASSOCIATIVE:
            if len(expr.tail) == 0:
                return cls.NULL[expr.head]
            elif len(expr.tail) == 1:
                return expr.tail[0]
            tail = []
            for p in expr.tail:
                if type(p) is cls: ## is an expression
                    if p.head == expr.head:
                        tail.extend(p.tail)
                        continue
                tail.append(p)
            else:
                return cls(expr.head, *tail)
        else:
            return expr
            
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

        expr = func(expr, *args, **kwargs)

        if type(expr) is cls:
            tail = [cls.apply(p, func, *args, **kwargs) for p in expr.tail]
            return cls(expr.head, *tail)
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

    @classmethod
    def classmethod(cls, func: callable):
        """ >>> @Expr.property
            ... def func(expr):
            ...     ...
            ...     return expr.attr

            >>> e = Expr(...)
            >>> e.func()
            e.attr
        """
        setattr(cls, func.__name__, classmethod(func))
        return getattr(cls, func.__name__)




class Number(SatType, decimal.Decimal, metaclass=MetaSatType):
    """ :: Number ::
        ============
    """
    context = decimal.getcontext()
    context.prec = 16

    regex = re.compile(r'(\.[0-9]*[1-9])(0+)|(\.0*)$')

    NUMERIC_TYPES = {int, float, decimal.Decimal}

    @classmethod
    def numeric(cls, x: object) -> bool:
        return type(x) is cls or type(x) in cls.NUMERIC_TYPES

    def __init__(self, value):
        SatType.__init__(self)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.regex.sub(r'\1', decimal.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

    def __int__(self):
        return decimal.Decimal.__int__(self)

    def __float__(self):
        return decimal.Decimal.__float__(self)

    ## Comparison
    def __gt__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__gt__(self, other))
        else:
            return NotImplemented
    
    def __ge__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__ge__(self, other))
        else:
            return NotImplemented
    
    def __lt__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__lt__(self, other))
        else:
            return NotImplemented

    def __le__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__le__(self, other))
        else:
            return NotImplemented

    def __eq__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__eq__(self, other))
        else:
            return NotImplemented

    def __add__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__add__(self, other))
        elif self == Number('0'):
            return other
        else:
            return NotImplemented

    def __radd__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__radd__(self, other))
        elif self == Number('0'):
            return other
        else:
            return NotImplemented

    def __sub__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__sub__(self, other))
        elif self == Number('0'):
            return (-other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__rsub__(self, other))
        elif self == Number('0'):
            return other
        else:
            return NotImplemented

    def __mul__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__mul__(self, other))
        elif self == Number('0'):
            return Number('0')
        elif self == Number('1'):
            return other
        else:
            return NotImplemented

    def __rmul__(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__rmul__(self, other))
        elif self == Number('0'):
            return Number('0')
        elif self == Number('1'):
            return other
        else:
            return NotImplemented

    def __and__(self, other):
        if self.numeric(other):
            return Number(self * other)
        elif self == Number.T:
            return other
        elif self == Number.F:
            return Number.F
        else:
            return NotImplemented

    def __rand__(self, other):
        if self.numeric(other):
            return Number(other * self)
        elif self == Number.T:
            return other
        elif self == Number.F:
            return Number.F
        else:
            return NotImplemented

    def __or__(self, other):
        if self.numeric(other):
            return Number((self + other) - (self * other))
        elif self == Number.T:
            return Number.T
        elif self == Number.F:
            return other
        else:
            return NotImplemented

    def __ror__(self, other):
        if self.numeric(other):
            return Number((self + other) - (self * other))
        elif self == Number.T:
            return Number.T
        elif self == Number.F:
            return other
        else:
            return NotImplemented

    def __xor__(self, other):
        if self.numeric(other):
            return Number((self + other) - (2 * self * other))
        else:
            return NotImplemented

    def __rxor__(self, other):
        if self.numeric(other):
            return Number((self + other) - (2 * self * other))
        else:
            return NotImplemented

    def __imp__(self, other):
        if self.numeric(other):
            return Number((~self) | other)
        elif self == Number.F:
            return Number.T
        elif self == Number.T:
            return other
        else:
            return NotImplemented

    def __rimp__(self, other):
        if self.numeric(other):
            return Number(self | (~other))
        elif self == Number.T:
            return Number.T
        elif self == Number.F:
            return (~other)
        else:
            return NotImplemented
        
    def __iff__(self, other):
        if self.numeric(other):
            return Number((~self & ~other) | (self & other))
        elif self == Number.T:
            return other
        elif self == Number.F:
            return (~other)
        else:
            return NotImplemented

    def __not__(self):
        return Number(Number('1') - self)

    def __neg__(self):
        return Number(decimal.Decimal.__neg__(self))

    @classmethod
    def prec(cls, value : int = None) -> int:
        if value is not None:
            cls.context.prec = value
        return int(cls.context.prec)
        
    @property
    def is_int(self) -> bool:
        return ((int(self) - float(self)) == 0)

Number.T = Number('1')
Number.F = Number('0')

class Var(SatType, str):

    def __init__(self, name : str):
        SatType.__init__(self)

    def __hash__(self):
        return str.__hash__(self)

    def __repr__(self):
        return f"Var('{self}')"

    def __idx__(self, idx):
        if type(idx) is Number:
            if idx.is_int:
                return Var(f"{self}_{idx}")
            else:
                raise SatValueError(f"Invalid non-integer index {idx}", target=idx)
        else:
            return Expr(T_IDX, self, idx)