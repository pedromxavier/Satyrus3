## Standard Library
from sys import intern

## Local
from ...sat_types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA, EXIT
from ...sat_types import SatType, String, Number, Var, Array
from ...sat_types.error import SatValueError, SatTypeError

def sys_config(compiler, name: str, args: list):
    if name in sys_config_options:
        yield from sys_config_options[name](compiler, name, len(args), args)
    else:
        yield SatValueError(f'Invalid config option ´{name}´.', target=name)

def sys_config_prec(compiler, name, argc: int, argv: list):
    if argc == 1:
        prec = argv[0]
    elif argc == 0:
        yield SatValueError(f'´#prec´ expected 1 argument, got {argc}', target=name)
    else:
        yield SatValueError(f'´#prec´ expected 1 argument, got {argc}', target=argv[1])

    if type(prec) is Number and prec.is_int and prec > 0:
        compiler.env.memset(Var(PREC), prec)
    else:
        yield SatTypeError(f'Precision must be a positive integer.', target=argv[0])

def sys_config_epsilon(compiler, name, argc : int, argv : list):
    if argc == 1:
        epsilon = argv[0]
    else:
        yield SatValueError(f'´#epsilon´ expected 1 argument, got {argc}', target=argv[1])

    if type(epsilon) is Number and epsilon > 0:
        compiler.env.memset(Var(EPSILON), epsilon)
    else:
        yield SatTypeError(f'Epsilon must be a positive number.', target=argv[0])

def sys_config_load(compiler, name, argc : int, argv : list):
    for fname in argv:
        yield from sat_load(compiler, fname)

def sat_load(compiler, fname : str):
    ...

def sys_config_alpha(compiler, name, argc : int, argv : list):
    if argc == 1:
        alpha = argv[0]
    else:
        yield SatValueError(f'`#alpha` expected 1 argument, got {argc}.', target=argv[1])

    if type(alpha) is Number and alpha > 0:
        compiler.env.memset(Var(ALPHA), alpha)
    else:
        yield SatTypeError(f'alpha must be a positive number.', target=argv[0])

def sys_config_exit(compiler, name, argc : int, argv : list):
    if argc != 1:
        if argc == 0:
            yield SatValueError(f'`exit` expected 1 argument (exit code), got {argc}', target=argv[1])
        else:
            yield SatValueError(f'`exit` expected 1 argument (exit code), got {argc}', target=None)
    elif type(argv[0]) is not Number or not argv[0].is_int or argv[0] < 0:
        yield SatTypeError(f'exit code must be a non-negative integer.')
    else:
        compiler.exit(int(argv[0]))

def sys_config_out(compiler, name, argc : int, argv : list):
    raise NotImplementedError

def sys_config_dir(compiler, name, argc : int, argv : list):
    if argc == 1:
        compiler.dir(argv[0])
    elif argc == 0:
        yield SatValueError(f'`dir` expected 1 argument, got None', target=name)
    else:
        yield SatValueError(f'`dir` expected 1 argument, got {argc}', target=argv[1])

sys_config_options = {
    EXIT : sys_config_exit,
    PREC : sys_config_prec,
    DIR : sys_config_dir,
    LOAD : sys_config_load,
    EPSILON : sys_config_epsilon,
    ALPHA : sys_config_alpha,
    OUT : sys_config_out,
}