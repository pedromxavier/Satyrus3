
## Local
from ..satlib import Source, stream

from .compiler import SatCompiler

from .types.symbols import DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT, SYS_CONFIG
from .compiler.instructions import instructions

class Satyrus:

    def __init__(self, source_path: str, legacy: bool=False, O: int=0):
        """
        """
        
        ## import parser
        if legacy:
            from .parser.legacy import SatLegacyParser as Parser
            
        else:
            from .parser import SatParser as Parser

        self.O = O

        self.parser = Parser()

        self.compiler = SatCompiler(instructions, parser=self.parser, O=O)

        self.source = Source(source_path)

        self.compiler.compile(self.source)
        
        self.results = self.compiler.results

    def __call__(self):
        """ sat() -> dict
        """
        return self.results