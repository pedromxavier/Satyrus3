from abc import ABCMeta, abstractmethod
from typing import Callable

from cstream import stderr, stdwar

from ...satlib import arange
from ...types import Var, Number
from ...types import Expr
from ...types.symbols.tokens import T_FORALL, T_EXISTS, T_UNIQUE, T_AND, T_OR
from ..compiler import SatCompiler

from .components import Loop


class SatIndexer(object):
    def __init__(self, compiler: SatCompiler, loops: list, expr: Expr):
        self.compiler = compiler
        self.loops = loops
        self.expr = expr

    def __str__(self):
        return " ".join([f"{loop.type}{loop.var}" for loop in self.loops] + [str(self.expr)])

    def index(self, *, ensure_dnf: bool = False, ensure_cnf: bool = False):
        """
        Parameters
        ----------
        key-word args:
            ensure_dnf : bool
            ensure_cnf : bool
        """

        if ensure_cnf and ensure_dnf:
            raise ValueError(
                "Can't ensure both Conjunctive and Disjunctive normal forms."
            )
        elif ensure_dnf:
            return self.ensure_dnf()
        elif ensure_dnf:
            return self.ensure_cnf()
        else:
            return self._index()

    def ensure_dnf(self):
        """Ensures that output comes in Disjunctive Normal Form (DNF)."""
        return Expr.dnf(self._index())

    def ensure_cnf(self):
        """Ensures that output comes in Conjunctive Normal Form (CNF)."""
        return Expr.cnf(self._index())

    def _index(self):
        self.n = len(self.loops)
        return self.__index(0, {})

    def __index(self, k: int, J: dict) -> Expr:
        """"""
        if k < self.n:
            loop: Loop = self.loops[k]

            if loop.type == T_FORALL:
                head = T_AND
            elif loop.type == T_EXISTS:
                head = T_OR
            else:
                raise ValueError(f"Invalid loop type '{loop.type}'.")

            tail = [self.__index(k + 1, I) for I in self.get_indices(loop, J)]

            return Expr(head, *tail)
        else:
            return self.compiler.evaluate(self.expr, context=J)

    def get_indices(self, loop: Loop, context: dict):
        """"""
        if loop.cond is not None:
            return [{**context, loop.var: i} for i in arange(*loop.bounds) if bool(self.compiler.evaluate(loop.cond, context={**context, loop.var: i}))]
        else:
            return [{**context, loop.var: i} for i in arange(*loop.bounds)]

    def negate(self):
        """"""
        for loop in self.loops:
            if loop.type == T_FORALL:
                loop.type = T_EXISTS
            elif loop.type == T_EXISTS:
                loop.type = T_FORALL
            else:
                raise ValueError(f"Invalid loop type '{loop.type}'.")
        else:
            self.expr = Expr.calculate(~self.expr)

    @property
    def in_dnf(self) -> bool:
        return all(loop.type == T_EXISTS for loop in self.loops)

    @property
    def in_cnf(self) -> bool:
        return all(loop.type == T_FORALL for loop in self.loops)