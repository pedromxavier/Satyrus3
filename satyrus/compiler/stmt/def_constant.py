from ...types.error import SatReferenceError
from ...types import SatType, Var

def def_constant(compiler, name : Var, value : SatType):
    try:
        compiler.memory.memset(name, compiler.eval(value))
    except SatReferenceError as error:
        yield error