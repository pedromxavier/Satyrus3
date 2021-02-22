""" :: RUN_INIT ::
	====================

	STATUS: COMPLETE
"""

from ..compiler import SatCompiler
from ...types import Number, Relaxed, Default
from ...types.symbols import PREC, DIR, LOAD, OPT, EPSILON, ALPHA, MAPPING, INDEXER

def run_init(compiler: SatCompiler, *args: tuple):
    """ RUN_INIT
        ========
        
        Initializes compiler env
    """
    default_env = [
        (PREC, 16),
        (OPT, 0),
        (ALPHA, Number('1.0')),
        (EPSILON, Number('1E-4')),
        (MAPPING, Relaxed),
        (INDEXER, Default)
    ]

    for key, val in default_env:
        if key not in compiler.env:
            compiler.env[key] = val