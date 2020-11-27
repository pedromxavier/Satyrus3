""" :: DEF_CONSTRAINT ::
	====================

	STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it
from functools import reduce

## Local
from ....satlib import arange, Stack, stdout, join
from ..compiler import SatCompiler
from ...types.error import SatValueError, SatTypeError, SatReferenceError, SatExprError, SatWarning
from ...types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL, T_IDX
from ...types.symbols import CONS_INT, CONS_OPT
from ...types import Var, String, Number, Constraint, Array
from ...types.expr import Expr

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}

def def_constraint(compiler: SatCompiler, cons_type: String, name: Var, loops: list, expr: Expr, level: Number):
	""" DEF_CONSTRAINT
		==============
	"""
	## Check constraint type and level
	def_constraint_type_level(compiler, cons_type, level)

	## Evaluate constraint loops
	indices = [] # loop indexing
	variables = {} # var bounds

	def_constraint_loops(compiler, loops, variables, indices)

	return

	## Evaluate constraint expr
	def_constraint_expr(compiler, cons_type, variables, indices, expr)

	return

	## constraint = Constraint()

	## Register constraint to compiler memory
	## def_constraint_name(compiler, name, constraint)

def def_constraint_type_level(compiler: SatCompiler, cons_type: String, level: Number):
	"""
	"""
	if str(cons_type) not in CONST_TYPES:
		compiler << SatTypeError(f"Invalid constraint type {cons_type}. Options are: `int`, `opt`.", target=cons_type)

	if str(cons_type) == CONS_OPT and level is not None:
		compiler << SatTypeError("Invalid penalty level for optimality constraint.", target=level)

	if str(cons_type) == CONS_INT and (level < 0 or not level.is_int):
		compiler << SatValueError(f"Invalid penalty level {level}. Must be positive integer.", target=level)

	compiler.checkpoint()

def def_constraint_loops(compiler: SatCompiler, loops: list, variables: dict, indices: list) -> None:
	"""
	"""

	sub_indices = [{}]

	## temporary compiler context
	with compiler as comp:

		depth = 0

		# extract loop properties
		# pylint: disable=unused-variable
		for (l_type, l_var, l_bounds, l_conds) in loops:

			depth += 1

			if l_var in comp:
				compiler < SatWarning(f"Variable `{l_var}` redefinition.", target=l_var)

			variables[l_var] = [None, None]

			## check for boundary consistency
			# extract loop boundaries
			start, stop, step = l_bounds

			# evaluate variables
			start = comp.evaluate(start, miss=True, calc=True)
			stop = comp.evaluate(stop, miss=True, calc=True)
			step = comp.evaluate(step, miss=True, calc=True, null=True) ## accepts null (None) as possible value

			if step is None:
				if start <= stop:
					step = Number('1')
				else:
					step = Number('-1')

			elif step == Number('0'):
				compiler << SatValueError('Step must be non-zero.', target=step)

			if ((start < stop) and (step < 0)) or ((start > stop) and (step > 0)):
				compiler << SatValueError('Inconsistent loop definition', target=start)
			
			compiler.checkpoint()

			## Run through all indices
			sub_indices = [{**J, l_var: i} for J in sub_indices for i in arange(start, stop, step)]

			## define condition
			if l_conds is not None:
				## Compile condition expressions
				cond = reduce(lambda x, y: x & y, l_conds, Number.T)

				def condition(subcompiler: SatCompiler, scope: dict) -> bool:
					subcompiler.push(scope)
					ans = subcompiler.evaluate(cond, miss=True, calc=True)
					subcompiler.pop()
					return bool(ans)

				## filter indices
				sub_indices = [I for I in sub_indices if condition(comp, I)]
		else:
			indices.extend(sub_indices)

		for index in indices:
			for var, value in index.items():
				## Updates minimum for this variable
				if variables[var][0] is None or value < variables[var][0]:
					variables[var][0] = value
				## Updates maximum for this variable					
				if variables[var][1] is None or value > variables[var][1]:
					variables[var][1] = value

	compiler.checkpoint()			
	
def def_constraint_expr(compiler: SatCompiler, cons_type: String, variables: set, indices: list, expr: Expr):
	"""
	"""
	## Reduces expression to simplest form
	subexpr = Expr.simplify(expr)

	# pylint: disable=no-member
	if str(cons_type) == CONS_INT and not Expr.logical(subexpr):
		compiler << SatExprError("Integrity constraint expressions must be purely logical.", target=expr)
	
	## Checks for undefined variables + evaluate constants
	
	## Adds inner scope where inside-loop variables
	## point to themselves. This prevents both older
	## variables from interfering in evaluation and
	## also undefined loop variables.
	compiler.push({var: var for var in variables})
	## evaluation
	subexpr = compiler.evaluate(subexpr, miss=True, calc=True, null=False)
	## Last but not least, removes this artificial scope
	compiler.pop()


	# find all indexings
	idx_func = (lambda p: (type(p) is Expr) and (p.head == T_IDX))

	for indexing in Expr.seek(subexpr, idx_func):
		array, index = indexing.tail
		if type(array) is not Array:
			compiler << SatTypeError(f"Invalid indexing to non-array of type {type(array)}.", target=indexing)
		

def def_constraint_name(compiler: SatCompiler, name: Var, constraint: Constraint):
	if name in compiler:
		compiler < SatWarning(f"Variable `{name}` overriden by constraint definition.", target=name)
	
	compiler.memset(name, constraint)