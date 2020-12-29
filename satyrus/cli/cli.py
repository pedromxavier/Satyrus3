r""" Satyrus III - A compiler.
"""
## Standard Library
import argparse
import sys
import os

## Local
from .help import HELP
from ..api import SatAPI
from ..satlib import stream, stdout, stdwar, stderr

class CLI:

    class ArgumentParser(argparse.ArgumentParser):

        def error(self, message):
            stderr << f"Argument Error: {message}"
            self.print_help(stdout)
            exit(1)

    @classmethod
    def run(cls):
        """ :: Satyrus CLI ::
            =================
        """
        ap_kwargs = {
            'description' : __doc__
        }

        parser = cls.ArgumentParser(**ap_kwargs)
        ## Mandatory - Source file path
        parser.add_argument("source", help=HELP['source'])

        ## Optional - Output format
        parser.add_argument("-o", "--out", type=str, dest="out", choices=SatAPI.options, help=HELP['out'])

        ## Optional - Legacy Syntax
        parser.add_argument("--legacy", action='store_true', help=HELP['legacy'])

        ## Optional - Compiler Optmization degree
        mutex_group = parser.add_mutually_exclusive_group()
        mutex_group.add_argument('-O0', dest='O', action='store_const', const=0)
        mutex_group.add_argument('-O1', dest='O', action='store_const', const=1)
        mutex_group.add_argument('-O2', dest='O', action='store_const', const=2)
        mutex_group.add_argument('-O3', dest='O', action='store_const', const=3)

        ## Optional - Compiler Verbosity
        parser.add_argument('-v', '--verbose', type=int, dest='verbose', choices=[0, 1, 2, 3, 4, 5], help=HELP['verbose'])

        args = parser.parse_args()

        ## Check source path
        source_path: str = args.source

        if not os.path.exists(source_path):
            stderr << f"File Error: File `{os.path.abspath(source_path)}` doesn't exists."
            exit(1)

        ## Legacy mode
        legacy: bool = args.legacy

        if legacy:
            stdwar << f"Warning: Parser is in legacy mode."

        ## Output selection
        output: str = args.out

        if output is None:
            output = 'text'

        ## Compiler Optmization
        O: int = args.O

        if O is None:
            O = 0

        ## Compiler Verbosity
        verbose: int = args.verbose

        if verbose is None:
            verbose = 0

        ## Sets compiler verbosity
        stream.set_lvl(verbose)

        ## Exhibits Compiler Command line arguments
        stdout[5] << f"Command line args: {vars(args)}"

        sat_kwargs = {
            'legacy': legacy,
            'O': O
        }

        ## Compile Problem
        sat_api = SatAPI(source_path=source_path, **sat_kwargs)

        ## Solve in desired way
        sat_api[output].solve()

        

        