""" :: DEF_CONSTRAINT ::
	====================

	STATUS: COMPLETE
"""
## Standard Library
import itertools as it
from functools import reduce

## Local
from ....satlib import arange, Stack, stdout, stdwar, stderr, join
from ..compiler import SatCompiler
from ...types.indexer import SatIndexer
from ...types.mapping import SatMapping
from ...types.error import SatValueError, SatTypeError, SatReferenceError, SatExprError, SatWarning
from ...types.symbols.tokens import T_EXISTS, T_EXISTS_ONE, T_FORALL, T_IDX
from ...types.symbols import CONS_INT, CONS_OPT, INDEXER
from ...types import Expr, Var, String, Number, Array, Constraint	

LOOP_TYPES = {T_EXISTS, T_EXISTS_ONE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}

def def_constraint(compiler: SatCompiler, cons_type: String, name: Var, loops: list, expr: Expr, level: Number):
	""" DEF_CONSTRAINT
		==============
	"""
	## Report process start
	stdout[5] << f"Started `{name}` ({cons_type}) constraint definition."

	## Check constraint type and level
	def_constraint_type_level(compiler, cons_type, level)

	## Create constraint object
	constraint: Constraint = Constraint(name, cons_type, level)

	## Retrieve clauses
	def_constraint_clauses(compiler, cons_type, loops, expr, constraint)

	## Register Constraint
	def_constraint_register(compiler, constraint)

def def_constraint_type_level(compiler: SatCompiler, cons_type: String, level: Number):
	"""
	"""
	
	if str(cons_type) not in CONST_TYPES:
		compiler << SatTypeError(f"Invalid constraint type {cons_type}. Options are: `int`, `opt`.", target=cons_type)

	if str(cons_type) == CONS_OPT and level is not None:
		compiler << SatTypeError("Invalid penalty level for optimality constraint.", target=level)

	if str(cons_type) == CONS_INT and (level < 0 or not level.is_int):
		compiler << SatValueError(f"Invalid penalty level {level}. Must be positive integer.", target=level)

	compiler.checkpoint()

def def_constraint_clauses(compiler: SatCompiler, cons_type: str, loops: list, raw_expr: Expr, constraint: Constraint):
	"""
	"""
	## Holds loop variables
	variables = set()

	## Retrieve Indexer Type
	Indexer = compiler.env[INDEXER]

	## Indexer
	indexer: SatIndexer = None

	# extract loop properties
	for (l_type, l_var, l_bounds, l_conds) in loops:

		# Check for earlier variable definitions
		if l_var in variables:
			compiler << SatExprError(f"Loop variable `{l_var}` repetition.", target=l_var)
		elif l_var in compiler:
			compiler < SatWarning(f"Variable `{l_var}` redefinition. Global values are set into the expression before loop variables.", target=l_var)

		## account for variable in loop scope
		variables.add(l_var)

		compiler.checkpoint()

		## check for boundary consistency
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

		## Run through all indices
		indices = [i for i in arange(start, stop, step)]

		## define condition
		if l_conds is not None:
			## Compile condition expressions
			cond = reduce(lambda x, y: x & y, [compiler.evaluate(c, miss=False, calc=True) for c in l_conds], Number.T)
		else:
			cond = None

		## Initialize Indexer for this loop
		if indexer is None:
			indexer: SatIndexer = Indexer(compiler, l_type, l_var, indices, cond)
		else:
			indexer: SatIndexer = indexer << Indexer(compiler, l_type, l_var, indices, cond)

		compiler.checkpoint()

	## Reduces expression to simplest form
	expr = Expr.calculate(raw_expr)

	stdwar << repr(expr)

	# pylint: disable=no-member
	if str(cons_type) == CONS_INT and not Expr.logical(expr):
		compiler << SatExprError("Integrity constraint expressions must be purely logical i.e. no arithmetic operations allowed.", target=raw_expr)

	compiler.checkpoint()

	## Checks for undefined variables + evaluate constants

	## Adds inner scope where inside-loop variables
	## point to themselves. This prevents both older
	## variables from interfering in evaluation and
	## also undefined loop variables.
	## Last but not least, automatically removes this
	## artificial scope.
	expr = compiler.evaluate(expr, miss=True, calc=True, null=False, context={var: var for var in variables})

	## Sets expression for this constraint in the Conjunctive Normal Form (C.N.F.)
	if str(cons_type) == CONS_INT:
		## Negate inner expression
		dnf_expr: Expr = Expr.dnf(~expr)
		## Invert Indexing Loops
		~indexer #pylint: disable=invalid-unary-operand-type
	elif str(cons_type) == CONS_OPT:
		dnf_expr: Expr = Expr.dnf(expr)
	else:
		raise NotImplementedError('There are no extra constraint types yet, just `int` or `opt`.')

	stdwar << repr(dnf_expr)

	compiler.checkpoint()

	## Simplify another time
	dnf_expr: Expr = Expr.calculate(dnf_expr)

	if indexer.in_dnf:
		stdwar << repr(dnf_expr)
		dnf_expr: Expr = indexer(dnf_expr)
	else:
		compiler < SatWarning(f'In Constraint `{constraint.name}` the expression indexed by `{indexer} {dnf_expr}` is not in the C.N.F.\nThis will require (probably many) extra steps to evaluate.\nThus, you may press Ctrl+X/Ctrl+C to interrupt compilation.', target=constraint.var)
		dnf_expr: Expr = indexer(dnf_expr, ensure_dnf=True)
	
	compiler.checkpoint()

	## One last time after indexing
	dnf_expr: Expr = Expr.calculate(dnf_expr)
	
	constraint.set_expr(dnf_expr)

	compiler.checkpoint()

def def_constraint_register(compiler: SatCompiler, constraint: Constraint):
	"""
	"""
	if constraint.name in compiler:
		compiler < SatWarning(f"Variable redefinition in constraint `{constraint.name}`.", target=constraint.name)
	
	compiler.memset(constraint.name, constraint)