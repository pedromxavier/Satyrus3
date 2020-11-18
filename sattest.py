from satyrus import Satyrus, Expr, Var, Number
from satyrus.satlib import stdout, stdwar, stream

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv) > 1) else r"examples/graph_colour.sat"

sat = Satyrus(SOURCE_PATH)
print(sat.results)