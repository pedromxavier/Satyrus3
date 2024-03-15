"""
satyrus/compiler/memory.py
--------------------------
"""

## Local
from ..error import SatReferenceError
from ..types import Var, SatType

class Memory(object):
	""" Satyrus Compiler Memory
	"""
	def __init__(self, defaults: dict=None):
		self.__memory = [{} if defaults is None else defaults]

	def __str__(self):
		return ">\n".join("\n".join(f"{key}:\t{val}" for key, val in layer.items()) for layer in self.__memory)

	def __iter__(self):
		i = len(self.__memory) - 1
		found = set()
		while i >= 0:
			for key in self.__memory[i]:
				if key not in found:
					yield self.__memory[i][key]
					found.add(key)
				else:
					continue
			else:
				i -= 1

	def __getitem__(self, key):
		i = len(self.__memory) - 1
		while i >= 0:
			try:
				return self.__memory[i][key]
			except KeyError:
				i -= 1
		else:
			return None

	def __contains__(self, item):
		return self[item] is not None

	@property
	def copy(self):
		new_mem = self.__class__()
		new_mem.__memory = [layer.copy() for layer in self.__memory]
		return new_mem

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
		# Clear list
		del self.__memory[:]
		
		# Add global scope
		self.__memory.append({})

	def memset(self, name: Var, value: SatType):
		"""
		"""
		self.__memory[-1][name] = value

	def memget(self, name: Var):
		"""
		"""
		value = self[name]
		if value is None:
			raise SatReferenceError(f"Undefined variable `{name}`.", target=name)
		else:
			return value