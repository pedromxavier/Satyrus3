from satyrus import SatAPI, Expr, Var
from satyrus.satlib import stdout, stdwar

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv)> 1) else r"examples/graph_colour.sat"

sat = SatAPI(SOURCE_PATH)

expr = Expr('*', Expr('+', Var('a'), Var('b')), Expr('+', Var('x'), Var('y')))

stdwar << sat['csv'].solve()