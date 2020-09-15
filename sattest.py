from satyrus import SatAPI, Expr
from satyrus.satlib import stdout, stdwar

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv)> 1) else r"examples/graph_colour.sat"

sat = SatAPI(SOURCE_PATH)

stdwar << sat['text'].solve()