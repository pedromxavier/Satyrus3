from ..sat_types.error import SatReferenceError
from ..sat_types import Var

class Memory(dict):
	"""
	"""
	def __init__(self, defaults=None):
		dict.__init__(self, defaults)

	def __str__(self):
		return "\n".join(f"{key}:\n\t{val}" for key, val in self.items())

	def __getitem__(self, name):
		try:
			dict.__getitem__(self, name)
		except KeyError:
			raise SatReferenceError(f"Undefined variable {name}.", target=name)

	def memset(self, name : Var, value):
		assert type(name) is Var
		if type(value) is Var:
			self[name] = self[value]
		else:
			self[name] = value

	def memget(self, name : Var):
		assert type(name) is Var
		return self[name]