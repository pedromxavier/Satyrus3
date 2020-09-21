from satyrus import SatAPI, Expr, Var, Number
from satyrus.satlib import stdout, stdwar, stream

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv) > 1) else r"examples/graph_colour.sat"

sat = SatAPI(SOURCE_PATH)

## Text Output
print(sat['text'].solve())

## CSV Output
with open('sat.csv', 'w') as file:
    file.write(sat['csv'].solve())