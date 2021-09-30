"""\
Satyrus Compiler v{version}
"""
from __future__ import annotations

__version__ = "3.0.5    "

## Standard Library
import argparse
import json
from pathlib import Path
from functools import wraps
from gettext import gettext

## Third-Party
from cstream import Stream, stdlog, stdwar, stderr, stdout

## Local
from .help import HELP
from ..api import SatAPI
from ..assets import SAT_BANNER, SAT_CRITICAL
from ..satlib import Timing, log

def load_json(parser, path: Path) -> object:
    if not path.exists() or not path.is_file():
            parser.error(f"File '{path}' doesn't exists")

    with path.open(mode="r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            parser.error(f"In '{path}':\n{error.msg}")
        else:
            return data

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

    def print_help(self, from_help: bool = True):
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
        exit(0)

class SetVerbosity(argparse._StoreAction):
    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(0)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        Stream.set_lvl(getattr(namespace, self.dest))


class DebugMode(argparse._StoreTrueAction):
    @wraps(argparse._StoreTrueAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreTrueAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(1)
    @wraps(argparse._StoreTrueAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreTrueAction.__call__(self, parser, namespace, values, option_string)
        setattr(namespace, "verbose", 3)
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
            SatAPI.include(str.strip(fname))


class SetSolver(argparse._StoreAction):
    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(3)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser: ArgParser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        solver = str.strip(getattr(namespace, self.dest))
        if solver not in SatAPI.options():
            parser.error(f"Invalid solver choice '{solver}' (choose from {SatAPI.options()!r})")


class readParams(argparse._StoreAction):
    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(4)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser: ArgParser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        params = getattr(namespace, self.dest)

        print("PARAMS:", params)

        if params is None:
            stdwar[1] << "Warning: No solver parameters passed."
            setattr(namespace, self.dest, {})

        params_path = Path(params)

        
        if isinstance(params, dict):
            setattr(namespace, self.dest, params)
        else:
            parser.error(f"In '{params_path}':\nParameter object must be mapping, not '{type(params)}'")


class CLI:
    """Satyrus command line interface.

    Example
    -------
    >>> CLI.run(["--help"])
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

        parser = ArgParser(prog="satyrus", description=__doc__.format(version=__version__))

        ## Mandatory - Source file path
        parser.add_argument("source", help=HELP["source"])

        # Optional - Compiler Version
        parser.add_argument("--version", help=HELP["version"], action=GetVersion)

        ## Optional - Compiler Verbosity
        parser.add_argument(
            "-v",
            "--verbose",
            type=int,
            dest="verbose",
            choices=[0, 1, 2, 3],
            default=1,
            help=HELP["verbose"],
            action=SetVerbosity,
        )

        # Optional - Debug Mode
        parser.add_argument("-d", "--debug", dest="debug", help=argparse.SUPPRESS, action=DebugMode)

        # Optional - Augmented API
        parser.add_argument("-a", "--api", type=str, dest="api", help=HELP["api"], action=IncludeSatAPI)

        # Optional - Solver Option
        parser.add_argument(
            "-s",
            "--solver",
            type=str,
            dest="solver",
            help=HELP["solver"],
            action=SetSolver,
        )

        # Optional - Output File
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            dest="output",
            help=HELP["output"],
            action="store",
        )

        # Optional - Legacy Syntax
        parser.add_argument("-l", "--legacy", dest="legacy", action="store_true", help=HELP["legacy"])

        # Optional - Timing Report
        parser.add_argument("-r", "--report", dest="report", action="store_true", help=HELP["report"])

        # Optional - Solver parameters
        parser.add_argument("-p", "--params", dest="params", help=HELP["params"], action=readParams)

        # Set base output verbosity level
        Stream.set_lvl(1)

        if argv is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(argv[1:])

        # Exhibits Compiler Command line arguments
        stdlog[3] << f"Command line args:"
        for k, v in vars(args).items():
            stdlog[3] << f"\t{k}={v!r}"

        ## Debug mode
        debug: bool = args.debug

        if debug:
            stdwar[1] << f"Warning: Debug mode enabled."

        ## Legacy mode
        legacy: bool = args.legacy

        if legacy:
            stdwar[1] << f"Warning: Parser is in legacy mode."

        # Performance Report
        report: bool = args.report

        # Solver Interface
        if args.solver is None:
            solver = "text"
        else:
            solver = args.solver

        # Solvers Parameters
        if args.params is None:
            params = {}
        else:
            params = args.params

        try:
            # Launch API
            sat_api = SatAPI(path=Path(args.source), legacy=legacy)

            # Solve in desired way
            answer: tuple[dict, float] | str = sat_api[solver].solve(**params)

            # Failure
            if answer is None:
                stderr[0] << "Error:"
                exit(1)
            elif SatAPI.complete(answer):
                answer = json.dumps({"solution": answer[0], "energy": answer[1]}, indent=4)

        except Exception:
            trace = log(target="satyrus.log")
            if debug:
                stderr[0] << trace
            else:
                stderr[0] << SAT_CRITICAL
            exit(1)

__all__ = ["CLI"]
