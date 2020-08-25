""" :: Sat Compiler ::
	==================

The SATyrus Compiler translates .sbc (SATyrus Bytecode) into
.sco (SATyrus compiled object), basically a Python dictionary
suitable for json serialization.
"""
## Standard Library
import os

## Local
from satlib import system, stderr, stdout, stdwar, Source, Stack

from ..parser import SatParser
from ..types.error import SatError, SatTypeError, SatCompilerError, SatReferenceError, SatExit, SatWarning
from ..types import SatType, String, Number, Var, Array, Expr
from ..types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA

from .memory import Memory

class SatCompiler:
	"""
	"""
	DEFAULT_SCO = {

	}
	
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
	
		## Compiled Object
		self.sco = None

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
		try:
			## Input
			self.source = source

			## Parse code into bytecode
			self.bytecode = self.parser.parse(self.source)

			## Set default environment variables
			self.env = Memory(self.DEFAULT_ENV)

			## Set default output
			self.sco = Memory(self.DEFAULT_SCO)

			## Error collector
			self.errors = []

			for stmt in self.bytecode:
				try:
					self.exec(stmt)
				except SatExit as error:
					code = error.code
					break
			else:
				code = 0
			
			## Output
			return self.sco
		except Exception as error:
			raise error
		finally:
			self.source = None
			self.bytecode = None
			self.env = None
			self.sco = None
			self.errors = None
			self.memory.clear()
			return code

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
			if self[1]:
				return Expr.solve(expr)
			else:
				return expr
		else:
			if not issubclass(type(value), SatType):
				self << SatTypeError(f'{type(value)} is not a valid Satyrus Type for evaluation.', target=value)
				self.checkpoint()
			else:
				return value

	def eval_expr(self, expr: Expr):
		"""
		"""
		if type(expr) is Expr:
			return Expr.back_apply(self._apply_eval_expr, expr)
		else:
			return expr

	def _apply_eval_expr(self, value: SatType):
		"""
		"""
		if type(value) is Expr:
			return value
		else:
			return self.eval(value)

	def __enter__(self, *args, **kwargs):
		...

	def __exit__(self, *args, **kwargs):
		...

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
		self.exit(self.status)

	def checkpoint(self):
		"""
		"""
		if self.status: self.interrupt()

	@property
	def status(self):
		"""
		"""
		return int(not self.error_stack)