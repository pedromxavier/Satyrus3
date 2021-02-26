from .satlib import Stream, stdout, stdwar, stdlog, stderr, Posiform
from .satyrus import Satyrus
from .api import SatAPI
from .cli import CLI

def main():
    import sys
    CLI.run(sys.argv)