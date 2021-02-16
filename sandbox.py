from satyrus.sat.types import Expr, Number, Var, Array
from satyrus.sat.types.main import Expr as _Expr
from satyrus.sat.types.symbols.tokens import T_MUL, T_ADD, T_NEG, T_IDX
from satyrus.sat.parser import ExprParser
from satyrus.satlib import join

parser = ExprParser()

e = parser.parse("x * (y + z * (w + i - j))")