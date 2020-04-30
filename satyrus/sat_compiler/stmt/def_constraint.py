""" :: DEF_CONSTRAINT ::
	====================

Two DEF_CONSTRAINT statement bytecodes:
(
'DEF_CONSTRAINT',
	Var('int'),
	Var('A'),
	[
		('@', Var('i'), (Number('1'), Var('m'), None), None),
	 	('$', Var('j'), (Number('1'), Var('n'), None), None)
	],
	('[]', ('->', ('[]', Var('x'), Var('i')), Var('y')), Var('j')),
	Number('0')
)
(
'DEF_CONSTRAINT',
	Var('opt'),
	Var('X'),
	[
		('@', Var('i'), (Number('1'), Var('m'), None), None),
		('@', Var('j'), (Number('1'), Var('n'), None), [('!=', Var('i'), Var('j'))])])
	],
	('[]', ('<-', ('[]', Var('x'), Var('i')), Var('y')), Var('j')),
	Number('1')
)
"""

## Local
from satlib import arange, stack
from ...sat_types.error import SatValueError, SatTypeError
from ...sat_types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL
from ...sat_types import Number, Constraint, Loop

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}

def def_constraint(compiler, type_, name, loops, expr, level):
	if type_ not in {'int', 'opt'}:
		yield SatValueError(f'Unknown constraint type {type_}', target=type_)
		return
	elif type_ == 'int' and level is not None:
			yield SatValueError(f'Integrity constraints have no penalty level.', target=level)
			return
	else:
		## Add new constraint
		compiler.sco[type_][name] = {}
		yield from def_constraint_loops(compiler, name, loops, expr)

def def_constraint_loops(compiler, type_, name, loops, expr):
	"""
	"""
	if len(loops) >= 1:
		compiler.memory.push()

		loop, *loops = loops

		loop_type, loop_var, loop_range, loop_conds = loop

		## Check Loop Type
		if loop_type not in LOOP_TYPES:
			yield SatTypeError(f'Invalid loop type {loop_type}', target=loop_type)

		## Evaluate Loop Parameters
		start = compiler.eval(loop_range[0])
		stop = compiler.eval(loop_range[1])
		step = compiler.eval(loop_range[2])

		## Check Values
		if not start.is_int:
			yield SatTypeError(f'Loop start must be an integer.', target=start)
			return

		if not stop.is_int:
			yield SatTypeError(f'Loop end must be an integer.', target=stop)
			return

		if step is None:
			if start < stop:
				step = Number('1')
			else:
				step = Number('-1')

		elif not step.is_int:
			yield SatTypeError(f'Loop step must be an integer.', target=step)
			return

		if (start < stop and step < 0) or (start > stop and step > 0):
			yield SatTypeError(f'Inconsistent Loop definition.', target=start)
			return

		## Check Conditions
		for cond in loop_conds:
			expr = compiler.eval_expr(cond)

		range_ = arange(int(start), int(stop), int(step))

		## Go deeper in nested loops
		yield from def_constraint_loops(compiler, type_, name, loops, expr)

		## Clear memory stack
		compiler.memory.pop()
	else:
		## Evaluate Expression
		def_constraint_expr(compiler, name, expr)

def def_constraint_expr(compiler, name, expr):
	"""
	"""
	...

		






		