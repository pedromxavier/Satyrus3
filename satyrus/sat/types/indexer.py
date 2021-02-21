from abc import ABCMeta, abstractmethod
from .main import Var, Number
from .expr import SatExpr as Expr
from .symbols.tokens import T_FORALL, T_EXISTS, T_EXISTS_ONE, T_AND, T_OR
from ...satlib import stderr
from ..compiler import SatCompiler

class SatIndexer(metaclass=ABCMeta):

    def __init__(self, compiler: SatCompiler, type_: str, var: Var, indices: list, cond: Expr=None):
        self._type = type_
        self._vars = [var]
        self._cond = cond
        self._next = None
        self._last = self
        self._comp = compiler
        self._indices = [{var: i} for i in indices]

    @abstractmethod
    def forall(self, expr: Expr, context: dict=None):
        ...
    
    @abstractmethod
    def exists(self, expr: Expr, context: dict=None):
        ...

    @abstractmethod
    def exists_one(self, expr: Expr, context: dict=None):
        ...

    @property
    def in_cnf(self) -> bool:
        if self._next is None:
            return (self._type == T_FORALL)
        else:
            return (self._type == T_FORALL) and self._next.in_cnf

    @property
    def in_dnf(self) -> bool:
        if self._next is None:
            return (self._type == T_EXISTS)
        else:
            return (self._type == T_EXISTS) and self._next.in_dnf

    def __str__(self):
        if self._next is None:
            return " ".join([f"{self._type}{var}" for var in self._vars])
        else:
            return f'{" ".join([f"{self._type}{var}" for var in self._vars])} {self._next}'

    def __call__(self, expr: Expr, ensure_cnf:bool=False, ensure_dnf: bool=False) -> Expr:
        """ It is assumed that this is applied first to the root of the indexing stack.
        """
        if ensure_cnf and ensure_dnf:
            raise ValueError("Cannot ensure both conjunctive and disjunctive normal forms.")
        elif ensure_cnf:
            return self.ensure_cnf(expr)
        elif ensure_dnf:
            return self.ensure_dnf(expr)
        else:
            return self.index(expr)

    def ensure_cnf(self, expr: Expr):
        if self.in_cnf:
            return self.index(expr)
        elif self._next is not None:
            expr = self.index(self._next.ensure_cnf(expr))
        else:
            expr = self.index(expr)

        if (self._type == T_EXISTS):
            #pylint: disable=no-member
            return Expr.cnf(expr)
        elif (self._type == T_FORALL):
            return expr
        else:
            raise NotImplementedError(f'C.N.F. Indexing not implemented for quantifier `{self._type}`.')

    def ensure_dnf(self, expr: Expr):
        if self.in_dnf:
            return self.index(expr)
        elif self._next is not None:
            expr = self.index(self._next.ensure_dnf(expr))
        else:
            expr = self.index(expr)

        if (self._type == T_FORALL):
            #pylint: disable=no-member
            return Expr.dnf(expr)
        elif (self._type == T_EXISTS):
            return expr
        else:
            raise NotImplementedError(f'D.N.F. Indexing not implemented for quantifier `{self._type}`.')
        
    def __lshift__(self, other):
        """ SatIndexer(...) << SatIndexer(...) << ... << SatIndexer() << Expr
        """
        if isinstance(other, SatIndexer):
            if self._last._type == other._type:
                ## Consume next Indexer
                self._last._vars.extend(other._vars)
                self._last._indices = [K for I in self._last._indices for J in other._indices if other.cond(K := {**I, **J})]
            else:
                self._last._next = other
                self._last._last = other
                self._last = other
            return self
        else:
            raise TypeError(f'Invalid type for indexer: {type(other)}.')

    def __invert__(self):
        if self._type == T_FORALL:
            self._type = T_EXISTS
        elif self._type == T_EXISTS:
            self._type = T_FORALL
        else:
            raise NotImplementedError(f'Unable to invert loop type `{self._type}`.')

        if self._next is not None: self._next.__invert__()

    def _index(self, tail: list):
        if self._type == T_FORALL:
            return self.forall(tail)
        elif self._type == T_EXISTS:
            return self.exists(tail)
        elif self._type == T_EXISTS_ONE:
            return self.exists_one(tail)
        else:
            return ValueError(f"Invalid loop type `{self._type}`")
        
    def index(self, expr: Expr, context: dict=None) -> dict:
        """
        """
        if context is None: context = {}
        
        if self._next is None:
            return self._index([self._eval(expr, context) for I in self._indices if self.cond(context := {**context, **I})])
        else:
            return self._index([self._next.index(expr, context) for I in self._indices if self.cond(context := {**context, **I})])

    def cond(self, context: dict) -> bool:
        if self._cond is not None:
            return bool(self._eval(self._cond, context))
        else:
            return True

    def _eval(self, expr: Expr, context: dict) -> Number:
        """ SatIndexer._eval(expr: Expr, context: dict) -> Number
            Here, `miss=False` supposes that all variables (`SatType::Var`) are
            verified before, during previous compilation i.e. it is not in the
            goals of this module to assert that condition.
        """
        return self._comp.evaluate(expr, miss=False, calc=True, null=False, context=context)

class Default(SatIndexer):

    def __init__(self, compiler: SatCompiler, type_: str, var: Var, indices: list, cond: Expr = None):
        SatIndexer.__init__(self, compiler, type_, var, indices, cond)

    def forall(self, tail: list):
        return Expr(T_AND, *tail)

    def exists(self, tail: list):
        return Expr(T_OR, *tail)

    def exists_one(self, tail: list):
        raise NotImplementedError