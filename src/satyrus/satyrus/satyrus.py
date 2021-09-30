# Future Imports
from __future__ import annotations

# Standard Library
from pathlib import Path

# Third-Party
from cstream import Stream

# Local
from ..satlib import Source, Posiform
from ..compiler import SatCompiler
from ..compiler.instructions import instructions
from ..parser.legacy import SatLegacyParser


class Satyrus:
    def __init__(self, *paths: str, legacy: bool = False):
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

        if not paths:
            raise ValueError("No input files provided.")
        else:
            energy = Posiform(0.0)
            sources = []
            for path in paths:
                path = Path(path)
                if not path.exists() or not path.is_file():
                    raise FileNotFoundError(f"File '{path}' does not exists")
                elif path.suffix == ".sat":
                    self.sources.append(Source(path))
                elif path.suffix == ".json":
                    pass

            for source in sources:
                pass

        self.compiler = SatCompiler(instructions, parser=self.parser, env=self.env)
        self.compiler.compile(self.source)

    @property
    def output(self):
        return self.compiler.output

    @property
    def code(self):
        return self.compiler.code


__all__ = ["Satyrus"]
