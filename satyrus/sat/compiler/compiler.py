""" :: Sat Compiler ::
	==================

The SATyrus Compiler translates .sbc (SATyrus Bytecode) into
.sco (SATyrus compiled object), basically a Python dictionary
suitable for json serialization.
"""
## Standard Library
import os
import math

## Local
from satyrus.satlib import system, stderr, stdout, stdwar, Source, Stack

from ..parser import SatParser
from ..types.error import SatValueError, SatTypeError, SatCompilerError, SatReferenceError
from ..types.error import SatError, SatExit, SatWarning
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
		EPSILON : Number(0.1),
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
		if parser is None:
			self.parser = SatParser()
		elif type(parser) is not SatParser:
			raise TypeError("`parser` must be of type `SatParser`.")
		else:
			self.parser = parser

		## Memory
		self.memory = Memory()

		## Environment
		self.env = None

		## Exit code
		self.code = 0

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
			self._compile(source)
		except SatExit as error:
			self.code = error.code
		except Exception as error:
			stderr << error
		finally:
			return self.code

	def _compile(self, source: Source):
		"""
		"""
		## Input
		self.source = source

		## Parse code into bytecode
		self.bytecode = self.parser.parse(self.source)

		## Set default environment variables
		self.env = self.DEFAULT_ENV.copy()

		## Error collector
		self.errors = []

		for stmt in self.bytecode:
			self.exec(stmt)

		## Parameter capture
		if (self.env[EPSILON] < pow(10, -Number.prec())):
			self << SatValueError("Tiebraker `epsilon` is neglected due to numeric precision.", target=self.env[EPSILON])
		
		## Set numeric presision
		Number.prec(int(self.env[PREC]))

		## value for alpha
		alpha = Number(self.env[ALPHA])

		## value for epsilon
		epsilon = Number(self.env[EPSILON])

		self.checkpoint()

		## Constraint compilation
		constraints = [item for item in self.memory if (type(item) is Constraint)]

		self.constraints = {
			CONS_INT: [cons for cons in constraints if (cons.cons_type == CONS_INT)],
			CONS_OPT: [cons for cons in constraints if (cons.cons_type == CONS_OPT)]
		}

		if len(self.constraints[CONS_INT]) + len(self.constraints[CONS_OPT]) == 0:
			self << SatCompilerError("No problem defined. Maybe you are just fine.", target=self.source.eof)
		elif len(self.constraints[CONS_INT]) == 0:
			self << SatCompilerError("No Integrity condition defined.", target=self.source.eof)
		elif len(self.constraints[CONS_OPT]) == 0:
			self << SatCompilerError("No Optmization condition defined.", target=self.source.eof)

		self.checkpoint()

		## Penalties
		self.penalties = {
			0: alpha
		}

		self.levels = {
			0: len(self.constraints[CONS_OPT])
		}

		for cons in self.constraints[CONS_INT]:
			stdout[1] << f"({cons.cons_type}) {cons.name}:"
			stdout[1] << f"{cons.expr}"
			if cons.level not in self.levels:
				self.levels[cons.level] = 1
			else:
				self.levels[cons.level] += 1
		else:
			self.levels = sorted(self.levels.items())

		for cons in self.constraints[CONS_OPT]:
			stdout[1] << f"({cons.cons_type}) {cons.name}:"
			stdout[1] << f"{cons.expr}"

		## Compute penalty levels
		level_j, n_j = self.levels[0]
		for i in range(1, len(self.levels)):
			## level_k <- level_j & n_k <- n_j
			## level_j <- level_i & n_j <- n_i
			(level_k, n_k), (level_j, n_j) = (level_j, n_j), self.levels[i]
			
			if i == 1:
				self.penalties[level_j] = self.penalties[level_k] * n_k + epsilon
			else:
				self.penalties[level_j] = self.penalties[level_k] * (n_k + 1)

		stdout[1] << ':  Penalty Table  :'
		stdout[1] << '| lvl | n | value |'
		for k, n in self.levels:
			stdout[1] << f"|{k:4d} | {n:d} | {self.penalties[k]:5.2f} |"

		stdout[1] << f"| ε={epsilon:.2f} ; α={alpha:.2f} |"

		self.checkpoint()

		## Generate Energy equation

		## Integrity Constraints
		#E_int = [cons.lms for cons in self.constraints[CONS_INT]]
		
		## Optimality ones
		#E_opt = [cons.lms for cons in self.constraints[CONS_OPT]]

		self.checkpoint()
		
		if self.code:
			stderr[1] << f"> compiler exited with code {self.code}."
		else:
			stdout[1] << f"> compiler exited with code {self.code}."

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