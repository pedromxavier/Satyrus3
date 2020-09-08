from satyrus import Satyrus, Expr, Var, Number, Array
import sys
SOURCE_PATH = sys.argv[1] if len(sys.argv)> 1 else r"examples/source.sat"
sat = Satyrus(SOURCE_PATH)