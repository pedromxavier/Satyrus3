# Future Imports
from __future__ import annotations

# Standard Library
import json
from pathlib import Path

# Third-Party
from cstream import stderr

# Local
from ..error import SatRuntimeError, EXIT_SUCCESS, EXIT_FAILURE
from ..satlib import Source, Posiform, package_path
from ..compiler import SatCompiler
from ..compiler.instructions import INSTRUCTIONS
from ..parser import SatParser
from ..parser.legacy import SatLegacyParser


class Satyrus(object):
    """
    Compiler flow diagram
    ---------------------

    ┌───────────┐
    │source.sat ├──┐
    └───────────┘  │
                   │
          .        │    ┌────────┐
          .        ├────►Satyrus3│      ┌───────────┐
          .        ├────►(Python)├──────►energy.json│
                   │    └────────┘      └───────────┘
    ┌───────────┐  │
    │energy.json├──┘
    └───────────┘
    """

    __cache_path__ = None

    def __init__(self, legacy: bool = False):
        """
        Parameters
        ----------
        legacy : bool (optional)
            If true, opts for the legacy parser and its syntax.
        """

        # Choose parser
        if legacy:
            self.parser = SatLegacyParser()
        else:
            self.parser = SatParser()

        # Start Compiler Engine
        self.compiler = SatCompiler(INSTRUCTIONS, self.parser)

        # Compilation Cache
        self.__cache__ = {}

    @staticmethod
    def _path(path: Path) -> str:
        """"""
        return str(path.absolute())

    @staticmethod
    def _stat(path: Path) -> float:
        """"""
        return path.stat().st_mtime

    @staticmethod
    def _stamp(path: Path) -> tuple[str, float]:
        """"""
        return (Satyrus._path(path), Satyrus._stat(path))

    def compile(self, *paths: str | Path) -> Posiform | None:
        """"""
        if not all(isinstance(path, (str, Path)) for path in paths):
            raise TypeError("File paths must be of type 'str' or 'pathlib.Path'")
        else:
            return self.__compile(*paths)

    def __compile(self, *paths: str) -> Posiform | None:
        """"""
        if not paths:
            raise IOError("No input files provided")
        else:
            # Status Code
            code = EXIT_SUCCESS

            # Load Cache
            self.load_cache()

            # Empty Energy Equation
            source_list: list[Path] = []
            energy_list: list[Path] = []

            for path in paths:
                path = Path(path)
                if not path.exists() or not path.is_file():
                    stderr << f"Error: File '{path}' does not exists"
                    code |= EXIT_FAILURE
                elif path.suffix == ".sat":
                    source_list.append(path)
                elif path.suffix == ".json":
                    energy_list.append(path)
                else:
                    stderr << f"Error: Invalid file extension '{path.suffix}'"
                    code |= EXIT_FAILURE

            total_energy = Posiform(None)

            for energy_path in energy_list:
                if not self.cached(energy_path):
                    with energy_path.open(mode="r") as energy_file:
                        try:
                            energy = Posiform.fromJSON(energy_file.read())
                        except json.decoder.JSONDecodeError:
                            stderr << f"Error: Inconsistent JSON data for energy equation in '{energy_path}'"
                            code |= EXIT_FAILURE
                        else:
                            total_energy += self.cache(energy_path, energy)
                else:
                    total_energy += self.cache(energy_path)

            for source_path in source_list:
                if not self.cached(source_path):
                    if self.compiler.compile(Source(fname=source_path)):
                        code |= EXIT_FAILURE
                    else:
                        total_energy += self.cache(source_path, self.compiler.energy)
                else:
                    total_energy += self.cache(source_path)

            self.write_cache()

            if not code:
                return total_energy
            else:
                raise SatRuntimeError("Compilation terminated with errors")

    # -*- Cache -*-
    def cache(self, path: Path, energy: Posiform | None = None) -> Posiform:
        if energy is None:
            return Posiform.fromMiniJSON(self.__cache__[self._path(path)]["energy"])
        else:
            self.__cache__[self._path(path)] = {"stat": self._stat(path), "energy": energy.toMiniJSON()}
            return energy

    def cached(self, path: Path) -> bool:
        key = self._path(path)
        return (key in self.__cache__) and (self.__cache__[key]["stat"] == self._stat(path))

    @classmethod
    def cache_path(cls) -> Path:
        if cls.__cache_path__ is None:
            cls.__cache_path__ = package_path(fname='.satyrus')
        return cls.__cache_path__
        

    def load_cache(self):
        if self.cache_path().exists() and self.cache_path().is_file():
            with self.cache_path().open(mode="r") as file:
                self.__cache__ = json.load(file)
                if self.__cache__ is None:
                    self.__cache__ = {}
        elif not self.cache_path().exists():
            with self.cache_path().open(mode="w") as file:
                json.dump(None, file)
                self.__cache__ = {}
        else:
            raise RuntimeError(f"Unable to load file '{self.cache_path()}'")

    def write_cache(self):
        with self.cache_path().open(mode="w") as file:
            if self.__cache__:
                json.dump(self.__cache__, file)
            else:
                json.dump(None, file)

    @classmethod
    def clear_cache(cls):
        with cls.cache_path().open(mode="w") as file:
            json.dump({}, file)


__all__ = ["Satyrus"]
