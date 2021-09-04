""" :: DEF_CONSTRAINT ::
    ====================

    STATUS: INCOMPLETE
"""
## Standard Library
import itertools as it
from functools import reduce

## Third-Party
from cstream import stdlog, stdout, stdwar, stderr

## Local
from ..compiler import SatCompiler
from ...satlib import arange, Stack, Queue
from ...error import (
    SatValueError,
    SatTypeError,
    SatReferenceError,
    SatExprError,
    SatWarning,
)
from ...symbols import (
    CONS_INT,
    CONS_OPT,
    T_EXISTS,
    T_UNIQUE,
    T_FORALL,
    T_IDX,
    T_AND,
    T_NOT,
    T_NE,
)
from ...types import Expr, Var, String, Number, Array

LOOP_TYPES = {T_EXISTS, T_UNIQUE, T_FORALL}
CONST_TYPES = {CONS_INT, CONS_OPT}


def def_constraint(
    compiler: SatCompiler,
    cons_type: String,
    name: Var,
    loops: list,
    expr: Expr,
    level: Number,
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
    level : Number, Var
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
    while stack:
        # Retrieve loop from stack
        loop: Loop = stack.pop()

        if loop.type in {T_EXISTS, T_FORALL}:
            queue.push(loop)
        elif loop.type in {T_UNIQUE}:
            queue.push(Loop())
        else:
            raise ValueError(f"Invalid Loop type {loop.type}")
    else:
        compiler.checkpoint()

    ## Create constraint object
    constraint = Constraint(name, cons_type, level)

    ## Setup Indexer
    indexer = SatIndexer(compiler, list(queue), Expr.dnf(expr))

    ## Sets expression for this constraint in the Conjunctive Normal Form (C.N.F.)
    if str(cons_type) == CONS_INT:
        indexer.negate()
    elif str(cons_type) == CONS_OPT:
        pass
    else:
        raise NotImplementedError(
            f"There are no extra constraint types yet, just 'int' or 'opt', not '{cons_type}'."
        )

    compiler.checkpoint()

    if not indexer.in_dnf:
        compiler < SatWarning(
            f"In Constraint `{constraint.name}` the expression indexed by '{indexer}' is not in the C.N.F.\nThis will require (probably many) extra steps to evaluate.\nThus, you may press Ctrl+X/Ctrl+C to interrupt compilation.",
            target=constraint.var,
        )

    # Retrieve Indexed expression
    expr: Expr = indexer.index(ensure_dnf=True)

    compiler.checkpoint()

    ## One last time after indexing
    expr: Expr = Expr.calculate(expr)

    compiler.checkpoint()

    ## Register Constraint
    if constraint.name in compiler:
        compiler < SatWarning(
            f"Variable redefinition in constraint '{constraint.name}'.",
            target=constraint.name,
        )

    ## Endpoint
    compiler.memset(constraint.name, constraint)

    compiler.checkpoint()
