
## Local
from ..satlib import Source, stream

from .compiler import SatCompiler

from .types.symbols import DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT, SYS_CONFIG
from .compiler.instructions import instructions

class Satyrus:

    def __init__(self, source_path: str):
        """
        """
        stream.set_lvl(None)

        self.compiler = SatCompiler(instructions)

        self.source = Source(source_path)

        self.compiler.compile(self.source)
        
        self.results = self.compiler.results