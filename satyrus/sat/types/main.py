""" :: Sat Types ::
    ===============
"""
## Standard Library
import decimal
import re
from sys import intern
from functools import wraps
import itertools as it

## Local
from ...satlib import join, keep_type, trackable
from .error import SatValueError, SatIndexError, SatTypeError
from .symbols.tokens import T_DICT, T_IDX, T_AND, T_OR, T_MUL, T_ADD, T_SUB

class MetaSatType(type):

    ATTRS = {f"_{name.upper()}_" : T_DICT[name] for name in T_DICT}
    REGEX = re.compile(r"_r[A-Z]+_")

    @staticmethod
    def null_func(*args):
        return NotImplemented

    def __new__(cls, name, bases, attrs):
        for name, token in cls.ATTRS.items():
            if name in attrs:
                callback = attrs[name]
            else:
                callback = cls.null_func

            attrs[name] = cls.magic(token, callback, swap=(cls.REGEX.match(name) is not None))

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
                    return Expr(token, *reversed(args))
                else:
                    return Expr(token, *args)
            else:
                return answer
        return new_callback

@trackable
class SatType(metaclass=MetaSatType):
    """ :: SatType ::
        =============

    """

    def __eq__(self, other) -> bool:
        return (hash(self) == hash(other))

    def __ne__(self, other) -> bool:
        return (hash(self) != hash(other))
    
    def _IDX_(self, i: tuple):
        return Expr(T_IDX, self, *i)

    ## Some aliases
    ## pylint: disable=no-member
    def __invert__(self):
        return self._NOT_()

    def __and__(self, other):
        return self._AND_(other)

    def __or__(self, other):
        return self._OR_(other)

    def __xor__(self, other):
        return self._XOR_(other)

    def __add__(self, other):
        return self._ADD_(other)
    
    def __mul__(self, other):
        return self._MUL_(other)

    @property
    def is_int(self):
        return False

    @property
    def copy(self):
        return self

class Expr(SatType, tuple):
    """ :: Expr ::
        ==========

        This is one of the core elements of the system. This is used to represent ASTs.

        Only basic functionality is implemented here. Context is implemented in `expr.py`
    """
    RULES = {}
    TABLE = {}

    GROUPS = {}

    EXPAND = {}
    SIMPLIFY = {}

    ASSOCIATIVE = set()
    COMMUTATIVE = set()

    NEUTRAL = {}
    NULL = {}

    HASH = {}

    FORMAT_FUNCS = {}
    FORMAT_PATTERNS = {}

    def __new__(cls, head, *tail):
        return tuple.__new__(cls, (head, *tail))

    def __init__(self, head, *tail):
        SatType.__init__(self)
        self._hash_ = None

    def parenthesise(self, child: object) -> bool:
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
        if self._hash_ is None:
            hash_key = self.HASH[self.head]
            if hash_key is None:
                self._hash_ = hash((self.head, hash(sum(hash(p) for p in self.tail))))
            elif hash_key == self.head:
                self._hash_ = hash((hash_key, hash(tuple(hash(p) for p in self.tail))))
            else:
                self._hash_ = hash((hash_key, hash(tuple(hash(p) for p in reversed(self.tail)))))
        return self._hash_

    @classmethod
    def rule(cls, token: str):
        def decor(callback):
            cls.RULES[token] = callback
        return decor

    @classmethod
    def calculate(cls, expr) -> SatType:
        """ :: CALCULATE ::
            ===============

            Applies rules as described in `cls.RULES` for each
            expression, in a backward fashion i.e. from leaves
            to root.

            As result, may yield Var, Number or Expr.
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
        """
        """
        return Expr(self.head, *[p.copy for p in self.tail])

    @classmethod
    def expand(cls, expr):
        """
        """
        if type(expr) is cls and expr.head in cls.EXPAND:
            return cls.EXPAND[expr.head](expr.tail)
        else:
            return expr

    @classmethod
    def associate(cls, expr):
        """
        """
        if type(expr) is cls:
            return cls.back_apply(expr, cls._associate)
        else:
            return expr

    @classmethod
    def _associate(cls, expr):
        """
        """
        if (type(expr) is cls) and (expr.head in cls.ASSOCIATIVE):
            if len(expr.tail) == 0:
                return cls.NULL[expr.head]
            elif len(expr.tail) == 1:
                return expr.tail[0]
            else:
                tail = []
                for p in expr.tail:
                    if (type(p) is cls) and (p.head == expr.head):
                        tail.extend(p.tail)
                    else:
                        tail.append(p)
                else:
                    return cls(expr.head, *tail)
        else:
            return expr

    @classmethod
    def simplify(cls: type, expr):
        return cls.associate(cls.calculate(expr))

    @classmethod
    def full_simplify(cls: type, expr):
        expr = cls.simplify(expr)
        return cls.back_apply(expr, cls._full_simplify)

    @classmethod
    def _full_simplify(cls: type, expr):
        if (type(expr) is cls) and (expr.head in cls.SIMPLIFY):
            return cls.SIMPLIFY[expr.head](expr.tail)
        else:
            return expr
            
    @classmethod
    def transverse(cls, expr, func, *args, **kwargs) -> None:
        """ Transverses expression tree calling `func` on leaves

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

            >>> def func(expr, *args, **kwargs) -> bool:
            ...     ...
            ...     return bool(...)
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
    def tell(cls, expr, choice: callable, func: callable, *args, **kwargs) -> bool:
        """ Returns either `True` or `False` if `choice` subtrees
            satisfies `func`.
        """
        if type(expr) is cls:
            head = (func(expr, *args, **kwargs),)
            tail = (cls.tell(p, choice, func, *args, **kwargs) for p in expr.tail)
            return choice(it.chain(head, tail))
        else:
            return func(expr, *args, **kwargs)

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
        """ Backward-applies function `func` to `expr`.

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
        self._hash_ = None

    def __hash__(self):
        if self._hash_ is None:
            self._hash_ = hash(str(self)) 
        return self._hash_

    def __str__(self):
        return self.regex.sub(r'\1', decimal.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

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

    ## Arithmetic
    def _ADD_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__add__(self, other))
        elif self == Number('0'):
            return other
        else:
            return NotImplemented

    def _RADD_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__radd__(self, other))
        elif self == Number('0'):
            return other
        else:
            return NotImplemented

    def _SUB_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__sub__(self, other))
        elif self == Number('0'):
            return (-other)
        else:
            return NotImplemented

    def _RSUB_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__rsub__(self, other))
        elif self == Number('0'):
            return other
        else:
            return NotImplemented

    def _MUL_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__mul__(self, other))
        elif self == Number('0'):
            return Number('0')
        elif self == Number('1'):
            return other
        else:
            return NotImplemented

    def _RMUL_(self, other):
        if self.numeric(other):
            return Number(decimal.Decimal.__rmul__(self, other))
        elif self == Number('0'):
            return Number('0')
        elif self == Number('1'):
            return other
        else:
            return NotImplemented

    def _DIV_(self, other):
        if self.numeric(other):
            if other != Number('0'):
                return Number(decimal.Decimal.__truediv__(self, other))
            else:
                raise SatValueError("Division by zero.", target=other)
        elif self == Number('0'):
            return Number('0')
        else:
            return NotImplemented

    def _RDIV_(self, other):
        if self == Number('0'):
            raise SatValueError("Division by zero.", target=self)
        elif self == Number('1'):
            return other
        elif self.numeric(other):
            return Number(decimal.Decimal.__truediv__(other, self))
        else:
            return NotImplemented

    def _MOD_(self, other):
        if self.numeric(other):
            if other != Number('0'):
                return Number(decimal.Decimal.__mod__(self, other))
            else:
                raise SatValueError("Division by zero.", target=other)
        elif self == Number('0'):
            return Number('0')
        else:
            return NotImplemented

    def _RMOD_(self, other):
        if self == Number('0'):
            raise SatValueError("Division by zero.", target=self)
        elif self.numeric(other):
            return Number(decimal.Decimal.__truediv__(other, self))
        else:
            return NotImplemented

    def _AND_(self, other):
        if self.numeric(other):
            return Number(self._MUL_(other))
        elif self == Number.T:
            return other
        elif self == Number.F:
            return Number.F
        else:
            return NotImplemented

    def _RAND_(self, other):
        if self.numeric(other):
            return Number(other._MUL_(self))
        elif self == Number.T:
            return other
        elif self == Number.F:
            return Number.F
        else:
            return NotImplemented

    def _OR_(self, other):
        if self.numeric(other):
            return Number((self._ADD_(other))._SUB_(self._MUL_(other)))
        elif self == Number.T:
            return Number.T
        elif self == Number.F:
            return other
        else:
            return NotImplemented

    def _ROR_(self, other):
        if self.numeric(other):
            return Number((self._ADD_(other))._SUB_(self._MUL_(other)))
        elif self == Number.T:
            return Number.T
        elif self == Number.F:
            return other
        else:
            return NotImplemented

    def _XOR_(self, other):
        if self.numeric(other):
            return Number((self._ADD_(other))._SUB_(Number('2')._MUL_(self)._MUL_(other)))
        else:
            return NotImplemented

    def _RXOR_(self, other):
        if self.numeric(other):
            return Number((self._ADD_(other))._SUB_(Number('2')._MUL_(self)._MUL_(other)))
        else:
            return NotImplemented

    def _IMP_(self, other):
        if self.numeric(other):
            return Number((self._NOT_())._OR_(other))
        elif self == Number.F:
            return Number.T
        elif self == Number.T:
            return other
        else:
            return NotImplemented

    def _RIMP_(self, other):
        if self.numeric(other):
            return Number(self._OR_(other._NOT_()))
        elif self == Number.T:
            return Number.T
        elif self == Number.F:
            return other._NOT_()
        else:
            return NotImplemented
        
    def _IFF_(self, other):
        if self.numeric(other):
            return Number((self._NOT_())._AND_(other._NOT_())._OR_(self._AND_(other)))
        elif self == Number.T:
            return other
        elif self == Number.F:
            return other._NOT_()
        else:
            return NotImplemented

    def _NOT_(self):
        return Number(Number('1')._SUB_(self))

    def _NEG_(self):
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
    """ :: VAR ::
        =========
    """

    def __init__(self, name : str):
        SatType.__init__(self)

    def __hash__(self):
        return str.__hash__(self)

    def __repr__(self):
        return f"Var('{self}')"

    def _IDX_(self, idx: tuple):
        subvarname = str(self)
        while idx:
            i, *idx = idx
            if type(i) is Number:
                if i > 0 and i.is_int:
                    subvarname = f"{subvarname}_{i}"
                else:
                    raise SatValueError(f"Index must be a positive integer, not `{i}`.", target=i)
            else:
                return Expr(T_IDX, Var(subvarname), i, *idx)
        else:
            return Var(subvarname)

class Array(SatType):
    """ :: Array ::
        ===========
    """
    def __init__(self, var: Var, shape: tuple):
        SatType.__init__(self)
        
        self.array = {}

        self.var = var
        self.shape = shape
        self.dim = len(shape)

    def _IDX_(self, idx: tuple):
        if len(idx) > self.dim:
            raise SatIndexError(f"Too much indices for {self.dim}-dimensional array.", target=idx[-1])
        elif len(idx) == 1:
            return self[idx[0]]
        else:
            i, *idx = idx
            return self[i]._IDX_(idx)

    def __getitem__(self, idx: Number):
        if type(idx) is Number and idx.is_int:
            i = int(idx)
            if i in self.array:
                return self.array[i]
            else:
                n = int(self.shape[0])
                if 1 <= i <= n:
                    if len(self.shape) > 1:
                        self.array[i] = Array(self.var._IDX_((idx,)), self.shape[1:])
                        return self.array[i]
                    else:
                        return self.var._IDX_((idx,))
                else:
                    raise SatIndexError(f"Index {idx} is out of bounds [1, {n}].", target=idx)
        elif type(idx) is Var:
            return Expr(T_IDX, self, idx)
        else:
            raise SatIndexError(f"Invalid index {idx}.", target=idx)

    def __setitem__(self, idx: Number, value: SatType):
        if type(idx) is Number and idx.is_int:
            if self.dim > 1:
                raise SatIndexError(f"Attempt to assign to {self.dim}-dimensional array.", target=idx)
            else:
                i = int(idx)
                n = int(self.shape[0])
                if 1 <= i <= n:
                    self.array[i] = value
                else:
                    raise SatIndexError(f"Index {idx} is out of bounds [1, {n}].", target=idx)                 
        else:
            raise SatIndexError(f"Invalid index {idx}.", target=idx)

    def __str__(self):
        return f"{self.var}" #+ "".join([f"[{n}]" for n in self.shape])

    def __repr__(self):
        return f"Array({self.var!r}, {self.shape!r})"

    def __hash__(self):
        return hash(sum(hash((k, hash(v))) for k, v in self.array.items()))
        
    @classmethod
    def from_buffer(cls, name, shape, buffer: dict):
        array = cls(name, shape)
        for idx in buffer:
            subarray = array
            for i in idx[:-1]:
                subarray = subarray[Number(i)]
            subarray[Number(idx[-1])] = buffer[idx]
        return array

    @classmethod
    def from_dict(cls, name: Var, shape: tuple, buffer: dict):
        """
        """
        return cls.from_buffer(name, shape, buffer)

    @classmethod
    def from_list(cls, name: Var, shape: tuple, buffer: dict):
        """
        """
        return cls.from_buffer(name, shape, { idx : val for (idx, val) in buffer })

@trackable
class String(str):
    """ :: STRING ::
        ============
    """
    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        str.__init__(self)

@trackable
class PythonObject(object):
    """ :: PYTHON_OBJECT ::
        ===================
    """

    def __init__(self, obj: object):
        self.obj = obj

class Constraint(object):

    def __init__(self, name: Var, cons_type: String, level: Number=None):
        self._name = name
        self._type = cons_type
        self._level = (level if level is not None else Number('0'))

        self._expr = None
        self._clauses = None
        
    def set_expr(self, expr: Expr):
        self._expr = expr

        if type(self._expr) is Expr:
            if (self._expr.head == T_OR):
                clauses = [([*p.tail] if (type(p) is Expr and p.head == T_AND) else [p]) for p in self._expr.tail]
            elif (self._expr.head == T_AND):
                clauses = [[*self._expr.tail]]
            else:
                clauses = [[self._expr]]
        else:
            clauses = [[self._expr]]

        self._clauses = clauses

    @property
    def var(self) -> Var:
        return self._name

    @property
    def name(self) -> str:
        return str(self._name)

    @property
    def type(self) -> str:
        return str(self._type)

    @property
    def level(self):
        return int(self._level)

    @property
    def clauses(self):
        return self._clauses
    
    @property
    def expr(self) -> Expr:
        return self._expr