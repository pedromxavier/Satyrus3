""" :: Sat Compiler ::
	==================
"""
## Standard Library
import traceback
import os
import math

## Local
from ...satlib import log, system, stderr, stdlog, stdout, stdwar, Source, Stack, join
from ...satlib import track as sat_track
from ..parser import SatParser
from ..parser.legacy import SatLegacyParser
from ..types.error import SatValueError, SatTypeError, SatCompilerError, SatReferenceError
from ..types.error import SatError, SatExit, SatWarning
from ..types import Expr, SatType, String, Number, Var, Array
from ..types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA, OPT, RUN_INIT, RUN_SCRIPT
from ..types.symbols import CONS_INT, CONS_OPT
from ..types.symbols.tokens import T_ADD, T_MUL
from .memory import Memory

class SatCompiler:
	"""
	"""
	def __init__(self, instructions: dict, parser : SatParser = None, env: dict=None):
		"""
		Parameters
		----------
		instructions : dict
			Dictionary containing the compiler's instruction set. Matches string command identifiers with respective functions.
		parser : SatParser
			Allows for chosing alternative parsers for a given compiler. Main uses are for parsing multiple versions of an evolving language.
		env : dict
			Initial compiler environment configuration.
		"""
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
		elif type(parser) is not SatParser and type(parser) is not SatLegacyParser:
			raise TypeError(f"`parser` must be of type `SatParser` or `SatLegacyParser, not {type(parser)}`.")
		else:
			self.parser = parser

		## Memory
		self.memory = Memory()

		## Compiler Environment
		if env is None:
			self.env = {}
		else:
			self.env = dict(env)

		## Results
		self.results = None

		## Exit code
		self.code = 1

		## Errors
		self.error_stack = Stack()

	def __enter__(self, *args, **kwargs):
		## Instantiate subcompiler
		subcomp = self.__class__(self.instructions, self.parser)
		subcomp.memory = self.memory.copy
		subcomp.env = self.env.copy()
		return subcomp

	def __exit__(self, *args, **kwargs):
		return None

	def __lshift__(self, error: SatError) -> None:
		""" Pushes error into compiler stack.

		Parameters
		----------
		error: SatError
			Error to be raised in the next `compiler.checkpoint()` call.
		"""
		self.error_stack.push(error)

	def __lt__(self, warning: SatWarning) -> None:
		""" Prints Warning to stdout.

		Parameters
		----------
		warning: SatWarning
		"""
		stdwar[1] << warning

	def __getitem__(self, opt_level: int) -> bool:
		""" Optimization Level check.

		Parameters
		----------
		opt_level: int
			Desired optimization level.

		Returns
		-------
		bool
			Equivalent to (compiler.opt >= opt_level)

		Example
		-------
		This requires optimization level to be at least `n` to execute block.
		>>> if compiler[n]:
				block
		"""
		return (self.env[OPT] >= opt_level)

	def __call__(self, results: object):
		self.results = results

	def compile(self, source: Source) -> int:
		"""
		Parameters
		----------
		source: Source
			String-like object created from `.sat` source-code file.

		Returns
		-------
		int
			Compiler exit code.
		"""
		try:
			self.code = 0
			self._compile(source)
			return self.code
		except SatExit as error:
			self.code = error.code
			self.results = None
			return self.code
		except SatError as error:
			stderr[0] << error
			self.code = error.code
			self.results = None
			return self.code
		except Exception as error:
			self.code = 1
			self.results = None
			raise error
		else:
			return self.code

	def _compile(self, source: Source):
		"""Parses source into bytecode and then executes it sequentially.

		Parameters
		----------
		source: Source
			String-like object created from `.sat` source-code file.
		"""
		## Input
		self.source = source

		## Parse code into bytecode
		## Adds special instructions RUN_INIT, RUN_SCRIPT in both ends
		self.bytecode = [(RUN_INIT,), *self.parser.parse(self.source), (RUN_SCRIPT,)]

		for stmt in self.bytecode:
			stdlog[3] << join('\n\t', [f"\nCMD {stmt[0]}", *(f"{i} {x}" for i, x in enumerate(stmt[1:]))])
			self.exec(stmt)
		else:
			stdlog[3] << ""

		self.checkpoint()

	def exit(self, code: int):
		"""
		Parameters
		----------
		code: int
			Compiler exit code.
		"""
		raise SatExit(code)

	def exec(self, stmt: tuple):
		name, *args = stmt
		return self.instructions[name](self, *args)

	def __contains__(self, item: Var):
		""" 
		"""
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

		Returns
		-------
		SatType
			Internal Satyrus Object retrieved from compiler memory.
		"""
		try:
			return self.memory.memget(name)
		except SatReferenceError as error:
			self << error
		finally:
			self.checkpoint()

	def evaluate(self, item: SatType, miss: bool=True, calc: bool=True, null: bool=False, track: bool=False, context: dict=None) -> SatType:
		"""
		Parameters
		----------
		item : SatType
			Internal Satyrus object to be evaluated.
		miss : bool
			If True, raises SatReferenceError when undefined variable is found. Otherwise, returns the variable itself.
		calc : bool
			If True, applies Expr.calculate to expressions retrived by compiler evaluation.
		null : bool
			If True, allows Python null (None) to be bypassed during evaluation. Otherwise, raises (critical) ValueError.
		track : bool
			If True, attempts to propagate `lexinfo` into evaluation results.
		context : dict
			Temporary memory scope to be pushed into memory stack before evaluation and released just after.

		Example
		-------
		...
		>>> compiler = SatCompiler(*args, **kwargs)
		>>> n = Var('n')
		>>> compiler.memset(n, Number('0.5'))
		>>> compiler.evaluate(n)
		Number('0.5')
		>>> compiler.evaluate(Number('7.4'))
		Number('7.4')
		"""
		if context is not None:
			self.push(context)
			result = self._evaluate(item, miss, calc, null)
			self.pop()
		else:
			result = self._evaluate(item, miss, calc, null)

		if track: sat_track(item, result)

		return result

	def _evaluate(self, item: SatType, miss: bool=True, calc: bool=True, null: bool=False) -> SatType:
		"""
		"""
		if item is None:
			if null:
				return None
			else:
				raise ValueError("Invalid None appearance in compiler `evaluate`.")
		elif type(item) is Expr:
			if calc:
				return Expr.calculate(Expr(item.head, *(self._evaluate(p, miss, calc) for p in item.tail)))
			else:
				return Expr(item.head, *(self._evaluate(p, miss, calc) for p in item.tail))
		elif type(item) is Number:
			return item
		elif type(item) is Array:
			return item
		elif type(item) is Var:
			try:
				return self.memory.memget(item)
			except SatReferenceError as error:
				if miss:
					self << error
				else:
					return item
			finally:
				self.checkpoint()
		else:
			raise TypeError(f'Invalid Type `{type(item)}` for `{item!r}` in `compiler.evaluate`.')

	def push(self, scope: dict=None):
		"""Adds new scope to the top of the memory stack. Variable definition is done by `SatCompiler.memset` and will follow its rules for referencing.

		Parameters
		----------
		scope : dict, optional
			Mapping between variables and values.
		"""
		self.memory.push()
		
		if scope is not None:
			for k, v in scope.items():
				self.memset(k, v)

	def pop(self, depth: int=1):
		"""Removes a given number of layers from the memory stack. If removal goes beyond global scope, an exception is raised.

		Parameters
		----------
		depth: int, optional
			How many layers should be removed from the memory stack, defaults to a single one.
		"""
		self.memory.pop(depth)

	def interrupt(self):
		"""Interrupts compilation after outputing error messages to stderr.
		"""
		while self.error_stack:
			error = self.error_stack.popleft()
			stderr[0] << error
		else:
			self.exit(1)

	def checkpoint(self):
		"""If there is any unhandled exception in the compiler's error stack, interrupts compilation via a `SatCompiler.interrupt` call
		"""
		if self.status: self.interrupt()

	@property
	def status(self) -> bool:
		"""Evaluates to True if there is any unhandled exception in the compiler's error stack. Otherwise, returns False.

		Returns
		-------
		bool
		"""
		return bool(self.error_stack)