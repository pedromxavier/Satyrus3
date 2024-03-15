"""\
satyrus.cli
-----------

Implements Satyrus Command line interface using ``argparse``.
"""
from .cli import SatCLI
from .api_cli import SatAPICLI

__all__ = ["SatCLI", "SatAPICLI"]
