"""
"""
# Future Imports
from __future__ import annotations

## Standard Library
import itertools as it
from functools import reduce
from typing import Callable

## Third-Party
from cstream import stdlog

## Local
from ..compiler import SatCompiler
from ...satlib import arange, Stack, Posiform
from ...error import (
    SatValueError,
    SatTypeError,
    SatExprError,
    SatWarning,
)
from ...symbols import CONS_INT, CONS_OPT, T_EXISTS, T_UNIQUE, T_FORALL, T_AND, T_OR, T_NOT, T_NE, T_ADD, T_MUL, T_XOR
from ...types import Expr, Var, String, Number, SatType

LOOP_TYPES = {T_EXISTS, T_UNIQUE, T_FORALL}
CONS_TYPES = {CONS_INT, CONS_OPT}


def def_constraint(
    compiler: SatCompiler,
    constype: String,
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
    constype : String
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

    # -*- Penalty Level -*-
    if level is None:
        pass
    elif isinstance(level, Number):
        pass
    elif isinstance(level, (Var, Expr)):
        level = compiler.evaluate(level, miss=True, calc=True, null=True)
    else:
        raise TypeError(f"'level' must be 'Number', 'Var' or 'Expr', not ({type(level)})")

    # -*- Constraint Type & Level Consistency Check -*-
    if str(constype) not in CONS_TYPES:
        compiler << SatTypeError(
            f"Invalid constraint type '{constype}'. Options are: {CONS_TYPES}",
            target=constype,
        )

    if str(constype) == CONS_OPT and level is not None:
        compiler << SatTypeError("Invalid penalty level for optimality constraint.", target=level)

    if str(constype) == CONS_INT and (level < 0 or not level.is_int):
        compiler << SatValueError(f"Penalty level must be a positive integer", target=level)

    compiler.checkpoint()

    # -*- Quantifier Replication Stack -*-
    stack = Stack()

    # -*- Variable Accountance -*-
    var_bag = set()

    # -*- Stacking Quantifiers -*-
    l_type: String
    l_var: Var
    l_bounds: tuple[Number, Number, Number]
    l_conds: list[Callable]

    for (l_type, l_var, l_bounds, l_conds) in loops:
        if l_var in var_bag:
            compiler << SatExprError(f"Loop variable '{l_var}' repetition.", target=l_var)
        elif l_var in compiler:
            compiler < SatWarning(
                f"Variable '{l_var}' redefinition. Global values are set into the expression before loop variables.",
                target=l_var,
            )

        compiler.checkpoint()

        var_bag.add(l_var)

        # -*- Extract Loop Bounds -*-
        start, stop, step = l_bounds

        start = compiler.evaluate(start, miss=True, calc=True)
        stop = compiler.evaluate(stop, miss=True, calc=True)
        step = compiler.evaluate(step, miss=True, calc=True, null=True)

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

        # -*- Condition Compilation -*-
        if l_conds is not None:
            # Compile condition expressions
            cond = reduce(
                lambda x, y: x._AND_(y),
                [compiler.evaluate(c, miss=True, calc=True, context={var: var for var in var_bag}) for c in l_conds],
                Number("1"),
            )
        else:
            cond = None

        # -*- Stack in reverse order -*-
        stack.push({"type": l_type, "var": l_var, "bounds": (start, stop, step), "cond": cond})

    # -*- Expression Analysis -*-
    if stdlog[3]:
        stdlog[3] << f"\n@{name}(raw):\n\t{expr}"

    if str(constype) == CONS_INT and expr.is_expr and not expr.logical:
        compiler << SatExprError(
            "Integrity constraint expressions must be purely logical i.e. no arithmetic operations allowed.",
            target=expr,
        )

    compiler.checkpoint()

    # Checks for undefined variables + evaluate constants
    # Adds inner scope where inside-loop variables point to themselves. This prevents both
    # older variables from interfering in evaluation and also undefined loop variables.
    # Last but not least, automatically removes this artificial scope
    expr: Expr = compiler.source.propagate(
        expr,
        compiler.evaluate(
            expr,
            miss=True,
            calc=False,
            null=False,
            context={var: var for var in var_bag},
        ),
        out=True,
    )

    if stdlog[3]:
        stdlog[3] << f"\n@{name}(verified):\n\t{expr}"

    # Simplifies expression
    expr: Expr = compiler.source.propagate(
        expr,
        compiler.evaluate(expr, miss=False, calc=True, null=False),
        out=True,
    )

    if stdlog[3]:
        stdlog[3] << f"\n@{name}(simplified):\n\t{expr}"

    build(compiler, constype, stack, Stack(), level, expr)


def build(compiler: SatCompiler, constype: str, A: Stack, B: Stack, level: Number, expr: Expr):
    """"""
    if A:
        # -*- Retrieve Innermost Quatifier -*-
        item = A.pop()

        if constype == CONS_INT:
            if item["type"] == T_UNIQUE:
                # -*- Winner Takes All -*-
                R = A.copy()
                S = B.copy()

                B.push({**item, "type": T_EXISTS})
                build(compiler, constype, A, B, level, expr)

                var = Var(f"${item['var']}")

                if item["cond"] is None:
                    cond = Expr(T_NE, item["var"], var)
                else:
                    cond = Expr(T_AND, Expr.sub(item["cond"], item["var"], var), Expr(T_NE, item["var"], var))

                S.push({"type": T_EXISTS, "var": var, "bounds": item["bounds"], "cond": cond})
                S.push({**item, "type": T_EXISTS})

                build(compiler, constype, R, S, level + 1, Expr(T_NOT, Expr(T_AND, expr, Expr.sub(expr, item["var"], var))).dnf)
            elif item["type"] == T_FORALL:
                B.push({**item, "type": T_EXISTS})
                build(compiler, constype, A, B, level, expr)
            elif item["type"] == T_EXISTS:
                B.push({**item, "type": T_FORALL})
                build(compiler, constype, A, B, level, expr)
            else:
                raise ValueError(f"Invalid quatifier {item['type']}")
        elif constype == CONS_OPT:
            if item["type"] == T_UNIQUE:
                # -*- Winner Takes All -*-
                R = A.copy()
                S = B.copy()

                B.push({**item, "type": T_FORALL})
                build(compiler, constype, A, B, level, expr)

                var = Var(f"${item['var']}")

                if item["cond"] is None:
                    cond = Expr(T_NE, item["var"], var)
                else:
                    cond = Expr(T_AND, Expr.sub(item["cond"], item["var"], var), Expr(T_NE, item["var"], var))

                S.push({"type": T_FORALL, "var": var, "bounds": item["bounds"], "cond": cond})
                S.push({**item, "type": T_FORALL})

                build(compiler, constype, R, S, level + 1, Expr(T_NOT, Expr(T_AND, expr, Expr.sub(expr, item["var"], var))).dnf)
            elif item["type"] == T_FORALL:
                B.push(item)
                build(compiler, constype, A, B, level, expr)
            elif item["type"] == T_EXISTS:
                B.push(item)
                build(compiler, constype, A, B, level, expr)
            else:
                raise ValueError(f"Invalid quatifier {item['type']}")
        else:
            raise ValueError(f"Invalid constraint type '{constype}'")
    else:
        if constype == CONS_INT:
            expr = Expr.calculate(~expr)
            if expr.is_expr:
                energy = unstack(compiler, B, expr.dnf, {})
            else:
                # Here I'm supposing that everything that is not an 'Expr' is in the C.N.F.
                # (Also in any other normal form, such as D.N.F.)
                energy = unstack(compiler, B, expr, {})
        elif constype == CONS_OPT:
            if expr.is_expr:
                energy = unstack(compiler, B, expr.dnf, {})
            else:
                energy = unstack(compiler, B, expr, {})
        else:
            raise ValueError(f"Invalid constraint type '{constype}'")

        if level is None:
            level = 0

        if stdlog[3]:
            stdlog[3] << energy

        compiler.constraints[constype].append((int(level), energy))


def unstack(compiler: SatCompiler, stack: Stack, expr: Expr, context: dict) -> tuple[int, Posiform]:
    """"""

    if stack:
        # -*- Retrieve Innermost Quatifier -*-
        item = stack.pop()

        var: Var = item["var"]

        if item["type"] == T_FORALL:
            energy = Posiform(1.0)
            for i in arange(*item["bounds"]):
                context[var] = i
                if item["cond"] is None or compiler.evaluate(item["cond"], miss=False, context=context):
                    energy *= unstack(compiler, stack, expr, context)
            else:
                del context[var]

        elif item["type"] == T_EXISTS:
            energy = Posiform(0.0)
            for i in arange(*item["bounds"]):
                context[var] = i
                if item["cond"] is None or compiler.evaluate(item["cond"], miss=False, context=context):
                    energy += unstack(compiler, stack, expr, context)
            else:
                del context[var]
        else:
            raise ValueError(f"Invalid Quantifier '{item['type']}'")

        # -*- Get Quantifier Back -*-
        stack.push(item)

        return energy
    else:
        return H(compiler.evaluate(expr, miss=False, context=context))


def H(x: SatType) -> Posiform:
    """Energy Equation Mapping"""

    if x.is_expr:
        if x.head == T_NOT:
            return 1.0 - H(x[1])
        elif x.head == T_AND or x.head == T_MUL:
            e = Posiform(1.0)
            for y in x.tail:
                e *= H(y)
            return e
        elif x.head == T_OR or x.head == T_ADD:
            e = Posiform(0.0)
            for y in x.tail:
                e += H(y)
            return e
        elif x.head == T_XOR:
            a, b = x.tail
            return H((a & ~b) | (~a & b))
        else:
            raise ValueError(f"Unable to map '{x.head}' into energy equation")
    elif x.is_number:
        return Posiform(x)
    elif x.is_var:
        return Posiform({(x,): 1.0})
    else:
        raise ValueError(f"Unable to map '{x}' into energy equation")
