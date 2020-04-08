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
from ..sat_types import SatError
from ..sat_types import SatType, String, Number, Var, Array, NULL
from ..sat_types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT
from ..sat_types.symbols import PREC, DIR, LOAD, OUT, EPSILON, N0

class SatCompilerError(SatError):
	TITLE = 'Compiler Error'

class SatValueError(SatError):
	TITLE = 'Value Error'

class SatTypeError(SatError):
	TITLE = 'Type Error'

class SatReferenceError(SatError):
	TITLE = 'Reference Error'

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

class SatCompiler:
	"""
	"""
	callbacks = {
		SYS_CONFIG : sys_config,
		DEF_CONSTANT : def_constant,
		DEF_ARRAY : def_array,
		DEF_CONSTRAINT : def_constraint
	}

	sys_config_options = {
		PREC : sys_config_prec,
		DIR : sys_config_dir,
		LOAD : sys_config_load,
		EPSILON : sys_config_epsilon,
		N0 : sys_config_n0,
		OUT : sys_config_out,
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

		## Bytecode
		self.bytecode = None
	
		## Compiled Object
		self.sco = None

		## Errors
		self.errors = None

	def __call__(self, source : Source):
		## Parse
		self.source = source
		self.bytecode = self.parser(self.source)

		## Compile
		self.compile(self.bytecode)
		
		return self.sco

	def compile(self, bytecode : str):
		self.sco = {}
		self.errors = []
		for stmt in bytecode:
			self.run(stmt)

		for error in self.errors:
			error.launch()

		if self.errors:
			stderr[0] << f":: Compilation terminated ::"

	def run(self, stmt):
		name, args = stmt
		yield from self.callbacks[name](*args)

	def eval(self, value):
		if type(value) is Var:
			## Get value from memory
			memval = self.memory.memget(value)

			## Copy error tracking information
			memval.lineno = value.lineno
			memval.lexpos = value.lexpos
			memval.chrpos = value.chrpos

			return memval
		else:
			return value

	def sys_config(self, name : str, args : list):
		yield from self.sys_config_options[name](len(args), args)

	def sys_config_prec(self, argc : int, argv : list):
		if argc == 1:
			prec = argv[0]
		else:
			yield SatValueError(f'´#prec´ expected 1 argument, got {argc}', target=argv[1])

		if type(prec) is Number and prec.is_int and prec > 0:
			self.env.memset(PREC, prec)
		else:
			yield SatTypeError(f'Precision must be a positive integer.', target=argv[0])

	def sys_config_epsilon(self, argc : int, argv : list):
		if argc == 1:
			epsilon = argv[0]
		else:
			yield SatValueError(f'´#epsilon´ expected 1 argument, got {argc}', target=argv[1])

		if type(epsilon) is Number and epsilon > 0:
			self.env.memset(EPSILON, epsilon)
		else:
			yield SatTypeError(f'Epsilon must be a positive number.', target=argv[0])

	def sys_config_load(self, argc : int, argv : list):
		for fname in argv:
			yield from self.load(fname)

	def load(self, fname : str):
		...

	def sys_config_n0(self, argc : int, argv : list):
		if argc == 1:
			n0 = argv[0]
		else:
			yield SatValueError(f'´#n0´ expected 1 argument, got {argc}.', target=argv[1])

		if type(n0) is Number and n0 > 0:
			self.env.memset(N0, n0)
		else:
			yield SatTypeError(f'n0 must be a positive number.', target=argv[0])


	def sys_config_out(self, argc : int, argv : list):
		raise NotImplementedError

	def sys_config_dir(self, argc : int, argv : list):
		raise NotImplementedError

	def def_constant(self, name : Var, value : SatType):
		try:
			self.memory.memset(name, value)
		except SatReferenceError as error:
			yield error

	def def_array(self, name, shape, buffer):
		shape = tuple(self.eval(n) for n in shape)
		shape_errors = list(self.def_array_shape(shape))

		if shape_errors:
			self.memory[name] = NULL
			yield from shape_errors
			yield StopIteration
		
		array_buffer = {}

		buffer_errors = list(self.def_array_buffer(shape, buffer, array_buffer))

		if buffer_errors:
			self.memory[name] = Array(name, shape)
			yield from buffer_errors
			yield StopIteration

		else:
			self.memory[name] = Array(name, shape, array_buffer)

	def def_array_shape(self, shape):
		for n in shape:
			if not n.is_int:
				yield SatTypeError(f'Array dimensions must be integers.', target=n)
			if not n > 0:
				yield SatValueError(f'Array dimensions must be positive numbers.', target=n)
	
	def def_array_buffer(self, shape, buffer, array_buffer):
		for idx, val in buffer:
			idx = tuple(self.eval(i) for i in idx)

			if len(idx) > len(shape):
				yield SatValueError(f'Too much indices for {len(shape)}-dimensional array', target=idx[len(shape)])
				
			for i, n in zip(idx, shape):
				if not i.is_int:
					yield SatTypeError(f'Array indices must be integers.', target=i)
					
				if not 1 <= i <= n:
					yield SatValueError(f'Indexing ´{i}´ is out of bounds [1, {n}]', target=i)

			val = self.eval(val)

			if type(val) is not Number:
				yield SatValueError(f'Array elements must be numbers.', target=val)
			else:
				array_buffer[idx] = val

	def def_constraint(self, type_, name, loops, expr, level):
		if type_ not in {'int', 'opt'}:
			yield SatValueError(f'Unknown constraint type {type_}', target=type_)
			yield StopIteration
		else:
			raise NotImplementedError