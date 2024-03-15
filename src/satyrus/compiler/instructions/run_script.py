"""
"""
# Standard Library
import itertools as it

# Third-Party
from tabulate import tabulate
from cstream import stdlog

# Local
from ..compiler import SatCompiler
from ...error import SatValueError, SatCompilerError, SatWarning
from ...types import Number
from ...symbols import CONS_INT, CONS_OPT, PREC, EPSILON, ALPHA


def run_script(compiler: SatCompiler, *args: tuple):
    """
    """
    # Setup compiler environment
    run_script_setup(compiler)

    # Retrieve constraints
    run_script_constraints(compiler)

    # Check for Errors
    compiler.checkpoint()

    # Compute penalties
    run_script_penalties(compiler)

    # Generate Energy Equations
    run_script_energy(compiler)


def run_script_setup(compiler: SatCompiler):
    ## Set numeric precision
    Number.prec(int(compiler.env[PREC]))

    # value for alpha
    compiler.env[ALPHA] = Number(compiler.env[ALPHA])

    # value for epsilon
    compiler.env[EPSILON] = Number(compiler.env[EPSILON])

    ## Parameter validation
    if compiler.env[EPSILON] < pow(10, -Number.prec(None)):
        compiler << SatValueError(
            "Tiebraker 'epsilon' was neglected due to numeric precision. Choose a greater value",
            target=compiler.env[EPSILON],
        )


def run_script_constraints(compiler: SatCompiler):
    """ """

    # -*- Constraint Validation -*-
    if len(compiler.constraints[CONS_INT]) + len(compiler.constraints[CONS_OPT]) == 0:
        compiler << SatCompilerError("No problem defined. Maybe you are just fine :)", target=compiler.source.eof)
    elif len(compiler.constraints[CONS_INT]) == 0:
        compiler < SatWarning("No Integrity condition defined.", target=compiler.source.eof)
    elif len(compiler.constraints[CONS_OPT]) == 0:
        compiler < SatCompilerError("No Optmization condition defined.", target=compiler.source.eof)


def run_script_penalties(compiler: SatCompiler):
    """ """
    # -*- Penalty Computation -*-
    compiler.penalties.update({0: float(compiler.env[ALPHA])})

    levels: dict[int, float] = {}

    constraints = it.chain(compiler.constraints[CONS_OPT], compiler.constraints[CONS_INT])

    for level, energy in constraints:
        if level not in levels:
            levels[level] = 0.0

        for term, cons in energy:
            if term is None:
                continue
            else:
                # Compute Energy Gap
                levels[level] += abs(cons)
    else:
        levels: list = sorted(levels.items())

    epsilon = float(compiler.env[EPSILON])

    # Compute penalty levels
    level_j, n_j = levels[0]
    for i in range(1, len(levels)):
        # level_k <- level_j, n_k <- n_j, level_j <- level_i, n_j <- n_i
        (level_k, n_k), (level_j, n_j) = (level_j, n_j), levels[i]

        if i == 1: # Base Penalty
            compiler.penalties[level_j] = compiler.penalties[level_k] * n_k + epsilon
        else:
            compiler.penalties[level_j] = compiler.penalties[level_k] * (n_k + 1)

    # -*- Penalty Table Exhibition -*-
    if stdlog[2]:
        stdlog[2] << "PENALTY TABLE"
        stdlog[2] << tabulate(
            [(f"{k}", f"{n}", compiler.penalties[k]) for k, n in levels],
            headers=["lvl", "n", "value"],
            tablefmt="pretty",
        )
        stdlog[2] << ""
        stdlog[2] << "CONSTANTS"
        stdlog[2] << tabulate(
            [[compiler.env[EPSILON], compiler.env[ALPHA]]],
            headers=["ε", "α"],
            tablefmt="pretty",
        )


def run_script_energy(compiler: SatCompiler):
    """"""
    # Integrity
    Ei = sum((compiler.penalties[level] * energy for level, energy in compiler.constraints[CONS_INT]), 0.0)

    # Optimality
    Eo = sum((compiler.penalties[level] * energy for level, energy in compiler.constraints[CONS_OPT]), 0.0)

    compiler.energy = Ei + Eo