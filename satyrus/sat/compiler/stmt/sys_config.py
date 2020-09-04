""" SYS_CONFIG
    ==========

    STATUS: INCOMPLETE
"""

## Standard Library
from sys import intern

## Local
from ...types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA, EXIT
from ...types import SatType, String, Number, Var, Array
from ...types.error import SatValueError, SatTypeError

def sys_config(compiler, name: Var, args: list):
    if name in sys_config_options:
        return sys_config_options[name](compiler, name, len(args), args)
    else:
        compiler << SatValueError(f'Invalid config option ´{name}´.', target=name)
    compiler.checkpoint()

def sys_config_prec(compiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(f'´#prec´ expected 1 argument, got {argc}', target=name)
        else:
            compiler << SatValueError(f'´#prec´ expected 1 argument, got {argc}', target=argv[1])
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(f'Precision must be a positive integer.', target=argv[0])
    elif not argv[0].is_int or argv[0] <= 0:
        compiler << SatValueError(f'Precision must be a positive integer.', target=argv[0])
    else:
        Number.prec(int(argv[0]))
        compiler.env.memset(Var(PREC), argv[0])
    compiler.checkpoint()

def sys_config_epsilon(compiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(f'´#epsilon´ expected 1 argument, got none.', target=name)
        else:
            compiler << SatValueError(f'´#epsilon´ expected 1 argument, got {argc}.', target=argv[1])
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(f'Epsilon must be a positive number.', target=argv[0])
    elif argv[0] <= 0:
        compiler << SatValueError(f'Epsilon must be a positive number.', target=argv[0])
    else:
        compiler.env.memset(Var(EPSILON), argv[0])
    compiler.checkpoint()

def sys_config_load(compiler, name: Var, argc: int, argv: list):
    raise NotImplementedError

def sys_config_alpha(compiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(f'`#alpha` expected 1 argument, got none.', target=name)
        else:
            compiler << SatValueError(f'`#alpha` expected 1 argument, got {argc}.', target=argv[1])
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(f'Parameter `alpha` must be a positive number.', target=argv[0])
    elif argv[0] <= 0:
        compiler << SatValueError(f'Parameter `alpha` must be a positive number.', target=argv[0])
    else:
        compiler.env.memset(Var(ALPHA), argv[0])
    compiler.checkpoint()

def sys_config_exit(compiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(f'`#exit` expected 1 argument (exit code), got none.', target=name)
        else:
            compiler << SatValueError(f'`#exit` expected 1 argument (exit code), got {argc}.', target=argv[1])
    elif type(argv[0]) is not Number:
        compiler << SatTypeError(f'The exit code must be a non-negative integer.', target=argv[0])
    elif not argv[0].is_int or argv[0] < 0:
        compiler << SatValueError(f'The exit code must be a non-negative integer.', target=argv[0])
    else:
        compiler.exit(int(argv[0]))
    compiler.checkpoint()

def sys_config_out(compiler, name: Var, argc: int, argv: list):
    raise NotImplementedError

def sys_config_dir(compiler, name: Var, argc: int, argv: list):
    if argc != 1:
        if argc == 0:
            compiler << SatValueError(f'`dir` expected 1 argument, got None', target=name)
        else:
            compiler << SatValueError(f'`dir` expected 1 argument, got {argc}', target=argv[1])
    else:
        compiler.dir_push(argv[0])
    compiler.checkpoint()

sys_config_options = {
    EXIT : sys_config_exit,
    PREC : sys_config_prec,
    DIR : sys_config_dir,
    LOAD : sys_config_load,
    EPSILON : sys_config_epsilon,
    ALPHA : sys_config_alpha,
    OUT : sys_config_out,
}