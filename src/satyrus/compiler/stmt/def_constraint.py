""" :: DEF_CONSTRAINT ::
	====================

	STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it

## Local
from satlib import arange, Stack
from ..compiler import SatCompiler
from ...types.error import SatValueError, SatTypeError, SatReferenceError
from ...types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL
from ...types import Var, Number, Expr

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {'int', 'opt'}

def def_constraint(compiler: SatCompiler, const_type: str, name: Var, loops: list, expr: Expr, level: int):
	"""
	"""
	if const_type not in CONST_TYPES:
		compiler << SatValueError(f'Unknown constraint type {const_type}', target=const_type)
	elif const_type == 'int' and level is not None:
		compiler << SatValueError(f'Integrity constraints have no penalty level.', target=level)
	else:
		def_constraint_loops(compiler, loops)

	compiler.checkpoint()

def def_constraint_loops(compiler: SatCompiler, loops: list) -> None:
	""" 
	"""

	depth = len(loops)

	for loop in loops:
		def_constraint_loop(compiler, loop)

	compiler.pop(depth)
	
	compiler.checkpoint()

def def_constraint_loop(compiler: SatCompiler, loop: tuple) -> None:
	"""
	"""
	## Get loop attributes
	(loop_type, loop_var, loop_range, loop_conds) = loop

	## Check Loop Type
	if loop_type not in LOOP_TYPES:
		compiler << SatTypeError(f'Invalid loop type {loop_type}', target=loop_type)

	if loop_var in compiler:
		compiler << SatReferenceError(f"Duplicate definition for loop variable {loop_var}", target=loop_var)
	else:
		## Push compile memory scope
		compiler.push()

	## Evaluate Loop Parameters
	start, stop, step = tuple(compiler.eval(k) for k in loop_range)

	## Check Values
	if not start.is_int:
		compiler << SatTypeError(f'Loop start must be an integer.', target=start)

	if not stop.is_int:
		compiler << SatTypeError(f'Loop end must be an integer.', target=stop)

	if step is None:
		if start < stop:
			step = Number('1')
		else:
			step = Number('-1')

	elif not step.is_int:
		compiler << SatTypeError(f'Loop step must be an integer.', target=step)
		
	if (start < stop and step < 0) or (start > stop and step > 0):
		compiler << SatTypeError(f'Inconsistent Loop definition.', target=start)

	## Set loop variable to itself
	compiler.memset(loop_var, loop_var)

	for cond in loop_conds:
		def_loop_cond(compiler, cond)

	compiler.checkpoint()

def def_loop_cond(compiler: SatCompiler, cond: Expr):
	""" DEF_LOOP_COND
		=============
	"""
	try:
		compiler.eval_expr(cond)
	except SatReferenceError as error:
		compiler << error
	finally:
		compiler.checkpoint()

def def_expr(compiler, expr: Expr):
	""" DEF_EXPR
		========

		Checks for expression consistency.
		1. Variable definition
		2. Proper indexing
	"""

	

		






		