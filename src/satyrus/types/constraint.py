"""
"""


# Local
from .expr import Expr
from .number import Number
from .string import String
from .var import Var

from ..satlib import Posiform
from ..symbols import T_AND, T_OR


class Constraint(object):
    def __init__(self, name: Var, cons_type: String, level: Number = None):
        self.name = name
        self.type = cons_type
        self.level = Number(level) if level is not None else Number("0")

        self.expr = None

    @staticmethod
    def clauses(expr: Expr) -> list:
        if expr.is_expr:
            if expr.head == T_OR:
                return [
                    (list(p.tail) if (p.is_expr and p.head == T_AND) else [p])
                    for p in expr.tail
                ]
            elif expr.head == T_AND:
                return [[*expr.tail]]
            else:
                return [[expr]]
        else:
            return [[expr]]
