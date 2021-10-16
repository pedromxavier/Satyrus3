"""\
Satyrus API v{version}
"""
from __future__ import annotations

__version__ = "3.0.8"

## Standard Library
import argparse
from functools import wraps
from gettext import gettext

## Third-Party
from cstream import Stream, stdlog, stderr, stdout

## Local
from .help import sat_api_help
from ..api import SatAPI
from ..error import EXIT_SUCCESS
from ..assets import SAT_BANNER

class ArgParser(argparse.ArgumentParser):
    @wraps(argparse.ArgumentParser.__init__)
    def __init__(self, *args, **kwargs):
        self._rank = {}
        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    @wraps(argparse.ArgumentParser.parse_args)
    def parse_args(self, args: list = None, namespace: argparse.Namespace = None):
        args = argparse.ArgumentParser.parse_args(self, args, namespace)

        for p in sorted(self._rank.keys()):
            for action, params in self._rank[p]:
                action(*params)

        return args

    def print_help(self, *, from_help: bool = True):
        if from_help:
            stdlog[0] << SAT_BANNER
        argparse.ArgumentParser.print_help(self, stdlog[0])

    def error(self, message: str, code: int = 1):
        stderr << f"Error: {gettext(message)}"
        self.print_help(from_help=False)
        exit(code)

    @classmethod
    def enqueue(cls, priority: int = 0):
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

class GetVersion(argparse._VersionAction):
    @wraps(argparse._VersionAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._VersionAction.__init__(self, *args, **kwargs)

    @wraps(argparse._VersionAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        from sys import version_info

        stdout[0] << f"satyrus {__version__} (python {version_info.major}.{version_info.minor})"
        exit(EXIT_SUCCESS)

class SetVerbosity(argparse._StoreAction):
    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(0)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        Stream.set_lvl(getattr(namespace, self.dest))

def addSatAPI(args: argparse.Namespace):
    SatAPI.add(*args.path)

def buildSatAPI(args: argparse.Namespace):
    SatAPI.build(*args.path)

def removeSatAPI(args: argparse.Namespace):
    SatAPI.remove(*args.name, yes=args.yes)

def clearSatAPI(args: argparse.Namespace):
    SatAPI.clear(yes=args.yes)
        
class SatAPICLI:
    r"""
      Satyrus Stack
      ┌───────────┐
    │ │  SatCLI   │
    │ ├───────────┤
    │ │  SatAPI   │
    │ ├───────────┤
    │ │  Satyrus  │
    │ ├───────────┤
    │ │SatCompiler│
    │ ├───────────┤
    ▼ │ SatParser │
      └───────────┘
    """

    @classmethod
    def run(cls, argv: list = None):
        """
        Parameters
        ----------

        source : str
            Path to source code.
        -o, --out : str
            Output Destination.
        --legacy : bool
            If True, uses the legacy parser.
        -v, --verbose : int
            Compiler verbosity level.
        -d, --debug : bool
            If True, enables debug mode.
        -a, --api : str
            If present, include solver interfaces defined in python file.
        -p, --params : str
            Path to JSON file containing parameters for passing to Solver API.
        """

        parser = ArgParser(prog="sat-api", description=__doc__.format(version=__version__))
        parser.set_defaults(func=None)

        # Optional - Compiler Version
        parser.add_argument("--version", help=sat_api_help("version"), action=GetVersion)

        # Optional - Compiler Verbosity
        parser.add_argument(
            "-v",
            "--verbose",
            type=int,
            dest="verbose",
            choices=[0, 1, 2, 3],
            default=1,
            help=sat_api_help("verbose"),
            action=SetVerbosity,
        )

        # -*- Subparsers -*-
        subparsers = parser.add_subparsers()

        add_parser = subparsers.add_parser("add")
        add_parser.add_argument("path", help=sat_api_help("add"), nargs="+")
        add_parser.set_defaults(func=addSatAPI)

        build_parser = subparsers.add_parser("build")
        build_parser.add_argument("path", help=sat_api_help("build"), nargs="+")
        build_parser.set_defaults(func=buildSatAPI)

        remove_parser = subparsers.add_parser("remove")
        remove_parser.add_argument("name", help=sat_api_help("remove"), nargs="+")
        remove_parser.add_argument("-y", "--yes", help=sat_api_help("yes"), action="store_true")
        remove_parser.set_defaults(func=removeSatAPI)

        clear_parser = subparsers.add_parser("clear")
        clear_parser.add_argument("-y", "--yes", help=sat_api_help("yes"), action="store_true")
        clear_parser.set_defaults(func=clearSatAPI)

        # -*- Set base output verbosity level -*-
        Stream.set_lvl(1)

        if argv is None:
            args: argparse.Namespace = parser.parse_args()
        else:
            args: argparse.Namespace = parser.parse_args(argv)

        # -*- Load Interfaces -*-
        SatAPI._load()

        # Exhibits Compiler Command line arguments
        stdlog[3] << f'Command line args:\n{";".join(f"{k}={v!r}" for k, v in vars(args).items())}'

        if args.func is None:
            stdout[1] << "Available Interfaces:"
            for (i, option) in enumerate(SatAPI.options(), start=1):
                stdout[1] << f"{i}. {option}"
        else:
            args.func(args)
        
        exit(EXIT_SUCCESS)
        
__all__ = ["SatAPICLI"]
