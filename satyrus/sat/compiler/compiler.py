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
from ..types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA
from ..types.symbols import CONS_INT, CONS_OPT
from ..types.symbols.tokens import T_ADD, T_MUL

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
		self.bytecode = self.parser.parse(self.source)

		## Set default environment variables
		self.env = self.DEFAULT_ENV.copy()

		## Error collector
		self.errors = []

		for stmt in self.bytecode:
			stdout[3] << f"{stmt[0]} {stmt[1]} {stmt[2]}"
			self.exec(stmt)
		else:
			stdout[3] << ""

		self.checkpoint()

		## Parameter capture
		if (self.env[EPSILON] < pow(10, -Number.prec(None))):
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
			CONS_INT: [cons for cons in constraints if (cons.type == CONS_INT)],
			CONS_OPT: [cons for cons in constraints if (cons.type == CONS_OPT)]
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
			if cons.level not in self.levels:
				self.levels[cons.level] = 1
			else:
				self.levels[cons.level] += 1
		else:
			self.levels = sorted(self.levels.items())

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

		stdout[2] << ':  Penalty Table  :'
		stdout[2] << '| lvl | n | value |'
		for k, n in self.levels:
			stdout[2] << f"|{k:4d} | {n:d} | {self.penalties[k]:5.2f} |"

		stdout[2] << f"| ε={epsilon:.2f} ; α={alpha:.2f} |"
		stdout[2] << ""

		self.checkpoint()

		## Generate Energy equations
		f_std = lambda expr: Expr.anf(Expr.calc(Expr.anf(Expr.calc(expr))))
		## Integrity Constraints
		stdout[3] << f"INT CONST"
		f_int = lambda expr: Expr.lms(Expr.dnf(~Expr.calc(expr)))
		E_int = []
		for cons in self.constraints[CONS_INT]:
			expr = self.penalties[cons.level] * f_int(cons.get_expr(self))
			stdout[3] << f"\t{expr!r}\n"
			E_int.append(f_std(expr))
		else:
			if len(E_int) == 1:
				E_int = E_int[0]
			else:
				E_int = Expr(T_ADD, *E_int)
		
		## Optimality ones
		stdout[3] << f"OPT CONST"
		f_opt = lambda expr: Expr.lms(Expr.dnf(Expr.calc(expr)))
		E_opt = []
		for cons in self.constraints[CONS_OPT]:
			expr = self.penalties[cons.level] * f_opt(cons.get_expr(self))
			stdout[3] << f"\t{expr!r}\n"
			E_opt.append(f_std(expr))
		else:
			if len(E_opt) == 1:
				E_opt = E_opt[0]
			else:
				E_opt = Expr(T_ADD, *E_opt)

		self.checkpoint()

		## Combining both
		E = E_int + E_opt

		self.checkpoint()

		E = f_std(E)

		self.checkpoint()

		table = Expr.sum_table(E)

		return {(tuple(k) if k is not None else None): table[k] for k in table}

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