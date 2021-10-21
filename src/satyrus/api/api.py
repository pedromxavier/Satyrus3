"""
/satyrus/api/api.py
"""
# Future Imports
from __future__ import annotations

# Standard Library
import sys
import json
import shutil
import marshal
import traceback
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import final

# Third-Party
from cstream import stdwar, stderr, stdlog, DEBUG

# Local
from ..error import SatRuntimeError, EXIT_FAILURE, EXIT_SUCCESS
from ..satlib import Timing, Posiform, package_path, prompt
from ..satyrus import Satyrus


class SatFinder:
    """"""

    key: str = None
    require: dict = {}

    @classmethod
    def find_spec(cls, name: str, *__args, **__kwargs):
        if cls.key is not None:
            stdwar << f"Warning: missing module {name!r} for {cls.key!r}"
            if cls.key in cls.require:
                cls.require[cls.key].append(name)
            else:
                cls.require[cls.key] = [name]
        return None

    @classmethod
    def set_key(cls, key: str):
        cls.key = key


# -*- Register SatFinder -*- #
sys.meta_path.append(SatFinder)


class MetaSatAPI(ABCMeta):
    """"""

    base_class: MetaSatAPI = None
    __stack__: list[MetaSatAPI] = []
    __satapi__: dict[str, MetaSatAPI] = {}

    def __new__(cls, name: str, bases: tuple, namespace: dict):
        """"""
        if name == "SatAPI":
            if cls.base_class is None:
                cls.base_class = type.__new__(
                    cls,
                    name,
                    bases,
                    {
                        **namespace,
                        "__stack__": cls.__stack__,
                        "__satapi__": cls.__satapi__,
                    },
                )
                return cls.base_class
            else:
                raise NameError("'SatAPI' base class is already implemented")
        elif cls.base_class is None:
            raise NameError("'SatAPI' base class is not implemented yet")
        elif not cls.implements_solve(namespace):
            cls.base_class.error("'solve' method is not implemented")


        interface: MetaSatAPI = type.__new__(cls, name, bases, namespace)

        if name in cls.__satapi__:
            stdwar << f"API Interface '{name}' redefinition"
            cls.__stack__.append(name)
        elif name == "default":
            pass
        else:
            cls.__stack__.append(name)

        cls.__satapi__[name] = interface

        return cls.__satapi__[name]

    @classmethod
    def implements_solve(cls, namespace: dict):
        if 'solve' not in namespace:
            return False
        elif not callable(namespace['solve']):
            return False
        else:
            return True


class SatAPI(metaclass=MetaSatAPI):
    """"""

    __stack__: list = []
    __satapi__: dict = {}
    __satref__: dict = {}
    __loaded__: bool = False
    __energy__: Posiform = None

    ext: str = "out.txt"

    def __init__(self, *paths, guess: dict = None, legacy: bool = False):
        """"""
        if paths:
            try:
                energy: Posiform | None = Satyrus(legacy=legacy).compile(*paths)
            except SatRuntimeError as exc:
                stderr << exc
                energy: Posiform | None = None
        else:
            energy: Posiform | None = None

        if (energy is not None) and (guess is not None):
            energy = energy(guess)

        self.energy(energy)

    @classmethod
    def energy(cls, __energy: Posiform | None):
        cls.__energy__ = __energy

    @classmethod
    def extension(cls, name: str) -> str:
        if name in cls.__satapi__:
            return cls.__satapi__[name].ext
        else:
            return cls.ext

    def __getitem__(self, name: str):
        """"""

        self._load()

        if name in self.__satapi__:
            return self.__satapi__[name]

        if name not in self.__satref__:
            raise KeyError(f"Undefined API interface {name!r}")

        pack_path: Path = package_path()
        code_path: Path = pack_path.joinpath(self.__satref__[name])

        with code_path.open(mode="rb") as file:
            code = marshal.load(file)

        SatFinder.set_key(name)

        exec(code, {})

        SatFinder.set_key(None)

        if name not in self.__satapi__:
            raise KeyError("Defined API not in '__satapi__'")
        elif self.__satapi__[name] is None:
            modules: str = ", ".join(SatFinder.require[name])
            self.error(
                f"Interface {name!r} is unavailable due to missing modules: {modules}"
            )
        else:
            return self.__satapi__[name]

    @Timing.timer(level=DEBUG, section="Solver.solve")
    def __call__(self, **params) -> tuple[dict, float] | object:
        """"""

        if "$solver" not in params:
            raise KeyError("No solver specified")

        name: str = params["$solver"]

        if self.__energy__ is None:
            return None
        else:
            return self[name]().solve(self.__energy__, **params)

    @classmethod
    def __load__(cls):
        """"""

        data_path: Path = package_path(fname=".sat-api")

        if not data_path.exists() or data_path.is_dir():
            raise IOError("API metadata not found. Try reinstalling Satyrus")

        with data_path.open(mode="r", encoding="utf8") as file:
            data: dict = json.load(file)

        if data is None:
            cls._bootstrap()
        elif not isinstance(data, dict):
            raise IOError("API metadata is corrupted. Try reinstalling Satyrus")
        else:
            cls.__satref__.update(data)

        cls.__loaded__ = True

    @classmethod
    def _load(cls):
        if not cls.__loaded__:
            cls.__load__()

    @classmethod
    def _bootstrap(cls):
        """"""
        pack_path: Path = package_path()
        cls.add(*pack_path.glob("*.py"))

    @classmethod
    def add(cls, *paths: str):
        """\
        Includes new SatAPI interfaces given a separate Python file (``.py``)

        Parameters
        ----------
        *paths : tuple[str]
            Paths to Python files.
        """

        pack_path: Path = package_path()
        data_path: Path = pack_path.joinpath(".sat-api")

        with data_path.open(mode="r", encoding="utf8") as file:
            data: dict = json.load(file)

        if data is None:
            pass
        elif not isinstance(data, dict):
            raise IOError("API metadata is corrupted. Try reinstalling Satyrus")
        elif not all(isinstance(k, str) for k in data.keys()):
            raise IOError("API metadata is corrupted. Try reinstalling Satyrus")
        elif not all(isinstance(v, str) for v in data.values()):
            raise IOError("API metadata is corrupted. Try reinstalling Satyrus")
        else:
            cls.__satref__.update(data)

        for file_path in map(Path, paths):
            if not file_path.exists() or not file_path.is_file():
                stderr << f"Error: '{file_path}' does not exists"
                continue
            elif file_path.suffix != ".py":
                (
                    stderr
                    << f"Error: '{file_path.absolute()}' is not a valid Python file"
                )
                continue

            new_path = pack_path.joinpath(file_path.name)

            # Copy file to data folder
            try:
                shutil.copyfile(file_path, new_path)
            except shutil.SameFileError:
                # Everything is gonna be alright
                pass

            # Build
            try:
                answer: tuple[str, str] | None = cls._build(new_path)

                if answer is not None:
                    name, path = answer
                    cls.__satref__[name] = path
            finally:
                # Remove Source
                new_path.unlink()
        
        with data_path.open(mode="w", encoding="utf8") as file:
            json.dump(cls.__satref__, file)

    @classmethod
    def build(cls, *paths: str):
        """"""
        for file_path in map(Path, paths):
            cls._build(file_path)

    @classmethod
    def _build(cls, file_path: Path) -> tuple[str, str] | None:
        """ """
        if not file_path.exists() or not file_path.is_file():
            stderr << f"Error: '{file_path}' does not exists"
            return None
        elif file_path.suffix != ".py":
            stderr << f"Error: '{file_path.absolute()}' is not a valid Python file"
            return None

        with file_path.open(mode="r") as file:
            source: str = file.read()

        # Compile Interface definition
        code = compile(source, filename=file_path.name, mode="exec")

        try:
            exec(code, {})

            new: int = len(cls.__stack__)

            if new == 0:
                cls.warn(f"No new interfaces declared in '{file_path.name}'")
                return None
            elif new == 1:
                name: str = cls.__stack__.pop()

                if name == "default":
                    cls.error(
                        "You are not allowed to override the 'default' interface",
                        code=None,
                    )
                    return None
            else:
                cls.__stack__.clear()

                cls.error(
                    f"Rejected multiple interfaces declared in '{file_path.name}'",
                    code=None,
                )
                return None

        except Exception:
            stderr << f"There are errors in '{file_path.name}':"
            stderr << f"\n{traceback.format_exc(limit=-1)}\n"
            return None
        else:
            code_path = file_path.with_suffix(".pyc")

            with code_path.open(mode="wb") as file:
                marshal.dump(code, file)

            # Allow File Execution
            code_path.chmod(0o755)

            cls.log(f"Built '{file_path.name}'")

            return (name, code_path.name)

    @classmethod
    def remove(cls, *names: str, yes: bool = False):
        """"""
        cls._load()

        question = (
            f"This will remove {', '.join(names)}. Are you sure? (Y/n) ",
            {"Y": True, "n": False}
        )

        if yes or prompt(*question):
            for name in names:
                cls._remove(name)

        exit(EXIT_SUCCESS)    

    @classmethod
    def _remove(cls, name: str):
        """"""
        if name not in cls.options():
            cls.error(f"Unable to remove unknown interface {name!r}", code=None)
            return

        pack_path: Path = package_path()
        data_path: Path = pack_path.joinpath(".sat-api")
        code_path: Path = pack_path.joinpath(cls.__satref__[name])

        del cls.__satref__[name]

        with data_path.open(mode="w", encoding="utf8") as file:
            json.dump(cls.__satref__, file)

        code_path.unlink()


    @classmethod
    def clear(cls, yes: bool = False):
        """"""
        cls.remove(*cls.options(), yes=yes)

    @classmethod
    def options(cls) -> set[str]:
        cls._load()
        return set(cls.__satref__)

    @classmethod
    def complete(cls, answer: tuple[dict, float] | object) -> bool:
        """"""

        if isinstance(answer, tuple):
            if len(answer) == 2:
                if isinstance(answer[0], dict):
                    for k, v in answer[0].items():
                        if not isinstance(k, str):
                            return False
                        if not isinstance(v, int) or v not in {0, 1}:
                            return False
                else:
                    return False

                if isinstance(answer[1], float):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    @abstractmethod
    def solve(self, energy: Posiform, **params: dict) -> tuple[dict, float] | object:
        pass

    @staticmethod
    def error(message: str, code: int | None = EXIT_FAILURE):
        if stderr:
            stderr << f"API Error: {message}"
        if code is not None:
            exit(code)

    @staticmethod
    def warn(message: str, level: int = 1):
        if stdwar[level]:
            stdwar[level] << f"Warning: {message}"

    @staticmethod
    def log(message: str, level: int = 3):
        stdlog[level] << message


# -*- Default Interface -*-
class default(SatAPI):
    """"""

    ext = "json"

    def solve(self, energy: Posiform, indent: int | None = 4, **params: dict) -> str:
        """"""
        self.check_params(indent=indent)
        
        return energy.toJSON(indent=indent)

    def check_params(self, **params):
        """"""
        if "indent" in params:
            if params["indent"] is None:
                return
            elif not isinstance(params["indent"], int) or (params["indent"] < 0):
                self.error("Parameter 'indent' must be a non-negative integer")
