""" :: DEF_CONSTRAINT ::
	====================

	STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it

## Local
from ....satlib import arange, Stack, stdout
from ..compiler import SatCompiler
from ...types.error import SatValueError, SatTypeError, SatReferenceError, SatWarning
from ...types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL
from ...types.symbols import CONS_INT, CONS_OPT
from ...types import Var, String, Number, Constraint
from ...types.expr import Expr

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}

def def_constraint(compiler: SatCompiler, cons_type: String, name: Var, loops: list, expr: Expr, level: Number):
	""" DEF_CONSTRAINT
		==============
	"""
	## Check constraint type and level
	def_constraint_type(compiler, cons_type, level)

	## Evaluate constraint loops
	def_constraint_loops(compiler, loops)

def def_constraint_type(compiler: SatCompiler, cons_type: String, level: Number):
	"""
	"""
	if str(cons_type) not in CONST_TYPES:
		compiler << SatTypeError(f"Invalid constraint type {cons_type}. Options are: `int`, `opt`.", target=cons_type)

	if str(cons_type) == CONS_OPT and level != 0:
		compiler << SatTypeError("Invalid penalty level for optimality constraint.", target=level)

	if level < 0 or not level.is_int:
		compiler << SatValueError(f"Invalid penalty level {level}. Must be positive integer.", target=level)

	compiler.checkpoint()

def def_constraint_loops(compiler: SatCompiler, loops: list):
	"""
	"""
	