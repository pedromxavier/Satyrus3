""" :: RUN_INIT ::
	====================

	STATUS: INCOMPLETE
"""

from ..compiler import SatCompiler
from ...types import Number, Relaxed, Default
from ...types.symbols import PREC, DIR, LOAD, OUT, EPSILON, ALPHA, MAPPING, INDEXER

def run_init(compiler: SatCompiler, *args: tuple):
    """ RUN_INIT
        ========
        
        Initializes compiler env
    """
    compiler.env[PREC] = 16

    compiler.env[ALPHA] = Number('1.0')

    compiler.env[EPSILON] = Number('1E-4')

    compiler.env[MAPPING] = Relaxed

    compiler.env[INDEXER] = Default