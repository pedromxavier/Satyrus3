"""\
Satyrus Compiler v{version}
"""
from __future__ import annotations

__version__ = "3.0.8"

## Standard Library
import argparse
import json
from pathlib import Path
from functools import wraps
from gettext import gettext

## Third-Party
from cstream import Stream, stdlog, stdwar, stderr, stdout

## Local
from .help import satyrus_help
from ..api import SatAPI
from ..error import EXIT_SUCCESS, EXIT_FAILURE
from ..assets import SAT_BANNER, SAT_CRITICAL
from ..satlib import Timing, log
from ..satyrus import Satyrus


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

        (
            stdout[0]
            << f"satyrus {__version__} (python {version_info.major}.{version_info.minor})"
        )
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


class DebugMode(argparse._StoreTrueAction):
    @wraps(argparse._StoreTrueAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreTrueAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(1)
    @wraps(argparse._StoreTrueAction.__call__)
    def __call__(self, parser, namespace, values, option_string=None):
        argparse._StoreTrueAction.__call__(
            self, parser, namespace, values, option_string
        )
        setattr(namespace, "verbose", 3)
        Stream.set_lvl(3)


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
            parser.error(
                f"Invalid solver choice '{solver}' (choose from {SatAPI.options()!r})"
            )


class readParams(argparse._StoreAction):
    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(4)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser: ArgParser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        params = getattr(namespace, self.dest)

        if params is None:
            stdwar[1] << "Warning: No solver parameters passed"
            setattr(namespace, self.dest, {})

        params_path = Path(params)

        params: dict = load_json(parser, params_path)

        if isinstance(params, dict):
            setattr(namespace, self.dest, params)
        else:
            parser.error(
                f"In '{params_path}':\nParameter object must be mapping, not '{type(params)}'"
            )

class readGuess(argparse._StoreAction):
    @wraps(argparse._StoreAction.__init__)
    def __init__(self, *args, **kwargs):
        argparse._StoreAction.__init__(self, *args, **kwargs)

    @ArgParser.enqueue(4)
    @wraps(argparse._StoreAction.__call__)
    def __call__(self, parser: ArgParser, namespace, values, option_string=None):
        argparse._StoreAction.__call__(self, parser, namespace, values, option_string)
        
        guess_path = Path(getattr(namespace, self.dest))

        guess: dict = load_json(parser, guess_path)

        if guess is None:
            stdwar[1] << "Warning: No solver guess given"
        elif not isinstance(guess, dict):
            parser.error(
                f"In '{guess_path}':\nGuess object must be mapping, not '{type(guess)}'"
            )
        elif not all(v in {0, 1} for v in guess.values()):
            parser.error(f"In '{guess_path}':\nGuess values must be of type Number (Python int) and binary (0 or 1) ")
        elif not all(isinstance(k, str) for k in guess):
            parser.error(f"In '{guess_path}':\nGuess keys must be variables of type String (Python str)")

        setattr(namespace, self.dest, guess)

class SatCLI:
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
    def infer_output(
        cls,
        ext: str,
        args: argparse.Namespace,
        answer: tuple[dict, float] | str | object,
    ) -> tuple[str, str]:
        if answer is None:
            exit(EXIT_FAILURE)

        if SatAPI.complete(answer):
            answer = json.dumps({"solution": answer[0], "energy": answer[1]}, indent=4)
            output = f"{Path(args.source[0]).stem}.out.json"
        else:
            answer = str(answer)
            output = f"{Path(args.source[0]).stem}.{ext}"

        if args.output is not None:
            output = args.output

        return output, answer

    @classmethod
    def run(cls, argv: list = None):
        """ """

        # -*- Set base output verbosity level -*-
        Stream.set_lvl(1)

        # -*- Load Interfaces -*-
        SatAPI._load()

        parser = ArgParser(
            prog="satyrus", description=__doc__.format(version=__version__)
        )

        ## Mandatory - Source file path
        parser.add_argument("source", help=satyrus_help("source"), nargs="+")

        # Optional - Compiler Version
        parser.add_argument(
            "--version", help=satyrus_help("version"), action=GetVersion
        )

        ## Optional - Compiler Verbosity
        parser.add_argument(
            "-v",
            "--verbose",
            type=int,
            dest="verbose",
            choices=[0, 1, 2, 3],
            default=1,
            help=satyrus_help("verbose"),
            action=SetVerbosity,
        )

        # Optional - Debug Mode
        parser.add_argument(
            "-d", "--debug", dest="debug", help=argparse.SUPPRESS, action=DebugMode
        )

        # Optional - Solver Option
        parser.add_argument(
            "-s",
            "--solver",
            type=str,
            dest="solver",
            help=satyrus_help("solver"),
            default="default",
            action=SetSolver,
        )

        # Optional - Solver Option
        parser.add_argument(
            "-c",
            "--clear",
            dest="clear",
            help=satyrus_help("clear"),
            action="store_true",
        )

        # Optional - Output File
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            dest="output",
            help=satyrus_help("output"),
            action="store",
        )

        # Optional - Legacy Syntax
        parser.add_argument(
            "-l",
            "--legacy",
            dest="legacy",
            action="store_true",
            help=satyrus_help("legacy"),
        )

        # Optional - Timing Report
        parser.add_argument(
            "-r",
            "--report",
            dest="report",
            action="store_true",
            help=satyrus_help("report"),
        )

        # Optional - Solver parameters
        parser.add_argument(
            "-p",
            "--params",
            dest="params",
            help=satyrus_help("params"),
            action=readParams,
        )

        # Optional - Augmented API
        parser.add_argument(
            "-g", "--guess", dest="guess", help=satyrus_help("guess"), action=readGuess
        )

        if argv is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(argv)

        # Exhibits Compiler Command line arguments
        stdlog[
            3
        ] << f'Command line args:\n{";".join(f"{k}={v!r}" for k, v in vars(args).items())}'

        # Warning: Debug mode
        if args.debug:
            stdwar[1] << "Warning: Debug mode enabled."

        # Warning: Legacy mode
        if args.legacy:
            stdwar[1] << "Warning: Parser is running in legacy mode."

        # Waning: Clear Cache
        if args.clear:
            Satyrus.clear_cache()
            stdwar[1] << "Warning: Cache Cleared."

        try:
            # Launch API
            api = SatAPI(*args.source, guess=args.guess, legacy=args.legacy)

            # Solve in desired way
            if args.params is None:
                params = {"$solver": args.solver}
            else:
                params = {"$solver": args.solver, **args.params}

            answer: tuple[dict, float] | str | object = api(**params)

            ext: str = api.extension(args.solver)

            # Retrieve Output Destination
            args.output, answer = cls.infer_output(ext, args, answer)

            with open(args.output, mode="w", encoding="utf8") as file:
                file.write(answer)

            # Report
            if args.report:
                Timing.timer.show_report(level=0)

            exit(EXIT_SUCCESS)
        except MemoryError as exc:
            stderr[0] << exc
            exit(EXIT_FAILURE)
        except RuntimeError as exc:
            stderr[0] << exc
            exit(EXIT_FAILURE)
        except Exception:
            trace = log(target="satyrus.log")
            if args.debug:
                stderr[0] << trace
            else:
                stderr[0] << SAT_CRITICAL
            exit(EXIT_FAILURE)


__all__ = ["SatCLI"]
