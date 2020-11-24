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
	def_constraint_type_level(compiler, cons_type, level)

	## Evaluate constraint loops
	indices = []

	def_constraint_loops(compiler, loops, indices)

	## Evaluate constraint expr
	def_constraint_expr(compiler, loops, indices, expr)

	constraint = Constraint(cons_type, name, loops, expr, level)

	## Register constraint to compiler memory
	def_constraint_name(compiler, name, constraint)

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

def def_constraint_loops(compiler: SatCompiler, loops: list, indices: list) -> None:
	"""
	"""

	sub_indices = [()]

	var_stack = Stack()

	## temporary compiler context
	with compiler as comp:

		depth = 0

		# extract loop properties
		for (l_type, l_var, l_bounds, l_conds) in loops:

			depth += 1

			if l_var in comp:
				compiler < SatWarning(f"Variable `{l_var}` redefinition.", target=l_var)

			var_stack.push(l_var)

			## check for boundary consistency
			# extract loop boundaries
			start, stop, step = l_bounds

			# evaluate variables
			start = comp.eval()

			if step is None:
				step = Number('1')

			elif step == Number('0'):
				compiler << SatValueError('Step must be non-zero.', target=step)

			if ((start < stop) and (step < 0)) or ((start > stop) and (step > 0)):
				compiler << SatValueError('Inconsistent loop definition', target=start)
			
			compiler.checkpoint()

			## define condition
			if l_conds is None:
				def condition(index: tuple):
					return True
			else:
				## Compile condition expressions
				def condition(index: tuple):
					table = { i : v for i, v in enumerate(var_stack) }

					for i in range(depth): comp.memset(table[i], index[i])

					return all([comp.eval(cond) for cond in l_conds])
					

			sub_indices = [(*J, i) for J in sub_indices for i in arange(start, stop, step)]
			sub_indices = [I for I in sub_indices if condition(I)]

	
			
	
def def_constraint_expr(compiler: SatCompiler, loops: list, indices: list, expr: Expr) -> None:
	"""
	"""
	...

def def_constraint_name(compiler: SatCompiler, name: Var, constraint: Constraint):
	if name in compiler:
		compiler < SatWarning(f"Variable `{name}` overriden by constraint definition.", target=name)
	
	compiler.memset(name, constraint)