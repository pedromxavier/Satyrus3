
## Local
from ..satlib import Source

from .compiler import SatCompiler

from .types.symbols import DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT, SYS_CONFIG
from .compiler.stmt import def_constant, def_array, def_constraint, sys_config

class Satyrus:

    instructions = {
        DEF_CONSTANT: def_constant,
        DEF_ARRAY: def_array,
        DEF_CONSTRAINT: def_constraint,
        SYS_CONFIG: sys_config
    }

    def __init__(self, source_path: str):
        """
        """
        self.compiler = SatCompiler(self.instructions)

        self.source = Source(source_path)

        self.compiler.compile(self.source)