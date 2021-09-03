"""
"""

from ..compiler import SatCompiler
from ...types import Number
from ...symbols import PREC, OPT, EPSILON, ALPHA


def run_init(compiler: SatCompiler, *args: tuple):
    """\
    Initializes compiler environment
    """
    default_env = [
        (PREC, 16),
        (OPT, 0),
        (ALPHA, Number("1.0")),
        (EPSILON, Number("1E-4")),
    ]

    for key, val in default_env:
        if key not in compiler.env:
            compiler.env[key] = val
