
## Local
from .satlib import Source, Stream

from .compiler import SatCompiler

from .types.symbols import DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT, SYS_CONFIG
from .types.symbols import OPT
from .compiler.instructions import instructions

class Satyrus:

    def __init__(self, source_path: str, legacy: bool=False, opt: int=0):
        """
        """
        
        ## Omport parser
        if legacy:
            from .parser.legacy import SatLegacyParser as Parser
        else:
            from .parser import SatParser as Parser

        self.env = {
            OPT: opt,
        }

        self.parser = Parser()

        self.compiler = SatCompiler(instructions, parser=self.parser, env=self.env)

        self.source = Source(source_path)

        self.compiler.compile(self.source)

    @property
    def results(self):
        return self.compiler.results

    @property
    def code(self):
        return self.compiler.code