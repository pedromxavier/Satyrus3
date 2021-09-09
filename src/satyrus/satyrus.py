# Standard Library
from pathlib import Path

# Local
from .error import SatCompilerError
from .satlib import Posiform, Source
from .compiler import SatCompiler
from .compiler.instructions import INSTRUCTIONS


class Satyrus:
    """\
    The highest-level compiler instance. This module aggregates both parser
    and compiler.
    """

    def __init__(self, path: str, *, legacy: bool = False, **params: dict):
        """\
        The highest-level compiler instance. This module aggregates both parser and compiler.
        """
        # Energy Function Compilation Status
        self.__ready__ = False

        # Source Code Path
        self.path = Path(path)

        if not self.path.exists() or not self.path.is_file():
            raise FileNotFoundError(f"Source File '{self.path}' does not exists")

        if legacy:
            from .parser.legacy import SatLegacyParser

            self.parser = SatLegacyParser()
        else:
            from .parser import SatParser

            self.parser = SatParser()

        self.compiler = SatCompiler(INSTRUCTIONS, self.parser)

        # Energy Function Posiform
        self.__energy__ = Posiform()

    def ready(self) -> bool:
        return self.__ready__

    def energy(self) -> Posiform:
        return self.__energy__

    def compile(self):
        self.__energy__ = self.compiler.compile(Source(fname=self.path))
        self.__ready__ = True

    