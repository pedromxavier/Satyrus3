""" DEF_CONSTANT
    ============

    STATUS: OK
"""

from ..compiler import SatCompiler
from ...types.error import SatReferenceError
from ...types import SatType, Var

def def_constant(compiler: SatCompiler, name : Var, value : SatType):
    """ DEF_CONSTANT
        ============
    """
    compiler.memset(name, compiler.evaluate(value, miss=True, calc=True, null=False, track=True))