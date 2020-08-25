""" DEF_CONSTANT
    ============

    STATUS: OK
"""

from ...types.error import SatReferenceError
from ...types import SatType, Var

def def_constant(compiler, name : Var, value : SatType):
    """ DEF_CONSTANT
        ============
    """
    compiler.memset(name, compiler.eval(value))
    