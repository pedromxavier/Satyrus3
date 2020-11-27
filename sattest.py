from satyrus import Satyrus, Expr, Var, Number, String
from satyrus.sat.compiler import SatCompiler
from satyrus.sat.compiler.instructions import instructions
from satyrus.satlib import stdout, stdwar, stream

import sys
SOURCE_PATH = sys.argv[1] if (len(sys.argv) > 1) else r"examples/graph_colour.sat"

sat = Satyrus(SOURCE_PATH)
print(sat.results)

##comp = SatCompiler(instructions)
##
##cond = Expr('!=', Var('l'), Var('k'))
##
##scope_a = {Var('i'): Number(1), Var('k'): Number(1), Var('l'): Number(1)}
##scope_b = {Var('i'): Number(1), Var('k'): Number(2), Var('l'): Number(4)}
####
##comp.push(scope_a)
##ans_a = comp.evaluate(cond)
##comp.pop()
##
##comp.push(scope_b)
##ans_b = comp.evaluate(cond)
##comp.pop()
