from satyrus.sat.types import Expr, Number, Var
from satyrus.sat.types.expr import Expr as EX
from satyrus.sat.types.symbols.tokens import T_MUL, T_ADD, T_NEG
from satyrus.sat.parser import ExprParser
from satyrus.satlib import join

parser = ExprParser()
a = parser.parse("2 + 3 * x")
b = parser.parse("3 * x + 2")