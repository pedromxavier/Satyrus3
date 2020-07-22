""" :: Memory ::
	============
"""

## Local
from satlib import stack, join
from ..types.error import SatReferenceError
from ..types import Var, SatType

class Memory(list):
	""" Satyrus Compiler Memory
	"""
	def __init__(self, defaults: dict=None):
		list.__init__(self, [{} if defaults is None else defaults])

	def __str__(self):
		return join(">\n", [join("\n", (f"{key}:\t{val}" for key, val in layer.items())) for layer in self])

	def push(self):
		"""
		"""
		list.append(self, {})

	def pop(self):
		"""
		"""
		if len(self) > 1:
			list.pop(self, -1)
		else:
			raise ValueError("Can't remove global scope.")

	def clear(self):
		"""
		"""
		## Clear list
		del self[:]
		## Add global scope
		self.append({})

	def memset(self, name: Var, value: SatType):
		"""
		"""
		self[-1][name] = value

	def memget(self, name: Var):
		"""
		"""
		i = len(self) - 1
		while i >= 0:
			try:
				return self[i][name]
			except KeyError:
				i -= 1
		else:
			raise SatReferenceError(f"Undefined variable `{name}`.", target=name)