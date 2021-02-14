from satyrus.sat.types import Expr, Number, Var, Array
from satyrus.sat.types.main import Expr as _Expr
from satyrus.sat.types.symbols.tokens import T_MUL, T_ADD, T_NEG, T_IDX
from satyrus.sat.parser import ExprParser
from satyrus.satlib import join

parser = ExprParser()

x = Array(Var('x'), (Number('3'), Number('3')))

e = Expr(T_IDX, x, Var('i'), Var('j'))
a = Expr(T_IDX, Var('x'), Var('i'), Var('j'))