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

    # Holds loop variables
    variables = set()

    def_constraint_stack(compiler, cons_type, name, loops, level, stack, variables)

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

    ## Print Loop Stack
    if stdlog[3]:
        stdlog[3] << stack

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
    # Loop Queue
    queue = Queue()

    while stack:
        # Retrieve loop from stack
        loop: Loop = stack.pop()

        if loop.type in {T_EXISTS, T_FORALL}:
            pass
        elif loop.type in {T_UNIQUE}:
            loop.type = T_FORALL
            def_constraint_wta_fork(
                compiler, name, cons_type, level, stack, queue, expr, loop
            )
        else:
            raise ValueError(f"Invalid Loop type {loop.type}")
        queue.push(loop)
    else:
        compiler.checkpoint()

    ## Create constraint object
    constraint = Constraint(name, cons_type, level)

    ## Setup Indexer
    indexer = SatIndexer(compiler, list(queue), Expr.dnf(expr))

    ## Sets expression for this constraint in the Conjunctive Normal Form (C.N.F.)
    if str(cons_type) == CONS_INT:
        indexer.negate()
        if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(D.N.F. + Negation):\n\t{indexer.expr}"
    elif str(cons_type) == CONS_OPT:
        if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(D.N.F.):\n\t{indexer.expr}"
    else:
        raise NotImplementedError(f"There are no extra constraint types yet, just 'int' or 'opt', not '{cons_type}'.")

    compiler.checkpoint()

    if not indexer.in_dnf:
        compiler < SatWarning(f'In Constraint `{constraint.name}` the expression indexed by `{indexer} {indexer.expr}` is not in the C.N.F.\nThis will require (probably many) extra steps to evaluate.\nThus, you may press Ctrl+X/Ctrl+C to interrupt compilation.', target=constraint.var)

    # Retrieve Indexed expression
    expr: Expr = indexer.index(ensure_dnf=True)

    compiler.checkpoint()

    ## Verbose
    if stdlog[3]: stdlog[3] << f"\n@{constraint.name}(indexed):\n\t{expr}"

    ## One last time after indexing
    expr: Expr = Expr.calculate(expr)

    compiler.checkpoint()
    
    constraint.set_expr(expr)

    if stdlog[2]: stdlog[2] << f"\n@{constraint.name}(final):\n\t{expr}"

    compiler.checkpoint()

    ## Register Constraint
    if constraint.name in compiler:
        compiler < SatWarning(f"Variable redefinition in constraint '{constraint.name}'.", target=constraint.name)
    
    compiler.memset(constraint.name, constraint)

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
    wta_stack = stack.copy()
    wta_queue = queue.copy()

    wta_var = f"{T_IJK}{loop.var}"
    wta_cond = (
        Expr(T_NE, loop.var, wta_var)
        if loop.cond is None
        else Expr(T_AND, Expr(T_NE, loop.var, wta_var), loop.cond)
    )
    wta_loop = Loop(type=T_FORALL, var=wta_var, bounds=loop.bounds, cond=wta_cond)
    wta_expr = Expr(T_NOT, Expr(T_AND, expr, Expr.sub(expr, loop.var, wta_var)))

    wta_queue.push(wta_loop)
    wta_queue.push(loop)

    wta_name = Var(f"{name}-wta")
    wta_level = level + 1

    def_constraint_build(
        compiler, wta_name, cons_type, wta_level, wta_stack, wta_queue, wta_expr
    )
