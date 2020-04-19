""" :: Sat Compiler ::
	==================

The SATyrus Compiler translates .sbc (SATyrus Bytecode) into
.sco (SATyrus compiled object), basically a Python dictionary
suitable for json serialization.
"""
## Standard Library
import os

## Local
from ..sat_parser import SatParser
from ..sat_core import stderr, stdout, Source
from ..sat_types import SatType, String, Number, Var, Array
from ..sat_types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT
from ..sat_types.symbols import PREC, DIR, LOAD, OUT, EPSILON, N0

from .memory import Memory
from .stmt import sys_config, def_constant, def_array, def_constraint

class SatCompiler:
	"""
	"""

	callbacks = {
		SYS_CONFIG : sys_config,
		DEF_CONSTANT : def_constant,
		DEF_ARRAY : def_array,
		DEF_CONSTRAINT : def_constraint
	}

	def __init__(self, source : Source, parser : SatParser = None):
		## Initialize parser
		self.source = source
		self.parser = parser if parser is not None else SatParser(self.source)

		assert self.source is self.parser.source

		## Memory
		self.memory = Memory()

		## Environment
		self.env = Memory({
			PREC : 16,
			DIR : os.path.abspath(os.getcwd()),
			N0 : 1,
			EPSILON : 1E-05,
		})
	
		## Compiled Object
		self.sco = None

		## Errors
		self.errors = None

	@property
	def bytecode(self):
		return self.parser.bytecode

	def compile(self):
		self.sco = {}
		self.errors = []

		for stmt in self.bytecode:
			self.errors.extend(self.run(stmt))

		if self.errors:
			for error in self.errors:
				error.launch()
			stderr[0] << f":: Compilation terminated ::"
			return None

		return self.sco

	def run(self, stmt):
		name, *args = stmt
		yield from self.callbacks[name](self, *args)

	def eval(self, value):
		if type(value) is Var:
			## Get value from memory
			memval = self.memory.memget(value)

			## Copy error tracking information
			memval.lexinfo = value.lexinfo
			
			return memval
		elif type(value) is Expr:
			raise NotImplementedError('Evaluating Expressions is not ready yet.')
		else:
			return value