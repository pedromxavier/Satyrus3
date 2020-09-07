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
from ...types import Var, Number, Constraint
from ...types.expr import Expr

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}

def def_constraint(compiler: SatCompiler, cons_type: Var, name: Var, loops: list, expr: Expr, level: Number):
	"""
	"""

	if str(cons_type) not in CONST_TYPES:
		compiler << SatValueError(f'Unknown constraint type {cons_type}', target=cons_type)
	elif (str(cons_type) == CONS_OPT) and (level is not None):
		compiler << SatValueError(f'Optimality constraints have no penalty level.', target=level)
	elif (str(cons_type) == CONS_INT) and (level is None):
		compiler << SatValueError(f'Integrity constraints must have a penalty level.', target=cons_type)
	elif (level is not None and not level.is_int):
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
		get_expr(compiler, expr)

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
		compiler < SatWarning(f"Duplicate definition for loop variable `{loop_var}`.", target=loop_var)

	## Push compile memory scope
	compiler.push()

	## Evaluate Loop Parameters
	start, stop, step = tuple((compiler.eval(k) if (k is not None) else None) for k in loop_range)

	## Check Values
	if not start.is_int:
		compiler << SatTypeError(f'Loop start must be an integer.', target=start)
	else:
		start = int(start)

	if not stop.is_int:
		compiler << SatTypeError(f'Loop end must be an integer.', target=stop)
	else:
		start = int(start)

	if step is None:
		if start < stop:
			step = 1
		else:
			step = -1
	elif not step.is_int:
		compiler << SatTypeError(f'Loop step must be an integer.', target=step)
	else:
		step = int(step)

	if (start < stop and step < 0) or (start > stop and step > 0):
		compiler << SatTypeError(f'Inconsistent Loop definition.', target=start)

	## Set loop variable to itself
	compiler.memset(loop_var, loop_var)

	## Evaluate loop conditionals
	def_loop_conds(compiler, loop_conds)

	compiler.checkpoint()

def def_loop_conds(compiler: SatCompiler, loop_conds: list):
	""" DEF_LOOP_CONDS
		==============
	"""
	for i, cond in enumerate(loop_conds):
		try:
			loop_conds[i] = get_common_expr(compiler, cond)
		except SatReferenceError as error:
			compiler << error
		except Exception as error:
			raise error
	else:
		compiler.checkpoint()

def get_common_expr(compiler, expr: Expr) -> Expr:
	""" DEF_COMMON_EXPR
		========

		Checks for expression consistency.
		1. Variable definition
		2. Proper indexing
		3. Constant evaluation
	"""
	expr = compiler.eval_expr(expr)

	return expr


def get_expr(compiler, expr: Expr):
	""" DEF_EXPR
		========

		Checks for expression consistency.
		1. Constant evaluation
		2. Proper indexing
	"""
	expr = compiler.eval_expr(expr)

	## Translates to C.N.F.
	expr = expr.cnf

	return expr




	


	

		






		