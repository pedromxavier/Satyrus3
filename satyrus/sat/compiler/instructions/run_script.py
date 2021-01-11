""" :: RUN_SCRIPT ::
	====================

	STATUS: INCOMPLETE
"""

## Third-Party
from tabulate import tabulate

## Local
from ....satlib import stdout
from ...types.error import SatValueError, SatCompilerError, SatWarning
from ...types import Number
from ...types.expr import Expr
from ...types.symbols import PREC, EPSILON, ALPHA
from ...types.symbols import CONS_INT, CONS_OPT
from ..compiler import SatCompiler

def run_script(compiler: SatCompiler, *args: tuple):
    """ RUN_SCRIPT
        ==========
    """
    ## Setup compiler environment
    run_script_setup(compiler)

    ## Retrieve constraints
    constraints = {}
    run_script_constraints(compiler, constraints)

    ## Compute penalties
    penalties = {}
    run_script_penalties(compiler, constraints, penalties)

    ## Generate Energy Equations
    run_script_energy(compiler, constraints, penalties)

def run_script_setup(compiler: SatCompiler):
    ## Set numeric precision
    Number.prec(int(compiler.env[PREC]))

    ## value for alpha
    compiler.env[ALPHA] = Number(compiler.env[ALPHA])

    ## value for epsilon
    compiler.env[EPSILON] = Number(compiler.env[EPSILON])

    ## Parameter validation
    if (compiler.env[EPSILON] < pow(10, -Number.prec(None))):
        compiler << SatValueError("Tiebraker `epsilon` is neglected due to numeric precision.", target=compiler.env[EPSILON])

    compiler.checkpoint()

def run_script_constraints(compiler: SatCompiler, constraints: dict):
    """ Constraint compilation
    """

    ## Retrieve constraints
    all_constraints = [item for item in compiler.memory if (type(item) is Constraint)]

    constraints.update({
        CONS_INT: [cons for cons in all_constraints if (cons.type == CONS_INT)],
        CONS_OPT: [cons for cons in all_constraints if (cons.type == CONS_OPT)]
    })

    if len(constraints[CONS_INT]) + len(constraints[CONS_OPT]) == 0:
        compiler << SatCompilerError("No problem defined. Maybe you are just fine.", target=compiler.source.eof)
    elif len(constraints[CONS_INT]) == 0:
        compiler < SatWarning("No Integrity condition defined.", target=compiler.source.eof)
    elif len(constraints[CONS_OPT]) == 0:
        compiler << SatCompilerError("No Optmization condition defined.", target=compiler.source.eof)

    compiler.checkpoint()


def run_script_penalties(compiler: SatCompiler, constraints: dict, penalties: dict):
    ## Penalties
    penalties.update({
        0 : compiler.env[ALPHA]
    })

    levels = {
        0 : sum(len(cons.clauses) for cons in constraints[CONS_OPT])
    }

    for cons in constraints[CONS_INT]:
        cons: Constraint
        if cons.level not in levels:
            levels[cons.level] = len(cons.clauses)
        else:
            levels[cons.level] += len(cons.clauses)
    else:
        levels = sorted(levels.items())

    ## Compute penalty levels
    level_j, n_j = levels[0]
    for i in range(1, len(levels)):
        ## level_k <- level_j & n_k <- n_j
        ## level_j <- level_i & n_j <- n_i
        (level_k, n_k), (level_j, n_j) = (level_j, n_j), levels[i]
        
        if i == 1:
            penalties[level_j] = penalties[level_k] * n_k + compiler.env[EPSILON]
        else:
            penalties[level_j] = penalties[level_k] * (n_k + 1)
    else: ## print penalty table
        stdout[2] << tabulate([(f"{k:6d}", f"{n:d}", penalties[k]) for k, n in levels], headers=["lvl", "n", "value"], tablefmt="pretty")
        stdout[2] << tabulate([[compiler.env[EPSILON], compiler.env[ALPHA]]], headers =["ε", "α"], tablefmt="pretty")


def run_script_energy(compiler: SatCompiler, constraints: dict, penalties: dict):
    """
    """
    print("CLAUSES:")
    print("\tINTEGRITY:")
    for cons in constraints[CONS_INT]:
        print(f'\texpr: {cons.expr}')
        print(f"\t{cons.clauses}")
    print("\tOPTMITY:")
    for cons in constraints[CONS_OPT]:
        print(f'\texpr: {cons.expr}')
        print(f"\t{cons.clauses}")