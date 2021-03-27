""" :: Sat Types ::
    ===============
"""
## Standard Library
import decimal
import re
import itertools as it
from functools import wraps, cmp_to_key
from sys import intern

## Local
from ..satlib import join, keep_type, trackable
from .error import SatValueError, SatIndexError, SatTypeError
from .symbols.tokens import T_DICT, T_IDX, T_AND, T_OR, T_MUL, T_ADD, T_NEG

class MetaSatType(type):

    ATTRS = {f"_{name.upper()}_" : T_DICT[name] for name in T_DICT}
    REGEX = re.compile(r"_r[A-Z]+_")

    ExprType = lambda *x: x

    @staticmethod
    def null_func(*args):
        return NotImplemented

    def __new__(cls, name, bases, attrs):
        for attr_name, token in cls.ATTRS.items():
            if attr_name in attrs:
                callback = attrs[attr_name]
            elif any(hasattr(base, attr_name) for base in bases):
                continue
            else:
                callback = cls.null_func

            attrs[attr_name] = cls.magic(token, callback, swap=(cls.REGEX.match(attr_name) is not None))

        sattype = type(name, bases, attrs)

        if 'Expr' in name: cls.ExprType = sattype

        return sattype
        

    @classmethod
    def magic(cls, token, callback, swap=False):
        """
        """
        @wraps(callback)
        def new_callback(*args):
            answer = callback(*args)
            if answer is NotImplemented:
                if swap:
                    return cls.ExprType(token, *reversed(args))
                else:
                    return cls.ExprType(token, *args)
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
        raise SatTypeError(f"Can not index object of type `{type(self)}`.", target=self)

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

    def __neg__(self):
        return self._NEG_()

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

class Expr(SatType, tuple, metaclass=MetaSatType):
    """ :: Expr ::
        ==========

        This is one of the core elements of the system. This is used to represent ASTs.

        Only basic functionality is implemented here. Context is implemented in `expr.py`
    """

    SORT = MetaSatType.null_func
    SORTABLE = set()
    FLAT = set()
    HASH = {}
    RULES = {}
    GROUPS = {}
    FORMAT_SPECIAL = {}
    FORMAT_PATTERNS = {}
    FORMAT_FUNCTIONS = {}

    VarType = str

    def __new__(cls, head: str, *tail: tuple, sort: bool=True, flat:bool=True):
        """ Creates pair (head, tail) to represent an expression. Here is applied, according to `sort` and `flat` parameters, child sorting and 
        """
        if sort and flat:
            return tuple.__new__(cls, (head, *cls.sort(head, cls.flat(head, tail))))
        elif sort:
            return tuple.__new__(cls, (head, *cls.sort(head, tail)))
        elif flat:
            return tuple.__new__(cls, (head, *cls.flat(head, tail)))
        else:
            return tuple.__new__(cls, (head, *tail))

    def __init__(self, head: str, *tail: tuple, sort: bool=True, flat:bool=True):
        SatType.__init__(self)
        self._flat_ = flat
        self._sort_ = sort
        self._hash_ = None
    
    @classmethod
    def sort(cls, head: str, tail: list) -> list:
        """ Returns sorted tail according to key function defined by `cls.SORT: object -> object`.
        """
        if head in cls.SORTABLE:
            return sorted([(p if (type(p) is not cls) else (p if p._sort_ else cls(p.head, *p.tail))) for p in tail], key=cls.SORT)
        else:
            return tail

    @classmethod
    def flat(cls, head: str, tail: list) -> list:
        if head in cls.FLAT:
            flattail = []
            for p in tail:
                if type(p) is cls and (p.head == head):
                    if p._flat_:
                        tail = p.tail
                    else:
                        tail = cls.flat(p.head, p.tail)
                    flattail.extend(tail)
                else:
                    flattail.append(p)
            return flattail
        else:
            return tail

    @classmethod
    def sorting(cls, sort: callable):
        cls.SORT = sort

    @classmethod
    def parenthesise(cls, root: object, child: object) -> bool:
        if type(root) is cls and type(child) is cls:
            return cls._parenthesise(root.head, child.head)
        else:
            return False

    @classmethod
    def _parenthesise(cls, from_head: str, to_head: str):
        if from_head not in cls.GROUPS:
            return False
        elif to_head not in cls.GROUPS:
            return False
        elif cls.GROUPS[from_head] > cls.GROUPS[to_head]:
            return True
        else:
            return False

    def __str__(self):
        tail = [(f"({p})" if self.parenthesise(self, p) else str(p)) for p in self.tail]
        if self.head in self.FORMAT_PATTERNS:
            return self.FORMAT_PATTERNS[self.head].format(self.head, *tail)
        elif self.head in self.FORMAT_FUNCTIONS:
            return self.FORMAT_FUNCTIONS[self.head](self.head, *tail)
        elif self.head in self.FORMAT_SPECIAL:
            return self.FORMAT_SPECIAL[self.head](type(self), self.head, self.tail)
        else:
            return join(" ", [self.head, *tail])
        
    def __repr__(self):
        return f"Expr({join(', ', self, repr)})"

    def __hash__(self):
        if self._hash_ is None:
            return self.HASH[self.head](*self.tail)
        return self._hash_

    @classmethod
    def rule(cls, token: str):
        def decor(callback: callable):
            if token in cls.RULES:
                cls.RULES[token].append(callback)
            else:
                cls.RULES[token] = [callback]
        return decor

    @classmethod
    def apply_rule(cls, expr):
        if type(expr) is cls:
            if expr.head in cls.RULES:
                e = expr
                for rule in cls.RULES[expr.head]:
                    if (type(e) is cls) and (e.head == expr.head):
                        e = rule(cls, *e.tail)
                    else:
                        return cls.apply_rule(e)
                else:
                    return e
            else:
                return expr
        else:
            return expr

    @classmethod
    def calculate(cls, expr) -> SatType:
        """ Applies rules as described in `cls.RULES` for each expression, in a backward fashion i.e. from leaves to root, then, applies forward. As result, may yield Var, Number or Expr.
        """
        return cls.apply(cls.back_apply(expr, cls.apply_rule), cls.apply_rule)

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
        return self.__class__(self.head, *(p.copy for p in self.tail))

    @classmethod
    def simplify(cls: type, expr):
        raise NotImplementedError
   
    @classmethod
    def transverse(cls, expr, func, *args, **kwargs) -> None:
        """Transverses expression tree calling `func` on leaves

        Example
        -------
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
        """Seeks for tree leaves who satisfy `func`

        Example
        -------
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
    def sub(cls, expr, x, y):
        """
        """
        return cls.apply(expr, lambda e: ((y if (e == x) else e) if type(e) is cls.VarType else e))

    def _IDX_(self, i: tuple):
        return type(self)(T_IDX, self, *i)

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

    def __init__(self, value: {int, float, str}):
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

    ## Aliases
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
            i, *idx = idx ## pick first
            if type(i) is Number:
                if i > 0 and i.is_int:
                    subvarname = f"{subvarname}_{i}"
                else:
                    raise SatValueError(f"Index must be a positive integer, not `{i}`.", target=i)
            else:
                return MetaSatType.ExprType(T_IDX, Var(subvarname), i, *idx)
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

    def __getitem__(self, i: Number):
        if type(i) is Number and i.is_int:
            j = int(i)
            if j in self.array:
                return self.array[j]
            else:
                n = int(self.shape[0])
                if 1 <= j <= n:
                    if len(self.shape) > 1:
                        self.array[j] = Array(self.var._IDX_((i,)), self.shape[1:])
                        return self.array[j]
                    else:
                        return self.var._IDX_((i,))
                else:
                    raise SatIndexError(f"Index {i} is out of bounds [1, {n}].", target=i)
        elif type(i) is Var:
            return MetaSatType.ExprType(T_IDX, self, i)
        else:
            raise SatIndexError(f"Invalid index `{i}` of type `{type(i)}`.", target=i)

    def __setitem__(self, i: Number, value: SatType):
        if type(i) is Number and i.is_int:
            if self.dim > 1:
                raise SatIndexError(f"Attempt to assign to {self.dim}-dimensional array.", target=i)
            else:
                j = int(i)
                n = int(self.shape[0])
                if 1 <= j <= n:
                    self.array[j] = value
                else:
                    raise SatIndexError(f"Index {i} is out of bounds [1, {n}].", target=i)                 
        else:
            raise SatIndexError(f"Invalid index {i}.", target=i)

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
        
    def set_expr(self, expr: MetaSatType.ExprType):
        self._expr = expr

        if isinstance(self._expr, Expr):
            if (self._expr.head == T_OR):
                clauses = [([*p.tail] if (isinstance(p, Expr) and p.head == T_AND) else [p]) for p in self._expr.tail]
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