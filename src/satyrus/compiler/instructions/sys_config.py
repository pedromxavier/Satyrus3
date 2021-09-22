""" SYS_CONFIG
    ==========

    STATUS: INCOMPLETE
"""

## Standard Library
from pathlib import Path

## Local
from ..compiler import SatCompiler
from ...satlib import Source
from ...symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA, EXIT
from ...types import SatType, String, Number, Var, Array
from ...error import SatValueError, SatTypeError, SatFileError, SatWarning


def sys_config(compiler, name: Var, args: list):
    if name in sys_config_options:
        return sys_config_options[name](compiler, name, len(args), args)
    else:
        compiler << SatValueError(f"Invalid config option '{name}'.", target=name)
    compiler.checkpoint()


def sys_config_prec(compiler: SatCompiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(
                f"'?prec' expected 1 argument, got {argc}", target=name
            )
        else:
            compiler << SatValueError(
                f"'?prec' expected 1 argument, got {argc}", target=argv[1]
            )
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(
            f"Precision must be a positive integer.", target=argv[0]
        )
    elif not argv[0].is_int or int(argv[0]) <= 0:
        compiler << SatValueError(
            f"Precision must be a positive integer.", target=argv[0]
        )
    else:
        compiler.env[PREC] = argv[0]
    compiler.checkpoint()


def sys_config_epsilon(compiler: SatCompiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(
                f"'?epsilon' expected 1 argument, got none.", target=name
            )
        else:
            compiler << SatValueError(
                f"'?epsilon' expected 1 argument, got {argc}.", target=argv[1]
            )
    elif not isinstance(argv[0], Number):
        compiler << SatTypeError(f"Epsilon must be a positive number", target=argv[0])
    elif float(argv[0]) <= 0.0:
        compiler << SatValueError(f"Epsilon must be a positive number", target=argv[0])
    else:
        if float(argv[0]) >= 1.0:
            compiler < SatWarning("Large values for Epsilon may cause Integrity errors")
        compiler.env[EPSILON] = argv[0]
    compiler.checkpoint()


def sys_config_load(compiler: SatCompiler, name: Var, argc: int, argv: list):
    if argc == 0:
        compiler << SatValueError(
            "`?load` expected 1 or more arguments, got none.", target=name
        )
    else:
        paths = []
        for fname in argv:
            path = Path(f"{fname}.sat")
            if not path.exists() or not path.is_file():
                compiler << SatFileError(f"file '{path}' not found.", target=fname)
            else:
                paths.append(path.absolute())

        bytecode = []
        for path in paths:
            bytecode.extend(compiler.parse(Source(path)))
        else:
            compiler.execute(bytecode)

        compiler.checkpoint()


def sys_config_alpha(compiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(
                f"`?alpha` expected 1 argument, got none.", target=name
            )
        else:
            compiler << SatValueError(
                f"`?alpha` expected 1 argument, got {argc}.", target=argv[1]
            )
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(
            f"Parameter `alpha` must be a positive number.", target=argv[0]
        )
    elif float(argv[0]) <= 0:
        compiler << SatValueError(
            f"Parameter `alpha` must be a positive number.", target=argv[0]
        )
    else:
        compiler.env[ALPHA] = argv[0]
    compiler.checkpoint()


def sys_config_exit(compiler, name: Var, argc: int, argv: list):
    """Exits program, for debug purposes."""
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(
                f"`?exit` expected 1 argument (exit code), got none.", target=name
            )
        else:
            compiler << SatValueError(
                f"`?exit` expected 1 argument (exit code), got {argc}.", target=argv[1]
            )
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(
            f"The exit code must be a non-negative integer.", target=argv[0]
        )
    elif not argv[0].is_int or int(argv[0]) < 0:
        compiler << SatValueError(
            f"The exit code must be a non-negative integer.", target=argv[0]
        )
    else:
        compiler.exit(int(argv[0]))
    compiler.checkpoint()


# def sys_config_out(compiler, name: Var, argc: int, argv: list):
# raise NotImplementedError

sys_config_options = {
    EXIT: sys_config_exit,
    PREC: sys_config_prec,
    LOAD: sys_config_load,
    EPSILON: sys_config_epsilon,
    ALPHA: sys_config_alpha,
    ## OUT : sys_config_out,
}
