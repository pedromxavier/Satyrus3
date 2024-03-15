# Standard Library
import os

# Third-Party
from cstream import stderr, stdout

# Local
from ..satlib import Source

# Constants
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class SatError(Exception):
    "Error"

    def __init__(self, msg=None, target=None, code=EXIT_FAILURE):
        Exception.__init__(self, msg)
        self.msg = str(msg) if msg is not None else ""
        self.code = code
        self.target = target

    def __str__(self) -> str:
        if Source.trackable(self.target):
            if self.target.source is None:
                return f"{self.__class__.__doc__}: {self.msg}\n"
            else:
                return self.target.source.error(self.msg, target=self.target, name=self.__doc__)
        else:
            return self.msg


class SatCompilerError(SatError):
    "Compiler Error"


class SatExprError(SatError):
    "Expression Error"


class SatIndexError(SatError):
    "Index Error"


class SatFileError(SatError):
    "File Error"


class SatLexerError(SatError):
    "Lexer Error"


class SatParserError(SatError):
    "Parser Error"


class SatPythonError(SatError):
    "Python Error"


class SatReferenceError(SatError):
    "Reference Error"

class SatRuntimeError(SatError):
    "Runtime Error"

class SatSyntaxError(SatError):
    "Syntax Error"


class SatTypeError(SatError):
    "Type Error"


class SatValueError(SatError):
    "Value Error"


class SatWarning(SatError):
    "Warning"


class SatSolverError(SatError):
    "Solver Error"


class SatExit(SatError):
    "Exit"

    def __init__(self, code: int):
        SatError.__init__(self, f"exit code {code}")


__all__ = [
    "EXIT_SUCCESS",
    "EXIT_FAILURE",
    "SatError",
    "SatCompilerError",
    "SatExprError",
    "SatIndexError",
    "SatFileError",
    "SatLexerError",
    "SatParserError",
    "SatPythonError",
    "SatReferenceError",
    "SatRuntimeError",
    "SatSyntaxError",
    "SatTypeError",
    "SatValueError",
    "SatWarning",
    "SatSolverError",
    "SatExit",
]
