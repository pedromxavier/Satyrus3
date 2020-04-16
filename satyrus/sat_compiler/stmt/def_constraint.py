from ...sat_types.error import SatValueError

def def_constraint(self, type_, name, loops, expr, level):
		if type_ not in {'int', 'opt'}:
			yield SatValueError(f'Unknown constraint type {type_}', target=type_)
			yield StopIteration
		else:
			raise NotImplementedError