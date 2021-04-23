r"""Satyrus optimization framework compiler.
"""
## Standard Library
import argparse
import sys
import os
from functools import wraps
from gettext import gettext

## Third-Party
from cstream import Stream, stdlog, stdout, stdwar, stderr

## Local
from .help import HELP
from ..api import SatAPI
from ..assets import SAT_BANNER
from ..satlib import Timing, log

class ArgParser(argparse.ArgumentParser):

    @wraps(argparse.ArgumentParser.__init__)
    def __init__(self, *args, **kwargs):
        self._rank = {}
        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    @wraps(argparse.ArgumentParser.parse_args)
    def parse_args(self, args: list=None, namespace: argparse.Namespace=None):
        args = argparse.ArgumentParser.parse_args(self, args, namespace)

        for p in sorted(self._rank.keys()):
            for action, params in self._rank[p]:
                action(*params)

        return args

    def print_help(self, from_help: bool=True):
        if from_help: stdlog[0] << SAT_BANNER
        argparse.ArgumentParser.print_help(self, stdlog[0])

    def error(self, message):
        stderr << f"Command Error: {message}"
        self.print_help(from_help=False)
        exit(1)

    @classmethod
    def enqueue(cls, priority: int=0):
        def decor(action):
            @wraps(action)
            def enqueued_action(self, parser, namespace, values, option_string=None):
                if isinstance(parser, cls):
                    params = (self, parser, namespace, values, option_string)
                    if priority in parser._rank:
                        parser._rank[priority].append((action, params))
                    else:
                        parser._rank[priority] = [(action, params)]
                else:
                    return action(self, parser, namespace, values, option_string)
            return enqueued_action
        return decor

class SetVerbosity(argparse._StoreAction):

    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(0)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        verbose = getattr(namespace, self.dest)
        Stream.set_lvl(verbose)

class DebugMode(argparse._StoreTrueAction):

    @wraps(argparse._StoreTrueAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreTrueAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(1)
    @wraps(argparse._StoreTrueAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreTrueAction.__call__(self, parser, namespace, values, option_string)
        setattr(namespace, 'verbose', 3)
        Stream.set_lvl(3)

class IncludeSatAPI(argparse._StoreAction):

    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(2)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        fname = getattr(namespace, self.dest)
        if fname is not None:
            SatAPI.include(fname)

class SetOutput(argparse._StoreAction):

    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(3)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser: ArgParser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        output = getattr(namespace, self.dest)
        if output not in SatAPI.options:
            parser.error(gettext(f'invalid choice: {output} (choose from {", ".join(map(repr, SatAPI.options))})'))

class CLI:
    """Satyrus command line interface.

    Example
    -------
    >>> CLI.run(["--help"])
    """
    @classmethod
    def run(cls, argv: list=None):
        """
        Parameters
        ----------

        source : str
            Path to source code.
        -o, --out : str
            Output method.
        --legacy : bool
            If True, uses the legacy parser.
        -O : int
            Compiler optimization level.
        -v, --verbose : int
            Compiler verbosity level.
        -d, --debug : bool
            If True, enables debug mode.
        -a, --api : str
            If present, include solver interfaces defined in python file.
        """

        ap_kwargs = {
            'prog' : 'satyrus',
            'description' : __doc__
        }

        parser = ArgParser(**ap_kwargs)

        ## Mandatory - Source file path
        parser.add_argument('source', help=HELP['source'])

        ## Optional - Compiler Verbosity
        parser.add_argument('-v', '--verbose', type=int, dest='verbose', choices=[0, 1, 2, 3], help=HELP['verbose'], action=SetVerbosity)

        ## Optional - Debug Mode
        parser.add_argument('-d', '--debug', dest='debug', help=argparse.SUPPRESS, action=DebugMode)

        ## Optional - Augmented API
        parser.add_argument('-a', '--api', type=str, dest='api', help=HELP['api'], action=IncludeSatAPI)

        ## Optional - Output format
        parser.add_argument('-o', '--out', type=str, dest="out", help=HELP['out'], action=SetOutput)

        ## Optional - Legacy Syntax
        parser.add_argument('-l', '--legacy', dest='legacy', action='store_true', help=HELP['legacy'])

        ## Optional - Legacy Syntax
        parser.add_argument('-r', '--report', dest='report', action='store_true', help=HELP['report'])

        ## Optional - Compiler Optmization degree
        parser.add_argument('-O', '--opt', type=int, dest='opt', choices=[0, 1, 2, 3], help=argparse.SUPPRESS)

        if argv is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(argv[1:])

        ## Debug mode
        debug: bool = args.debug

        if debug: stdwar[0] << f"Warning: Debug mode enabled."

        ## Check source path
        source_path: str = args.source

        if not os.path.exists(source_path):
            stderr[0] << f"File Error: File `{os.path.abspath(source_path)}` doesn't exists."
            exit(1)

        ## Legacy mode
        legacy: bool = args.legacy

        if legacy: stdwar[0] << f"Warning: Parser is in legacy mode."

        ## Report performance
        report: bool = args.report

        ## Output selection
        output: str = args.out

        if output is None: output = 'text'

        ## Compiler Optmization
        opt: int = args.opt

        if opt is None: opt = 0

        ## Exhibits Compiler Command line arguments
        with stdlog[3] as stream:
            stream << f"Command line args:"
            for k, v in vars(args).items():
                stream << f"\t{k}={v!r}"

        sat_kwargs = {
            'legacy': legacy,
            'opt': opt
        }

        ## Compile Problem
        try:
            sat_api = SatAPI(source_path=source_path, **sat_kwargs)

            ## Solve in desired way
            answer: (dict, float) = sat_api[output].solve()

            ## Compilation Failed
            if answer is None: return None
        except Exception:
            trace = log()
            if debug:
                stderr[0] << trace
            else:
                from ..assets import SAT_CRITICAL_ERROR
                print(SAT_CRITICAL_ERROR, file=sys.stderr)
            return None
        else:
            ## Output
            with stdout[0] as stream:
                if SatAPI.complete(answer):
                    x, e = answer
                    for var, val in x.items():
                        stream << f"{var}\t{val}" ## Variable choice
                    stream << f"E = {e}" ## Total energy for given configuration
                else: ## Partial Solution
                    stream << answer
        finally:
            if report: Timing.timer.show_report()