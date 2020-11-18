""" :: Sat Compiler ::
	==================
"""
## Standard Library
import traceback
import os
import math

## Local
from satyrus.satlib import log, system, stderr, stdout, stdwar, Source, Stack, join

from ..parser import SatParser
from ..types.error import SatValueError, SatTypeError, SatCompilerError, SatReferenceError
from ..types.error import SatError, SatExit, SatWarning
from ..types import SatType, String, Number, Var, Array, Constraint
from ..types.expr import Expr
from ..types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA, RUN_INIT, RUN_SCRIPT
from ..types.symbols import CONS_INT, CONS_OPT
from ..types.symbols.tokens import T_ADD, T_MUL

from .memory import Memory

class SatCompiler:
	"""
	"""
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
		if parser is None:
			self.parser = SatParser()
		elif type(parser) is not SatParser:
			raise TypeError("`parser` must be of type `SatParser`.")
		else:
			self.parser = parser

		## Memory
		self.memory = Memory()

		## Environment
		self.env = {}

		## Results
		self.results = None

		## Exit code
		self.code = 1

		## Errors
		self.error_stack = Stack()

	def __lshift__(self, error: SatError):
		self.error_stack.push(error)

	def __getitem__(self, level: int):
		""" Optimization Level
		"""
		return (self.O >= level)

	def __lt__(self, warning: SatWarning):
		stdwar << warning
		
	def compile(self, source: Source):
		"""
		"""
		try:
			self.code = 0
			self.results = self._compile(source)
		except SatExit as error:
			self.code = error.code
			self.results = None
		except Exception:
			trace = traceback.format_exc()
			with open('sat.log', 'w') as file:
				file.write(trace)
			stderr[3] << trace
			self.code = 1
			self.results = None
			raise
		finally:
			if self.code:
				stderr << f"> compiler exited with code {self.code}."
			else:
				stdout << f"> compiler exited with code {self.code}."
			return self.code

	def _compile(self, source: Source):
		"""
		"""
		## Input
		self.source = source

		## Parse code into bytecode
		## Adds special instructions RUN_INIT, RUN_SCRIPT in both ends
		self.bytecode = [(RUN_INIT,), *self.parser.parse(self.source), (RUN_SCRIPT,)]

		for stmt in self.bytecode:
			stdout[3] << f"{join(', ', stmt, repr)}"
			self.exec(stmt)
		else:
			stdout[3] << ""

		self.checkpoint()

		return {}

	def exit(self, code: int):
		raise SatExit(code)

	def exec(self, stmt: tuple):
		name, *args = stmt
		return self.instructions[name](self, *args)

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

	def eval(self, item: SatType):
		if type(item) is Var:
			## Get value from memory
			value = self.memget(item)

			## Copy error tracking information
			value.lexinfo = item.lexinfo
			
			return value

		elif type(item) is Expr:				
			## Return own expression
			return item

		elif not issubclass(type(item), SatType):
			raise TypeError(f'{type(item)} is not a valid Satyrus type for evaluation.')

		else:
			return item

	def eval_expr(self, expr: Expr, calc=False):
		"""
		"""
		return Expr.back_apply(expr, (lambda item: (Expr.calc(item) if calc else item) if (type(item) is Expr) else self.eval(item)))
	
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