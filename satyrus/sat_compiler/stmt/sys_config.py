from ...sat_types.symbols import PREC, DIR, LOAD, OUT, EPSILON, N0

from ...sat_types import SatType, String, Number, Var, Array, NULL
from ...sat_types.error import SatValueError, SatTypeError

def sys_config(compiler, name : str, args : list):
	yield from sys_config_options[name](compiler, len(args), args)

def sys_config_prec(compiler, argc : int, argv : list):
    if argc == 1:
        prec = argv[0]
    else:
        yield SatValueError(f'´#prec´ expected 1 argument, got {argc}', target=argv[1])

    if type(prec) is Number and prec.is_int and prec > 0:
        compiler.env.memset(PREC, prec)
    else:
        yield SatTypeError(f'Precision must be a positive integer.', target=argv[0])

def sys_config_epsilon(compiler, argc : int, argv : list):
    if argc == 1:
        epsilon = argv[0]
    else:
        yield SatValueError(f'´#epsilon´ expected 1 argument, got {argc}', target=argv[1])

    if type(epsilon) is Number and epsilon > 0:
        compiler.env.memset(EPSILON, epsilon)
    else:
        yield SatTypeError(f'Epsilon must be a positive number.', target=argv[0])

def sys_config_load(compiler, argc : int, argv : list):
    for fname in argv:
        yield from sat_load(compiler, fname)

def sat_load(compiler, fname : str):
    ...

def sys_config_n0(compiler, argc : int, argv : list):
    if argc == 1:
        n0 = argv[0]
    else:
        yield SatValueError(f'´#n0´ expected 1 argument, got {argc}.', target=argv[1])

    if type(n0) is Number and n0 > 0:
        compiler.env.memset(N0, n0)
    else:
        yield SatTypeError(f'n0 must be a positive number.', target=argv[0])

def sys_config_out(compiler, argc : int, argv : list):
    raise NotImplementedError

def sys_config_dir(compiler, argc : int, argv : list):
    raise NotImplementedError

sys_config_options = {
    PREC : sys_config_prec,
    DIR : sys_config_dir,
    LOAD : sys_config_load,
    EPSILON : sys_config_epsilon,
    N0 : sys_config_n0,
    OUT : sys_config_out,
}