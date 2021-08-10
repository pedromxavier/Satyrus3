""" :: DEF_CONSTRAINT ::
    ====================

    STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it
from functools import reduce
from dataclasses import dataclass

## Third-Party
from cstream import stdlog, stdout, stdwar, stderr

## Local
from ..compiler import SatCompiler
from ..components.components import Loop
from ..components.indexer import SatIndexer
from ..components.mapping import SatMapping
from ...satlib import arange, Stack, Queue, join, track
from ...types.error import (
    SatValueError,
    SatTypeError,
    SatReferenceError,
    SatExprError,
    SatWarning,
)
from ...types.symbols.tokens import (
    T_EXISTS,
    T_UNIQUE,
    T_FORALL,
    T_IDX,
    T_IJK,
    T_AND,
    T_NOT,
    T_NE,
)
from ...types.symbols import CONS_INT, CONS_OPT, INDEXER
from ...types import Expr, Var, String, Number, Array, Constraint

LOOP_TYPES = {T_EXISTS, T_UNIQUE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}

def def_constraint(
    compiler: SatCompiler,
    cons_type: String,
    name: Var,
    loops: list,
    expr: Expr,
    level: {Number, Var},
):
    """
    Parameters
    ----------
    compiler : SatCompiler
            Current running compiler instance.
    cons_type : String
            Either 'opt' or 'int'.
    name : Var
            Constraint identifier.
    loops : list
            Nested replication loops.
    expr : Expr
            Inner constraint expression.
    level : {Number, Var}
            Constraint's penalty level.
    """
    if type(level) is not Number:
        level = compiler.evaluate(level, miss=True, calc=True, null=True)

    ## Check constraint type and level
    if str(cons_type) not in CONST_TYPES:
        compiler << SatTypeError(
            f"Invalid constraint type {cons_type}. Options are: `int`, `opt`.",
            target=cons_type,
        )

    if str(cons_type) == CONS_OPT and level is not None:
        compiler << SatTypeError(
            "Invalid penalty level for optimality constraint.", target=level
        )

    if str(cons_type) == CONS_INT and (level < 0 or not level.is_int):
        compiler << SatValueError(
            f"Invalid penalty level {level}. Must be positive integer.", target=level
        )

    compiler.checkpoint()

    # Loop Stack
    # At each level we have:
    # Loop(type, var, indices, conds)
    stack = Stack()

    # Loop Queue
    queue = Queue()

    # Holds loop variables
    variables = set()

    def_constraint_stack(compiler, cons_type, name, loops, level, stack, variables)

    compiler.checkpoint()

    ## Begin expr analysis
    if stdlog[3]:
        stdlog[3] << f"\n@{name}(raw):\n\t{expr}"

    ## Simplify
    expr = track(expr, Expr.calculate(expr), out=True)

    if stdlog[3]:
        stdlog[3] << f"\n@{name}(simplified):\n\t{expr}"

    if str(cons_type) == CONS_INT and not expr.logical:
        compiler << SatExprError(
            "Integrity constraint expressions must be purely logical i.e. no arithmetic operations allowed.",
            target=expr,
        )

    compiler.checkpoint()

    # Checks for undefined variables + evaluate constants
    # Adds inner scope where inside-loop variables point to themselves. This prevents both
    # older variables from interfering in evaluation and also undefined loop variables.
    # Last but not least, automatically removes this artificial scope.
    expr: Expr = track(
        expr,
        compiler.evaluate(
            expr,
            miss=True,
            calc=True,
            null=False,
            context={var: var for var in variables},
        ),
        out=True,
    )

    compiler.checkpoint()

    def_constraint_build(compiler, name, cons_type, level, stack, queue, expr)

def def_constraint_stack(
    compiler: SatCompiler,
    cons_type: String,
    name: Var,
    loops: list,
    level: {Number, Var},
    stack: Stack,
    variables: set,
) -> Stack:
    """
    Parameters
    ----------
    compiler : SatCompiler
        Satyrus Compiler instance.
    cons_type : String
        Constraint type: either 'int' or 'opt'.
    name : Var
        Constraint name.
    loops : list
        Nested repetition loop stack.
    level : Number, Var
        Constraint Penalty level.
    """
    # extract loop properties
    for (l_type, l_var, l_bounds, l_conds) in loops:

        # Check for earlier variable definitions
        if l_var in variables:
            compiler << SatExprError(
                f"Loop variable '{l_var}' repetition.", target=l_var
            )
        elif l_var in compiler:
            compiler < SatWarning(
                f"Variable '{l_var}' redefinition. Global values are set into the expression before loop variables.",
                target=l_var,
            )

        # account for variable in loop scope
        variables.add(l_var)

        compiler.checkpoint()

        # check for boundary consistency
        # extract loop boundaries
        start, stop, step = l_bounds

        # evaluate variables
        start = compiler.evaluate(start, miss=True, calc=True)
        stop = compiler.evaluate(stop, miss=True, calc=True)
        step = compiler.evaluate(
            step, miss=True, calc=True, null=True
        )  ## accepts null (None) as possible value

        if step is None:
            if start <= stop:
                step = Number("1")
            else:
                step = Number("-1")

        elif step == Number("0"):
            compiler << SatValueError("Step must be non-zero.", target=step)

        if ((start < stop) and (step < 0)) or ((start > stop) and (step > 0)):
            compiler << SatValueError("Inconsistent loop definition", target=start)

        compiler.checkpoint()

        # define condition
        if l_conds is not None:
            # Compile condition expressions
            cond = reduce(
                lambda x, y: x._AND_(y),
                [compiler.evaluate(c, miss=False, calc=True) for c in l_conds],
                Number.T,
            )
        else:
            cond = None

        stack.push(Loop(type=l_type, var=l_var, bounds=(start, stop, step), cond=cond))

    compiler.checkpoint()

def def_constraint_build(
    compiler: SatCompiler,
    name: Var,
    cons_type: String,
    level: Number,
    stack: Stack,
    queue: Queue,
    expr: Expr,
) -> None:
    """"""
    stdlog[3] << f"\nBUILD CONSTRAINT ({cons_type}) {name} [{level}]:"
    stdlog[3] << f"STACK:\n{stack}"
    stdlog[3] << f"QUEUE:\n{queue}"
    stdlog[3] << f"EXPR: {expr}"

    while stack:
        # Retrieve loop from stack
        loop: Loop = stack.pop()

        if loop.type in {T_EXISTS, T_FORALL}:
            queue.push(loop)
        elif loop.type in {T_UNIQUE}:
            def_constraint_wta_fork(
                compiler=compiler,
                name=name,
                cons_type=cons_type,
                level=level,
                stack=stack.copy(),
                queue=queue.copy(),
                loop=loop,
                expr=expr
            )
            queue.push(Loop())
        else:
            raise ValueError(f"Invalid Loop type {loop.type}")
    else:
        compiler.checkpoint()

    stdlog[3] << f"\nAFTER STACK PUSH ({cons_type}) {name} [{level}]:"
    stdlog[3] << f"STACK:\n{stack}"
    stdlog[3] << f"QUEUE:\n{queue}"
    stdlog[3] << f"EXPR: {expr}"

    ## Create constraint object
    constraint = Constraint(name, cons_type, level)

    ## Setup Indexer
    indexer = SatIndexer(compiler, list(queue), Expr.dnf(expr))

    ## Sets expression for this constraint in the Conjunctive Normal Form (C.N.F.)
    if str(cons_type) == CONS_INT:
        indexer.negate()
        if stdlog[3]:
            stdlog[3] << f"\n@{constraint.name}(D.N.F. + Negation):\n\t{indexer.expr}"
            stdlog[3] << f"\n@{constraint.name}(Loop Stack):"
            stdlog[3] << '\n'.join(map(str, indexer.loops))
    elif str(cons_type) == CONS_OPT:
        if stdlog[3]:
            stdlog[3] << f"\n@{constraint.name}(D.N.F.):\n\t{indexer.expr}"
            stdlog[3] << f"\n@{constraint.name}(Loop Stack):"
            stdlog[3] << '\n'.join(map(str, indexer.loops))
    else:
        raise NotImplementedError(f"There are no extra constraint types yet, just 'int' or 'opt', not '{cons_type}'.")

    compiler.checkpoint()

    if not indexer.in_dnf:
        compiler < SatWarning(f"In Constraint `{constraint.name}` the expression indexed by '{indexer}' is not in the C.N.F.\nThis will require (probably many) extra steps to evaluate.\nThus, you may press Ctrl+X/Ctrl+C to interrupt compilation.", target=constraint.var)

    # Retrieve Indexed expression
    expr: Expr = indexer.index(ensure_dnf=True)

    compiler.checkpoint()

    ## Verbose
    # if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(indexed):\n\t{expr}"

    ## One last time after indexing
    expr: Expr = Expr.calculate(expr)

    compiler.checkpoint()
    
    constraint.set_expr(expr)

    # if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(final):\n\t{expr}"

    compiler.checkpoint()

    ## Register Constraint
    if constraint.name in compiler:
        compiler < SatWarning(f"Variable redefinition in constraint '{constraint.name}'.", target=constraint.name)
    
    ## Endpoint
    compiler.memset(constraint.name, constraint)

    compiler.checkpoint()

def def_constraint_wta_fork(
    compiler: SatCompiler,
    name: Var,
    cons_type: String,
    level: Number,
    stack: Stack,
    queue: Queue,
    loop: Loop,
    expr: Expr,
) -> None:
    """"""

    wta_name = Var(f"{name}-wta")
    wta_level = level + 1
    wta_bounds = tuple(loop.bounds)

    wta_ivar = Var(f"{loop.var}")
    wta_icond = loop.cond
    wta_iloop = Loop(type=T_FORALL, var=wta_ivar, bounds=wta_bounds, cond=wta_icond)

    wta_jvar = Var(f"{loop.var}{T_IJK}")
    if loop.cond is None:
        wta_jcond = Expr(T_NE, wta_ivar, wta_jvar)
    else:
        wta_jcond = Expr(T_AND, Expr(T_NE, wta_ivar, wta_jvar), loop.cond)
    wta_jloop = Loop(type=T_FORALL, var=wta_jvar, bounds=wta_bounds, cond=wta_jcond)

    wta_stack = stack
    wta_queue = queue

    wta_expr = Expr(T_NOT, Expr(T_AND, expr, Expr.sub(expr, wta_ivar, wta_jvar)))

    wta_queue.push(wta_iloop)
    wta_queue.push(wta_jloop)

    def_constraint_build(compiler, wta_name, cons_type, wta_level, wta_stack, wta_queue, wta_expr)
