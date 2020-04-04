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
from .sat_core import stderr, stdout, Source
from .sat_types import SatError
from .sat_types import SatType, Number, Var, Array
from .sat_types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT
from .sat_types.symbols import PREC, DIR, LOAD, OUT, EPSILON, N0

class SatCompilerError(SatError):
	pass

class SatValueError(SatError):
	pass

class SatTypeError(SatError):
	pass

class SatReferenceError(SatError):
	pass

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
			raise SatReferenceError(f"Reference Error: Undefined variable {name}", target=name)

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

	def __init__(self):
		## Initialize parser
		self.parser = SatParser()

		self.source = None

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

		## Errors
		self.errors = None

	def __call__(self, source : str):
		## Parse
		self.source = Source(source)
		self.bytecode = self.parser(self.source)

		## Compile
		self.compile(self.bytecode)
		
		return self.sco

	def compile(self, bytecode : str):
		self.sco = {}
		self.errors = []
		for stmt in bytecode:
			self.errors.extend(self.run(stmt))

		for error in self.errors:
			error.launch(error, self.source)

		if self.flag:
			stderr << f":: Compilation terminated ::"

	def run(self, stmt : Stmt):
		yield from self.callbacks[stmt.name](*stmt.args)

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
			yield SatValueError(f'Value Error: ´#prec´ expected 1 argument, got {argc}', target=argv[1])

		if type(prec) is Number and prec.is_int and prec > 0:
			self.env[PREC] = prec
		else:
			yield SatTypeError(f'Type Error: Precision must be a positive integer.', target=argv[0])

	def sys_config_epsilon(self, argc : int, argv : list):
		if argc == 1:
			epsilon = argv[0]
		else:
			yield SatValueError(f'Value Error: ´#epsilon´ expected 1 argument, got {argc}', target=argv[1])

		if type(epsilon) is Number and epsilon > 0:
			self.env[EPSILON] = epsilon
		else:
			yield SatTypeError(f'Type Error: Epsilon must be a positive number.', target=argv[0])

	def sys_config_load(self, argc : int, argv : list):
		for fname in argv:
			self.load(fname)

	def load(self, fname : str):
		...

	def sys_config_n0(self, argc : int, argv : list):
		...

	def sys_config_out(self, argc : int, argv : list):
		...

	def sys_config_dir(self, argc : int, argv : list):
		...

	def def_constant(self, name : Var, value : SatType):
		SatType.check_type(value)
		self.memory.memset(name, value)			

	def def_array(self, name, shape, buffer):
		shape = tuple(self.eval(n) for n in shape)

		dim = len(shape)

		array_buffer = {}

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
			
			array_buffer[idx] = val

        
        elif not all((type(i) is int) for i in idx):
            error_msg = 

		self.memory[name] = Array(name, shape, buffer)

	def def_constraint(self, type_, name, loops, expr, level):
		...

	@property
	def flag(self):
		return bool(self.errors)
