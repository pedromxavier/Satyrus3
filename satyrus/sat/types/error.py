## Standard Library
import os

## Local
from ...satlib import stderr, stdout

class SatError(Exception):
    'Error'
    def __init__(self, msg=None, target=None):
        Exception.__init__(self, msg)
        self.msg = str(msg) if msg is not None else ""
        self.target = target

    def __str__(self):
        if self.target is not None and hasattr(self.target, 'lexinfo'):
            return (
                f"In '{os.path.abspath(self.target.source.fname)}' at line {self.target.lineno}:\n"
                f"{self.target.source.lines[self.target.lineno]}\n"
                f"{' ' * self.target.chrpos}^\n"
                f"{self.__class__.__doc__}: {self.msg}\n"
            )
        else:
            return self.msg

class SatWarning(SatError):
    'Warning'
##
class SatIndexError(SatError):
    'Index Error'
    
class SatCompilerError(SatError):
	'Compiler Error'

class SatValueError(SatError):
	'Value Error'

class SatTypeError(SatError):
	'Type Error'

class SatReferenceError(SatError):
	'Reference Error'

class SatParserError(SatError):
    'Parser Error'

class SatLexerError(SatError):
    'Lexer Error'

class SatSyntaxError(SatError):
    'Syntax Error'

class SatPythonError(SatError):
    'Python Error'

class SatExit(SatError):
    'Exit'

    def __init__(self, code: int):
        self.code = code
        SatError.__init__(self, f'exit code {code}')
