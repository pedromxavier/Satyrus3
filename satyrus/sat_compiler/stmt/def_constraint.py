"""
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
		('@', Var('j'), (Number('1'), Var('n'), None), [Var('i')])
	],
	('[]', ('<-', ('[]', Var('x'), Var('i')), Var('y')), Var('j')),
	Number('1')
)
"""

from ...sat_types.error import SatValueError
from ...sat_types import Constraint, ConstraintLoop

def def_constraint(compiler, type_, name, loops, expr, level):
	if type_ not in {'int', 'opt'}:
		yield SatValueError(f'Unknown constraint type {type_}', target=type_)
		yield StopIteration
	else:
		for loop in loops:
			loop_type, loop_var, (start, stop, step), conditions = loop
