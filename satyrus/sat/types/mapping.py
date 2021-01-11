## Satandard Library
import abc
from functools import reduce

## Local1
from .main import Var, Number
from .expr import Expr
from .symbols.tokens import T_AND, T_OR, T_XOR, T_NOT, T_ADD, T_MUL, T_SUB

class SatMapping(metaclass=abc.ABCMeta):
    """
    """
    
    @abc.abstractclassmethod
    def map_and(cls, tail: list) -> Expr:
        ...

    @abc.abstractclassmethod
    def map_or(cls, tail: list) -> Expr:
        ...

    @abc.abstractclassmethod
    def map_xor(cls, tail: list) -> Expr:
        ...

    @abc.abstractclassmethod
    def map_not(cls, tail: list) -> Expr:
        ...

    @classmethod
    def _map_expr(cls, expr: Expr) -> Expr:
        if type(expr) is Expr:
            if expr.head == T_AND:
                return cls.map_and(expr.tail)
            elif expr.head == T_OR:
                return cls.map_or(expr.tail)
            elif expr.head == T_XOR:
                return cls.map_xor(expr.tail)
            elif expr.head == T_NOT:
                return cls.map_not(expr.tail)
            else:
                return expr
        else:
            return expr

    @classmethod
    def map_expr(cls, expr: Expr) -> Expr:
        return Expr.back_apply(expr, cls._map_expr)

class Strict(SatMapping):

    @classmethod
    def map_and(cls, tail: list) -> Expr:
        """ SatMapping.map_and:
            x & y & ... & z => x * y * ... * z
        """
        return Expr(T_MUL, *tail)

    @classmethod
    def map_or(cls, tail: list) -> Expr:
        raise NotImplementedError

    @classmethod
    def map_xor(cls, tail: list) -> Expr:
        raise NotImplementedError

    @classmethod
    def map_not(cls, tail: list) -> Expr:
        """ SatMapping.map_not:
            ~x => 1 - x
        """
        return Expr(T_SUB, Number('1'), *tail)

class Relaxed(SatMapping):

    @classmethod
    def map_and(cls, tail: list) -> Expr:
        """ SatMapping.map_and:
            x & y & ... & z => x * y * ... * z
        """
        return Expr(T_MUL, *tail)

    @classmethod
    def map_or(cls, tail: list) -> Expr:
        """ SatMapping.map_or:
            x | y | ... | z => x + y + ... + z
        """
        return Expr(T_ADD, *tail)

    @classmethod
    def map_xor(cls, tail: list) -> Expr:
        raise NotImplementedError

    @classmethod
    def map_not(cls, tail: list) -> Expr:
        """ SatMapping.map_not:
            ~x => 1 - x
        """
        return Expr(T_SUB, Number('1'), *tail)
    
    