""" :: RUN_INIT ::
	====================

	STATUS: COMPLETE
"""

from ..compiler import SatCompiler
from ..components.mapping import RelaxedMapping
from ...types import Number
from ...types.symbols import PREC, DIR, LOAD, OPT, EPSILON, ALPHA, MAPPING

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
        (MAPPING, RelaxedMapping),
    ]

    for key, val in default_env:
        if key not in compiler.env:
            compiler.env[key] = val