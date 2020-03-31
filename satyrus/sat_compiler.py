""" :: Sat Compiler ::
	==================

The SATyrus Compiler translates .sbc (SATyrus Bytecode) into
.sco (SATyrus compiled object), basically a Python dictionary
suitable for json serialization.
"""
## Standard Library
import os

## Local
from .sat_parser import SatParser, Stmt
from .sat_core import stderr, stdout
from .sat_types import SatError
from .sat_types import SatType, Number, Var, Array
from .sat_types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT

class SatCompilerError(SatError):
	pass

class SatReferenceError(SatError):
	pass

class Memory(dict):

	def __init__(self, defaults=None):
		dict.__init__(self, defaults)

	def __str__(self):
		return "\n".join(f"{key}:\n\t{val}" for key, val in self.items())

	def __getitem__(self, name):
		try:
			dict.__getitem__(self, name)
		except KeyError:
			stderr << f"Unknown name {name}."
			raise SatReferenceError(SatError)

	def memset(self, name : Var, value):
		assert type(name) is Var
		if type(value) is Var:
			self[name] = self[value]
		else:
			self[name] = value

	def memget(self, name : Var):
		assert type(name) is Var
		return self[name]

class SatCompiler:
	"""
	"""
	callbacks = {
		SYS_CONFIG : sys_config,
		DEF_CONSTANT : def_constant,
		DEF_ARRAY : def_array,
		DEF_CONSTRAINT : def_constraint
	}

	def __init__(self):
		## Initialize parser
		self.parser = SatParser()

		## Memory
		self.memory = Memory()

		## Environment
		self.env = Memory({
			'prec' : 16,
			'dir' : os.path.abspath(os.getcwd()),
		})

		## Bytecode
		self.bytecode = None
	
		## Compiled Object
		self.sco = None

	def __call__(self, source : str):
		self.compile(source)
		return self.sco

	def compile(self, source : str):
		self.bytecode = self.parser(source)
		self.sco = {}
		for stmt in self.bytecode:
			try:
				self.run(stmt)
			except SatCompilerError:
				return None
			except SatReferenceError:
				return None
			finally:
				stdout << ":: Compilation terminated ::"

	def run(self, stmt : Stmt):
		self.callbacks[stmt.name](*stmt.args)
		
	def sys_config(self, name : Var, value):
		self.env[name] = value
	
	def def_constant(self, name : Var, value : SatType):
		SatType.check_type(value)
		try:
			self.memory.memset(name, value)
		except SatReferenceError:
			
			raise

	def def_array(self, name, shape, buffer):
		buffer = {idx:val for idx, val in buffer}

		self.memory[name] = Array(name, shape, buffer)

	def def_constraint(self, type_, name, level, loops, expr):
		...