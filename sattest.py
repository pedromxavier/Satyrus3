from satyrus import SatAPI, Expr
from satyrus.satlib import stdout

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv)> 1) else r"examples/source.sat"

sat = SatAPI(SOURCE_PATH)

sat['text'].solve()