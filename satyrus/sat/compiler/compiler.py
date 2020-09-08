""" :: Sat Compiler ::
	==================

The SATyrus Compiler translates .sbc (SATyrus Bytecode) into
.sco (SATyrus compiled object), basically a Python dictionary
suitable for json serialization.
"""
## Standard Library
import os

## Local
from satyrus.satlib import system, stderr, stdout, stdwar, Source, Stack

from ..parser import SatParser
from ..types.error import SatError, SatTypeError, SatCompilerError, SatReferenceError, SatExit, SatWarning
from ..types import SatType, String, Number, Var, Array, Expr, Constraint
from ..types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA
from ..types.symbols import CONS_INT, CONS_OPT

from .memory import Memory

class SatCompiler:
	"""
	"""
	DEFAULT_ENV = {
		PREC : 16,
		ALPHA : Number(1.0),
		EPSILON : Number(1E-05),
	}

	## Optimization Level
	O = 0

	def __init__(self, instructions: dict, parser : SatParser = None):
		## Build Instruction Set
		if type(instructions) is not dict:
			raise TypeError("`instructions` must be of type `dict`.")
		elif not instructions:
			raise ValueError("Empty Instruction Set.")
		else:
			self.instructions = instructions

		## Initialize parser
		if type(parser) is not SatParser:
			raise TypeError("`parser` must be of type `SatParser`.")
		elif parser is None:
			self.parser = SatParser()
		else:
			self.parser = parser

		## Memory
		self.memory = Memory()

		## Environment
		self.env = None

		## Errors
		self.error_stack = Stack()

	def __lshift__(self, error: SatError):
		self.error_stack.push(error)

	def __getitem__(self, level: int):
		""" Optimization Level
		"""
		return self.O >= level

	def __lt__(self, warning: SatWarning):
		stdwar << warning
		
	def compile(self, source: Source):
		"""
		"""
		code = 1

		## Input
		self.source = source

		## Parse code into bytecode
		self.bytecode = self.parser.parse(self.source)

		## Set default environment variables
		self.env = self.DEFAULT_ENV.copy()

		## Error collector
		self.errors = []

		for stmt in self.bytecode:
			try:
				stdout[1] << f"> {stmt}"
				self.exec(stmt)
			except SatExit as error:
				code = error.code
				break
		else:
			## Constraint compilation
			constraints = [item for item in self.memory if (type(item) is Constraint)]

			constraints = {
				CONS_INT: [cons for cons in constraints if cons.cons_type == CONS_INT],
				CONS_OPT: [cons for cons in constraints if cons.cons_type == CONS_OPT]
			}

			## value for alpha
			alpha = self.env[ALPHA]

			## value for epsilon
			epsilon = self.env[EPSILON]

			## Penalties
			penalties = {
				0: alpha
			}

			cons_levels = {}

			levels = []

			for cons in constraints[CONS_INT]:
				level = cons.level
				if level not in cons_levels:
					cons_levels[level] = 1
					levels.append(level)
				else:
					cons_levels[level] += 1
			
			

			code = 0
		
		if code:
			stderr[1] << f"> compiler exited with code {code}."
		else:
			stdout[1] << f"> compiler exited with code {code}."
		return code
		
	def p(n: int, penalties):
		if n == 0:
			return 

	def exit(self, code: int):
		raise SatExit(code)

	def dir(self, path: str):
		return system.dir_push(path)

	def exec(self, stmt: tuple):
		name, *args = stmt
		return self.instructions[name](self, *args)

	def eval(self, value: SatType):
		if type(value) is Var:
			## Rename variable
			var = value

			## Get value from memory
			var_value = self.memget(var)

			## Copy error tracking information
			var_value.lexinfo = value.lexinfo
			
			return var_value

		elif type(value) is Expr:
			## Rename variable
			expr = value
			
			## Return solved expression
			return expr
		else:
			if not issubclass(type(value), SatType):
				print(self.memory)
				self << SatTypeError(f'{type(value)} is not a valid Satyrus type for evaluation.', target=value)
				self.checkpoint()
			else:
				return value

	def eval_expr(self, expr: Expr):
		"""
		"""
		if type(expr) is Expr:
			return Expr.back_apply(expr, self._apply_eval_expr)
		else:
			return expr

	def _apply_eval_expr(self, value: SatType):
		"""
		"""
		if type(value) is Expr:
			return value
		else:
			return self.eval(value)

	def __contains__(self, item: Var):
		return (item in self.memory)

	def memset(self, name: Var, value: SatType):
		"""
		"""
		try:
			return self.memory.memset(name, value)
		except SatTypeError as error:
			self << error
		finally:
			self.checkpoint()

	def memget(self, name: Var):
		"""
		"""
		try:
			return self.memory.memget(name)
		except SatReferenceError as error:
			self << error
		finally:
			self.checkpoint()

	
	def push(self):
		""" push memory scope
		"""
		self.memory.push()

	def pop(self, depth: int=1):
		""" pop memory scope
		"""
		self.memory.pop(depth)

	def interrupt(self):
		"""
		"""
		while self.error_stack:
			error = self.error_stack.pop()
			stderr << error
		else:
			self.exit(1)

	def checkpoint(self):
		"""
		"""
		if self.status: self.interrupt()

	@property
	def status(self):
		"""
		"""
		return bool(self.error_stack)