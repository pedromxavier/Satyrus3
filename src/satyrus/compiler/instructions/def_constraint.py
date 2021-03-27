""" :: DEF_CONSTRAINT ::
	====================

	STATUS: COMPLETE
"""
## Standard Library
import itertools as it
from functools import reduce
from dataclasses import dataclass

## Local
from ..compiler import SatCompiler
from ...satlib import arange, Stack, stdlog, stdout, stdwar, stderr, join, track
from ...types.indexer import SatIndexer
from ...types.mapping import SatMapping
from ...types.error import SatValueError, SatTypeError, SatReferenceError, SatExprError, SatWarning
from ...types.symbols.tokens import T_EXISTS, T_UNIQUE, T_FORALL, T_IDX, T_IJK
from ...types.symbols import CONS_INT, CONS_OPT, INDEXER
from ...types import Expr, Var, String, Number, Array, Constraint	

LOOP_TYPES = {T_EXISTS, T_UNIQUE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}

@dataclass
class Loop:
	type: String
	var: Var
	bounds: tuple
	cond: Expr

	def __iter__(self):
		return iter([self.type, self.var, self.bounds, self.cond])

	def __str__(self):
		start, stop, step = self.bounds
		return f"{self.type} {self.var} [{start}:{stop}:{step}] ? {'Ø' if self.cond is None else self.cond}"

def def_constraint(compiler: SatCompiler, cons_type: String, name: Var, loops: list, expr: Expr, level: {Number, Var}):
	"""
	"""
	if type(level) is not Number:
		level = compiler.evaluate(level, miss=True, calc=True, null=True)

	## Check constraint type and level
	if str(cons_type) not in CONST_TYPES:
		compiler << SatTypeError(f"Invalid constraint type {cons_type}. Options are: `int`, `opt`.", target=cons_type)

	if str(cons_type) == CONS_OPT and level is not None:
		compiler << SatTypeError("Invalid penalty level for optimality constraint.", target=level)

	if str(cons_type) == CONS_INT and (level < 0 or not level.is_int):
		compiler << SatValueError(f"Invalid penalty level {level}. Must be positive integer.", target=level)

	compiler.checkpoint()

	## Create constraint object
	constraint = Constraint(name, cons_type, level)

	## Retrieve Indexer Type
	Indexer = compiler.env[INDEXER]

	# Holds loop variables
	variables = set()

	# Loop Stack
	# At each level we have:
	# Loop(type, var, indices, conds)
	stack_A = Stack()
	stack_B = Stack()

	# extract loop properties
	for (l_type, l_var, l_bounds, l_conds) in loops:

		# Check for earlier variable definitions
		if l_var in variables:
			compiler << SatExprError(f"Loop variable `{l_var}` repetition.", target=l_var)
		elif l_var in compiler:
			compiler < SatWarning(f"Variable `{l_var}` redefinition. Global values are set into the expression before loop variables.", target=l_var)

		# account for variable in loop scope
		variables.add(l_var)

		compiler.checkpoint()

		# check for boundary consistency
		# extract loop boundaries
		start, stop, step = l_bounds

		# evaluate variables
		start = compiler.evaluate(start, miss=True, calc=True)
		stop = compiler.evaluate(stop, miss=True, calc=True)
		step = compiler.evaluate(step, miss=True, calc=True, null=True) ## accepts null (None) as possible value

		if step is None:
			if start <= stop:
				step = Number('1')
			else:
				step = Number('-1')

		elif step == Number('0'):
			compiler << SatValueError('Step must be non-zero.', target=step)

		if ((start < stop) and (step < 0)) or ((start > stop) and (step > 0)):
			compiler << SatValueError('Inconsistent loop definition', target=start)
		
		compiler.checkpoint()

		# define condition
		if l_conds is not None:
			# Compile condition expressions
			cond = reduce(lambda x, y: x._AND_(y), [compiler.evaluate(c, miss=False, calc=True) for c in l_conds], Number.T)
		else:
			cond = None

		stack_A.push(Loop(type=l_type, var=l_var, bounds=(start, stop, step), cond=cond))

	## Print Loop Stack
	if stdlog[3]: stdlog[3] << stack_A

	compiler.checkpoint()

	## Begin expr analysis
	if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(raw):\n\t{expr}"

	## Simplify
	expr = track(expr, Expr.calculate(expr), out=True)

	if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(simplified):\n\t{expr}"

	if str(cons_type) == CONS_INT and not expr.logical:
		compiler << SatExprError("Integrity constraint expressions must be purely logical i.e. no arithmetic operations allowed.", target=expr)

	compiler.checkpoint()

	# Checks for undefined variables + evaluate constants
	# Adds inner scope where inside-loop variables point to themselves. This prevents both
	# older variables from interfering in evaluation and also undefined loop variables.
	# Last but not least, automatically removes this artificial scope.
	expr: Expr = track(expr, compiler.evaluate(expr, miss=True, calc=True, null=False, context={var: var for var in variables}), out=True)

	while stack_A:
		loop: Loop = stack_A.pop()

		if loop.type in {T_EXISTS, T_FORALL}:
			stack_B.push(loop)
		elif loop.type in {T_UNIQUE}:
			fork_wta(compiler, constraint, loop, stack_A, stack_B, expr)
		else:
			raise ValueError(f"Invalid Loop type {loop.type}")

	compiler.checkpoint()

	indexer: Indexer = Indexer(stack_B, expr)

	"""
	## Sets expression for this constraint in the Conjunctive Normal Form (C.N.F.)
	if str(cons_type) == CONS_INT:
		## Negate inner expression
		dnf_expr: Expr = Expr.dnf(~expr)
		## Invert Indexing Loops
		~indexer #pylint: disable=invalid-unary-operand-type
		## Verbose
		if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(D.N.F. + Negation):\n\t{dnf_expr}"
	elif str(cons_type) == CONS_OPT:
		dnf_expr: Expr = Expr.dnf(expr)
		## Verbose
		if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(D.N.F.):\n\t{dnf_expr}"
	else:
		raise NotImplementedError('There are no extra constraint types yet, just `int` or `opt`.')

	## Simplify another time
	dnf_expr: Expr = Expr.calculate(dnf_expr)

	## Verbose
	if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(D.N.F. + Simplify):\n\t{dnf_expr}"

	compiler.checkpoint()

	if indexer.in_dnf:
		idx_expr: Expr = indexer(dnf_expr)
	else:
		compiler < SatWarning(f'In Constraint `{constraint.name}` the expression indexed by `{indexer} {dnf_expr}` is not in the C.N.F.\nThis will require (probably many) extra steps to evaluate.\nThus, you may press Ctrl+X/Ctrl+C to interrupt compilation.', target=constraint.var)
		idx_expr: Expr = indexer(dnf_expr, ensure_dnf=True)

	compiler.checkpoint()

	## Verbose
	if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(indexed):\n\t{idx_expr}"

	## One last time after indexing
	final_expr: Expr = Expr.calculate(idx_expr)

	compiler.checkpoint()
	
	constraint.set_expr(final_expr)

	if stdlog[2]: stdlog[2] << f"\n@{constraint.name}(final):\n\t{final_expr}"

	compiler.checkpoint()

	## Register Constraint
	if constraint.name in compiler:
		compiler < SatWarning(f"Variable redefinition in constraint `{constraint.name}`.", target=constraint.name)
	
	compiler.memset(constraint.name, constraint)
	"""

def fork_wta(compiler: SatCompiler, constraint: Constraint, loop: Loop, stack_a: Stack, stack_b: Stack, expr: Expr):
	"""
	"""
	wta_var = Var(f"{T_IJK}{loop.var}")
	wta_name = Var(f"{constraint.name}_wta")
	wta_expr = ~(expr & Expr.sub(expr, loop.var, wta_var))
	wta_cond = None if loop.cond is None else Expr.sub(loop, loop.var, wta_var)
	wta_loop = Loop(T_FORALL, loop.var, loop.bounds, wta_cond)
	wta_loops = [*stack_a, loop, wta_loop, *reversed(stack_b)]
	wta_level = Number(constraint.level) + Number('1')

	def_constraint(compiler, constraint.type, wta_name, wta_loops, wta_expr, wta_level)
