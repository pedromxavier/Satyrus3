""" :: Memory ::
	============
"""

## Local
from ...satlib import Stack, join
from ..types.error import SatReferenceError
from ..types import Var, SatType

class Memory(object):
	""" Satyrus Compiler Memory
	"""
	def __init__(self, defaults: dict=None):
		self.__memory = [{} if defaults is None else defaults]

	def __str__(self):
		return join(">\n", [join("\n", (f"{key}:\t{val}" for key, val in layer.items())) for layer in self])

	def __iter__(self):
		return iter(self.__memory)

	def push(self):
		"""
		"""
		self.__memory.append({})

	def pop(self, n: int=1):
		"""
		"""
		for _ in range(n):
			if len(self.__memory) > 1:
				self.__memory.pop()
			else:
				raise ValueError("Can't remove global scope.")

	def clear(self):
		"""
		"""
		## Clear list
		del self.__memory[:]
		
		## Add global scope
		self.__memory.append({})

	def memset(self, name: Var, value: SatType):
		"""
		"""
		self.__memory[-1][name] = value

	def memget(self, name: Var):
		"""
		"""
		i = len(self.__memory) - 1
		while i >= 0:
			try:
				return self.__memory[i][name]
			except KeyError:
				i -= 1
		else:
			raise SatReferenceError(f"Undefined variable `{name}`.", target=name)