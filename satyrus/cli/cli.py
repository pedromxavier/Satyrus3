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
        parser.add_argument('-O', type=int, dest='opt', choices=[0, 1, 2, 3], help=HELP['opt'])

        ## Optional - Compiler Verbosity
        parser.add_argument('-v', '--verbose', type=int, dest='verbose', choices=[0, 1, 2, 3], help=HELP['verbose'])

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
        opt: int = args.opt

        if opt is None:
            opt = 0

        ## Compiler Verbosity
        verbose: int = args.verbose

        if verbose is None:
            verbose = 0

        ## Sets compiler verbosity
        stream.set_lvl(verbose)

        ## Exhibits Compiler Command line arguments
        stdout[3] << f"Command line args: {vars(args)}"

        sat_kwargs = {
            'legacy': legacy,
            'opt': opt
        }

        ## Compile Problem
        sat_api = SatAPI(source_path=source_path, **sat_kwargs)

        ## Solve in desired way
        stdout[0] << sat_api[output].solve()

        

        