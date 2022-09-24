""" DEF_CONSTANT
    ============

    STATUS: OK
"""

from ..compiler import SATCompiler
from ...error import SATReferenceError
from ...types import SATType, Var

def def_constant(compiler: SATCompiler, name : Var, value : SATType):
    """ DEF_CONSTANT
        ============
    """
    compiler.memset(name, compiler.evaluate(value, miss=True, calc=True, null=False, track=True))