from .types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT
from .compiler.stmt import sys_config, def_constant, def_array, def_constraint
from .compiler import SatCompiler
from .api import SatAPI

class Satyrus(object):

    instructions = {
        SYS_CONFIG : sys_config,
        DEF_CONSTANT : def_constant,
        DEF_ARRAY : def_array,
        DEF_CONSTRAINT : def_constraint
    }

    def __init__(self, source_path: str):
        self.source = source_path
        self.compiler = SatCompiler(self.instructions)

        self.problem = self.compiler.compile(self.source)

        self.api = SatAPI(self.problem)

        print(self.api['text'])