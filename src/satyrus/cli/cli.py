r""" Satyrus III - A compiler.
"""
## Standard Library
import argparse
import sys
import os

## Local
from .help import HELP
from ..api import SatAPI
from ..assets import SAT_BANNER
from ..satlib import Stream, stdlog, stdout, stdwar, stderr, log

class CLI:
    """Satyrus command line interface.

    Note
    ----

    Example
    -------
    >>> CLI.run()
    """

    class ArgumentParser(argparse.ArgumentParser):

        def print_help(self, from_help: bool=True):
            if from_help: stdlog[0] << SAT_BANNER
            argparse.ArgumentParser.print_help(self, stdlog[0])

        def error(self, message):
            stderr << f"Command Error: {message}"
            self.print_help(from_help=False)
            exit(1)

    @classmethod
    def run(cls, argv: list=None):
        """
        Options
        -------
        source : str
            Path to source code.
        -o, --out : str
            Output method.
        --legacy : bool
            If True, uses the legacy parser.
        -O : int
            Compiler optimization level.
        -v : int
            Compiler verbosity level.
        -d, --debug : bool
            If True, enables debug mode.
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

        ## Optional - Debug Mode
        parser.add_argument('-d', '--debug', action='store_true', help=HELP['debug'])

        if argv is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(argv)

        ## Compiler Verbosity
        verbose: int = args.verbose

        if verbose is None:
            verbose = 0

        ## Debug mode
        debug: bool = args.debug

        if debug:
            verbose = 3 ## forces maximum verbosity

        ## Sets compiler verbosity
        Stream.set_lvl(verbose)

        ## Check source path
        source_path: str = args.source

        if not os.path.exists(source_path):
            stderr[0] << f"File Error: File `{os.path.abspath(source_path)}` doesn't exists."
            exit(1)

        ## Legacy mode
        legacy: bool = args.legacy

        if legacy:
            stdwar[0] << f"Warning: Parser is in legacy mode."

        ## Output selection
        output: str = args.out

        if output is None:
            output = 'text'

        ## Compiler Optmization
        opt: int = args.opt

        if opt is None:
            opt = 0

        ## Exhibits Compiler Command line arguments
        stdlog[3] << f"Command line args: {vars(args)}"

        sat_kwargs = {
            'legacy': legacy,
            'opt': opt
        }

        ## Compile Problem
        try:
            sat_api = SatAPI(source_path=source_path, **sat_kwargs)
        except Exception:
            trace = log()
            if debug:
                stderr[0] << trace
            else:
                from ..assets import SAT_CRITICAL_ERROR
                print(SAT_CRITICAL_ERROR, file=sys.stderr)
            return None

        ## Solve in desired way
        answer: (dict, float) = sat_api[output].solve()

        ## Compilation Failed
        if answer is None:
            return None

        ## Output
        x, e = answer
        if x is not None: ## Print solution
            for var, val in x.items():
                stdout[0] << f"{var}\t{val}" ## Variable choice
            stdout[0] << f"E = {e}" ## Total energy for given configuration
        else: ## Incomplete process
            stdout[0] << e

        

        