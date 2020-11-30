from satyrus import Satyrus, Expr, Var, Number, String, Array
from satyrus.sat.compiler import SatCompiler
from satyrus.sat.compiler.instructions import instructions
from satyrus.satlib import stdout, stdwar, stream

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv) > 1) else r"examples/graph_colour.sat"

sat = Satyrus(SOURCE_PATH)
##print(sat.results)

##e = Expr('[]', Expr('[]', Var('vc'), Var('i')), Var('k'))

##print(repr(Expr.calculate(e)))
