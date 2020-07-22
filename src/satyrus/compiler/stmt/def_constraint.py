""" :: DEF_CONSTRAINT ::
	====================

	STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it

## Local
from satlib import arange, stack
from ...types.error import SatValueError, SatTypeError
from ...types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL
from ...types import Number, Expr

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {'int', 'opt'}

def def_constraint(compiler, const_type, name: Var, loops, expr, level):
	"""
	"""
	if const_type not in CONST_TYPES:
		raise SatValueError(f'Unknown constraint type {const_type}', target=const_type)
	elif const_type == 'int' and level is not None:
		raise SatValueError(f'Integrity constraints have no penalty level.', target=level)
	else:
		## Get variables and indices from loops
		var_stack, indices = def_constraint_loops(compiler, loops)

		## Add new constraint
		compiler.sco[const_type][name] = (const_type, var_stack, indices, expr)

def def_constraint_loops(compiler, loops: list):
	""" def_constraint_loops(compiler, loops: list) -> (var_stack: tuple, indices: list)

		Returns a tuple containing the variables from outer to innermost, and a list of indices to be assigned to these variables in each loop. 
	"""
	var_stack, indices_stack = def_constraint_loop(compiler, loops)

	indices = list(it.product(*indices_stack))

	return var_stack, indices

def def_constraint_loop(compiler, loops, var_stack=None, indices_stack=None):
	if len(loops) >= 1:
		## Push compile memory scope
		compiler.memory.push()

		## Untangle loop
		(loop, *loops) = loops

		## Get loop attributes
		(loop_type, loop_var, loop_range, loop_conds) = loop

		## Add Variable to stack
		if var_stack is None:
			var_stack = (loop_var,)
		else:
			var_stack = (*var_stack, loop_var)

		## Check Loop Type
		if loop_type not in LOOP_TYPES:
			raise SatTypeError(f'Invalid loop type {loop_type}', target=loop_type)

		## Evaluate Loop Parameters
		start = compiler.eval(loop_range[0])
		stop = compiler.eval(loop_range[1])
		step = compiler.eval(loop_range[2])

		## Check Values
		if not start.is_int:
			raise SatTypeError(f'Loop start must be an integer.', target=start)

		if not stop.is_int:
			raise SatTypeError(f'Loop end must be an integer.', target=stop)

		if step is None:
			if start < stop:
				step = Number('1')
			else:
				step = Number('-1')

		elif not step.is_int:
			raise SatTypeError(f'Loop step must be an integer.', target=step)
			
		if (start < stop and step < 0) or (start > stop and step > 0):
			raise SatTypeError(f'Inconsistent Loop definition.', target=start)

		## Build Indices list
		indices = list(arange(int(start), int(stop), int(step)))

		## Check Conditions
		conds = [Expr.apply(compiler.eval_expr, cond) for cond in loop_conds]

		## Build function from Conditions
		def f(var, i):
			for cond in conds:
				for j in range(len(var)):
					compiler.memset(var[j], i[j])
		
		## Filter Indices list
		indices = [(var, i) for (var, i) in indices if f(var, i)]

		if indices_stack is None:
			indices_stack = (indices,)
		else:
			indices_stack = (*indices_stack, indices)

		## Go deeper in nested loops
		var_stack, indices_stack = def_constraint_loop(compiler, loops, var_stack, indices_stack)

		## Clear memory stack
		compiler.memory.pop()

	## Output
	return var_stack, indices_stack

def def_constraint_expr(compiler, name, expr):
	"""
	"""
	...

		






		