## Satandard Library
import abc
from functools import reduce

## Local1
from .main import Var, Number
from .expr import SatExpr as Expr
from .symbols.tokens import T_AND, T_OR, T_XOR, T_NOT, T_ADD, T_MUL, T_NEG

class SatMapping(metaclass=abc.ABCMeta):
    """
    """

    def __init__(self):
        ...

    def __call__(self, expr: Expr) -> Expr:
        return Expr.back_apply(expr, self._map_expr)
    
    @abc.abstractmethod
    def map_and(self, tail: list) -> Expr:
        ...

    @abc.abstractmethod
    def map_or(self, tail: list) -> Expr:
        ...

    @abc.abstractmethod
    def map_xor(self, tail: list) -> Expr:
        ...

    @abc.abstractmethod
    def map_not(self, tail: list) -> Expr:
        ...
        
    def _map_expr(self, expr: Expr) -> Expr:
        if type(expr) is Expr:
            if expr.head == T_AND:
                return self.map_and(expr.tail)
            elif expr.head == T_OR:
                return self.map_or(expr.tail)
            elif expr.head == T_XOR:
                return self.map_xor(expr.tail)
            elif expr.head == T_NOT:
                return self.map_not(expr.tail)
            else:
                return expr
        else:
            return expr

class Strict(SatMapping):

    def map_and(self, tail: list) -> Expr:
        """ SatMapping.map_and:
            x & y & ... & z => x * y * ... * z
        """
        return Expr(T_MUL, *tail)

    def map_or(self, tail: list) -> Expr:
        raise NotImplementedError

    def map_xor(self, tail: list) -> Expr:
        raise NotImplementedError

    def map_not(self, tail: list) -> Expr:
        """ SatMapping.map_not:
            ~x => 1 - x
        """
        return Expr(T_ADD, Number('1'), Expr(T_NEG, *tail))

class Relaxed(SatMapping):

    def map_and(self, tail: list) -> Expr:
        """ SatMapping.map_and:
            x & y & ... & z => x * y * ... * z
        """
        return Expr(T_MUL, *tail)

    def map_or(self, tail: list) -> Expr:
        """ SatMapping.map_or:
            x | y | ... | z => x + y + ... + z
        """
        return Expr(T_ADD, *tail)

    def map_xor(self, tail: list) -> Expr:
        raise NotImplementedError

    def map_not(self, tail: list) -> Expr:
        """ SatMapping.map_not:
            ~x => 1 - x
        """
        return Expr(T_ADD, Number('1'), Expr(T_NEG, *tail))
    
    