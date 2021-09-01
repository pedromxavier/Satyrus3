## Standard Library
import os

## Local
from cstream import stderr, stdout

class SatError(Exception):
    'Error'
    def __init__(self, msg=None, target=None, code=2):
        Exception.__init__(self, msg)
        self.msg = str(msg) if msg is not None else ""
        self.code = code
        self.target = target

    def __str__(self):
        if self.target is not None and hasattr(self.target, "lexinfo"):
            if self.target.source is None:
                return f"{self.__class__.__doc__}: {self.msg}\n"
            else:
                return self.target.source.error(self.msg, name=self.__doc__)
        else:
            return self.msg

class SatCompilerError(SatError):
	'Compiler Error'

class SatExprError(SatError):
    'Expression Error'

class SatIndexError(SatError):
    'Index Error'

class SatFileError(SatError):
    'File Error'

class SatLexerError(SatError):
    'Lexer Error'

class SatParserError(SatError):
    'Parser Error'

class SatPythonError(SatError):
    'Python Error'

class SatReferenceError(SatError):
	'Reference Error'

class SatSyntaxError(SatError):
    'Syntax Error'

class SatTypeError(SatError):
	'Type Error'

class SatValueError(SatError):
	'Value Error'

class SatWarning(SatError):
    'Warning'

class SatExit(SatError):
    'Exit'

    def __init__(self, code: int):
        SatError.__init__(self, f'exit code {code}')