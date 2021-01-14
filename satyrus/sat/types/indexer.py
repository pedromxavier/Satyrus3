from abc import ABCMeta, abstractmethod
from .main import Var, Number
from .expr import Expr
from .symbols.tokens import T_FORALL, T_EXISTS, T_EXISTS_ONE, T_AND, T_OR
from ..compiler import SatCompiler

class SatIndexer(metaclass=ABCMeta):

    def __init__(self, compiler: SatCompiler, type_: str, var: Var, indices: list, cond: Expr=None):
        self._type = type_
        self._var = var
        self._indices = indices

        self._cond = cond
        
        self._root = self
        self._next = None
    
        self._comp = compiler

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
    def cnf(self) -> bool:
        if self._next is None:
            return (self._type == T_EXISTS)
        else:
            return (self._type == T_EXISTS) and self._next.cnf

    def __repr__(self):
        if self._next is None:
            return f"{self._type}{self._var}"
        else:
            return f"{self._type}{self._var} {self._next}"  

    def __lshift__(self, indexer) -> Expr:
        """ SatIndexer(...) << SatIndexer(...) << ... << SatIndexer() << Expr
        """
        if isinstance(indexer, SatIndexer):
            self._next = indexer
            self._next._root = self._root
            return self._next
        elif isinstance(indexer, Expr):
            return self._root.index(indexer)
        else:
            raise TypeError(f'Invalid type for indexer: {type(indexer)}.')

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
        
    def index(self, expr: Expr, context: dict=None):
        if context is None: context = {}

        if self._next is None:
            return self._index([self._eval(expr, context) for i in self._indices if self.cond(context := {**context, self._var: i})])
        else:
            return self._index([self._next.index(expr, context) for i in self._indices if self.cond(context := {**context, self._var: i})])

    def cond(self, context: dict) -> bool:
        if self._cond is not None:
            return bool(self._eval(self._cond, context))
        else:
            return True

    def _eval(self, expr: Expr, context: dict) -> Number:
        return self._comp.evaluate(expr, miss=True, calc=True, null=False, context=context)

class Default(SatIndexer):

    def __init__(self, compiler: SatCompiler, type_: str, var: Var, indices: list, cond: Expr = None):
        SatIndexer.__init__(self, compiler, type_, var, indices, cond)

    def forall(self, tail: list):
        return Expr(T_AND, *tail)

    def exists(self, tail: list):
        return Expr(T_OR, *tail)

    def exists_one(self, tail: list):
        raise NotImplementedError