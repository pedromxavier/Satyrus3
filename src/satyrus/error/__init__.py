# Local
from ..satlib import Source

# Constants
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class SATError(Exception):
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
                return self.target.source.error(
                    self.msg, target=self.target, name=self.__doc__
                )
        else:
            return self.msg


class SATCompilerError(SATError):
    "Compiler Error"


class SATExprError(SATError):
    "Expression Error"


class SATIndexError(SATError):
    "Index Error"


class SATFileError(SATError):
    "File Error"


class SATLexerError(SATError):
    "Lexer Error"


class SATParserError(SATError):
    "Parser Error"


class SATPythonError(SATError):
    "Python Error"


class SATReferenceError(SATError):
    "Reference Error"


class SATRuntimeError(SATError):
    "Runtime Error"


class SATSyntaxError(SATError):
    "Syntax Error"


class SATTypeError(SATError):
    "Type Error"


class SATValueError(SATError):
    "Value Error"


class SATWarning(SATError):
    "Warning"


class SATSolverError(SATError):
    "Solver Error"


class SATExit(SATError):
    "Exit"

    def __init__(self, code: int):
        SATError.__init__(self, f"exit code {code}")


__all__ = [
    "EXIT_SUCCESS",
    "EXIT_FAILURE",
    "SATError",
    "SATCompilerError",
    "SATExprError",
    "SATIndexError",
    "SATFileError",
    "SATLexerError",
    "SATParserError",
    "SATPythonError",
    "SATReferenceError",
    "SATRuntimeError",
    "SATSyntaxError",
    "SATTypeError",
    "SATValueError",
    "SATWarning",
    "SATSolverError",
    "SATExit",
]
