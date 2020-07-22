""" :: Sat Compiler ::
	==================

The SATyrus Compiler translates .sbc (SATyrus Bytecode) into
.sco (SATyrus compiled object), basically a Python dictionary
suitable for json serialization.
"""
## Standard Library
import os

## Local
from satlib import system, stderr, stdout, Source, Stack

from ..parser import SatParser
from ..types.error import SatError, SatTypeError, SatCompilerError, SatReferenceError, SatExit
from ..types import SatType, String, Number, Var, Array, Expr
from ..types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT
from ..types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA

from .memory import Memory
from .stmt import sys_config, def_constant, def_array, def_constraint

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

	callbacks = {
		SYS_CONFIG : sys_config,
		DEF_CONSTANT : def_constant,
		DEF_ARRAY : def_array,
		DEF_CONSTRAINT : def_constraint
	}

	def __init__(self, parser : SatParser = None):
		## Initialize parser
		self.parser = parser if parser is not None else SatParser()

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
		return self.callbacks[name](self, *args)

	def eval(self, value: SatType):
		if type(value) is Var:
			## Rename variable
			var = value

			## Get value from memory
			var_value = self.memory.memget(var)

			## Copy error tracking information
			var_value.lexinfo = value.lexinfo
			
			return var_value

		elif type(value) is Expr:
			## Rename variable
			expr = value

			## Evaluate expression
			expr = self.eval_expr(expr)
			
			## Return solved expression
			return Expr.solve(expr)
		else:
			return value

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


	def eval_expr(self, expr: Expr):
		"""
		"""
		if type(expr) is Expr:
			return Expr.apply(self._apply_eval_expr, expr)
		else:
			return expr

	def _apply_eval_expr(self, value: SatType):
		"""
		"""
		if type(value) is Expr:
			return value
		else:
			return self.eval(value)

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