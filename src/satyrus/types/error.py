## Local
from satlib import stderr, stdout

class SatError(Exception):
    TITLE = 'Error'
    def __init__(self, msg=None, target=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.target = target

    def __str__(self):
        if self.target is not None:
            return (
                f"In '{self.target.source.fname}' at line {self.target.lineno}:"
                f"{self.target.source.lines[self.target.lineno]}"
                f"{' ' * self.target.chrpos}^"
                f"{self.TITLE}: {self.msg}"
            )
        else:
            return self.msg

class SatWarning(SatError):
    TITLE = 'Warning'

##
class SatIndexError(SatError):
    TITLE = 'Index Error'
    
class SatCompilerError(SatError):
	TITLE = 'Compiler Error'

class SatValueError(SatError):
	TITLE = 'Value Error'

class SatTypeError(SatError):
	TITLE = 'Type Error'

class SatReferenceError(SatError):
	TITLE = 'Reference Error'

class SatParserError(SatError):
    TITLE = 'Parser Error'

class SatLexerError(SatError):
    TITLE = 'Lexer Error'

class SatSyntaxError(SatError):
    TITLE = 'SyntaxError'

class SatExit(SatError):
    TITLE = 'Exit'

    def __init__(self, code: int):
        self.code = code
        SatError.__init__(self, f'exit code {code}')
