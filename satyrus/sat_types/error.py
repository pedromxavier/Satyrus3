from satlib import stderr

class SatError(Exception):
    TITLE = 'Error'
    def __init__(self, msg=None, target=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.target = target

    def launch(self):
        if self.target is not None:
            stderr << f"""Error at line {self.target.lineno}:
            {self.target.source.lines[self.target.lineno]}
            {' ' * self.target.chrpos}^
            {self.TITLE}: {self.msg}"""
        else:
            raise self

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