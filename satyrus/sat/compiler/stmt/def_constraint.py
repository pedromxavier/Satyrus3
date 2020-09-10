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
	""" DEF_CONSTRAINT
		==============
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
		if level is None:
			level = 0
		else:
			level = int(level)

		## Create constraint
		constraint = Constraint(name, cons_type, level)

		## Compile Constraint Loops
		for loop in loops:
			def_constraint_loop(compiler, loop, constraint)

		compiler.checkpoint()

		## Compile expression
		constraint.set_expr(expr)

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

	## Evaluate Loop Parameters
	start, stop, step = tuple((compiler.eval(k) if (k is not None) else None) for k in loop_range)

	## Check Values
	if not start.is_int:
		compiler << SatTypeError(f'Loop start must be an integer.', target=start)

	if not stop.is_int:
		compiler << SatTypeError(f'Loop end must be an integer.', target=stop)

	if step is None:
		if start < stop:
			step = Number('1')
		else:
			step = Number('1')
	elif not step.is_int:
		compiler << SatTypeError(f'Loop step must be an integer.', target=step)

	if (start < stop and step < 0) or (start > stop and step > 0):
		print(start < stop)
		print(step < 0)
		compiler << SatValueError(f'Inconsistent Loop definition.', target=start)

	compiler.checkpoint()

	## Evaluate loop conditionals
	conds = []

	def_loop_conds(compiler, loop_conds, conds)

	constraint.add_loop(loop_var, loop_type, start, stop, step, conds)

	compiler.checkpoint()

def def_loop_conds(compiler: SatCompiler, loop_conds: list, conds: list):
	""" DEF_LOOP_CONDS
		==============
	"""
	## No conditions at all
	if loop_conds is None:
		return

	for cond in loop_conds:
		try:
			conds.append(compiler.eval_expr(cond))
		except SatReferenceError as error:
			compiler << error
		except Exception as error:
			raise error
	else:
		compiler.checkpoint()