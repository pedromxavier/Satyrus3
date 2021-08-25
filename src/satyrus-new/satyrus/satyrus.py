
from cstream import Stream

## Local
from ..satlib import Source
from ..compiler import SatCompiler
from ..compiler.instructions import instructions


from ..parser.legacy import SatLegacyParser

## Disable unecessary output
Stream.set_lvl(0)

class Satyrus:

    def __init__(self, source_path: str, legacy: bool=False, opt: int=0):
        """
        Parameters
        ----------
        source_path : str
            ``.sat`` file destination.
        legacy : bool
            If true, opts for the legacy parser and its syntax.
        """
        # Optimizations are not enabled yet.

        ## Choose parser
        if legacy:

            self.parser = SatLegacyParser()
        else:
            from ..parser import SatParser
            self.parser = SatParser()

        self.source = Source(source_path)

        self.compiler = SatCompiler(instructions, parser=self.parser, env=self.env)
        self.compiler.compile(self.source)

    @property
    def output(self):
        return self.compiler.output

    @property
    def code(self):
        return self.compiler.code