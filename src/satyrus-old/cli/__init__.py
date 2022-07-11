"""\
satyrus.cli
-----------

Implements SATyrus Command line interface using ``argparse``.
"""
from .cli import SATCLI
from .api_cli import SATAPICLI

__all__ = ["SATCLI", "SATAPICLI"]
