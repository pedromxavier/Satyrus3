""" :: DEF_CONSTRAINT ::
	====================

	STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it

## Local
from satlib import arange, Stack
from ..compiler import SatCompiler
from ...types.error import SatValueError, SatTypeError, SatReferenceError, SatWarning
from ...types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL
from ...types import Var, Number, Expr, Constraint

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {'int', 'opt'}

def def_constraint(compiler: SatCompiler, cons_type: Var, name: Var, loops: list, expr: Expr, level: Number):
	"""
	"""

	if cons_type not in CONST_TYPES:
		compiler << SatValueError(f'Unknown constraint type {cons_type}', target=cons_type)
	elif (cons_type == 'int') and (level is not None):
		compiler << SatValueError(f'Integrity constraints have no penalty level.', target=level)
	elif not level.is_int:
		compiler << SatValueError(f'Penalty level must be an integer.', target=level)
	else:
		## Create constraint
		constraint = Constraint(cons_type, int(level))

		## Compile constraint loops
		loop_depth = len(loops)

		for loop in loops:
			def_constraint_loop(compiler, loop, constraint)

		compiler.checkpoint()

		## Compile expression
		def_expr(compiler, expr, constraint)

		compiler.pop(loop_depth)

	compiler.checkpoint()

	## Check for constraint re-definition
	if name in compiler:
		compiler < SatWarning(f'Constraint definition overrides previous assignment.', target=name)

	compiler.memset(name, constraint)

	compiler.checkpoint()

def def_constraint_loop(compiler: SatCompiler, loop: tuple, constraint: Constraint) -> None:
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

	## Evaluate loop conditionals
	def_loop_conds(compiler, loop_conds)

	compiler.checkpoint()

def def_loop_conds(compiler: SatCompiler, loop_conds: list):
	""" DEF_LOOP_COND
		=============
	"""
	for i, cond in enumerate(loop_conds):
		try:
			loop_conds[i] = compiler.eval_expr(cond)
		except SatReferenceError as error:
			compiler << error
		except Exception as error:
			raise error
	else:
		compiler.checkpoint()

def def_expr(compiler, expr: Expr, constraint: Constraint):
	""" DEF_EXPR
		========

		Checks for expression consistency.
		1. Variable definition
		2. Proper indexing
	"""
	expr = compiler.eval_expr(expr)
	


	

		






		