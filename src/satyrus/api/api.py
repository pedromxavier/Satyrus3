"""\
satyrus/api/api.py
------------------
"""
# Future Imports
from __future__ import annotations

# Standard Library
from abc import abstractmethod

# Third-Party

# Local
from ..satyrus import Satyrus
from ..satlib import Posiform


class MetaSatAPI(type):
    """"""

    BASE_CLASS = "SatAPI"
    base_class = None
    subclasses = {}

    def __new__(cls, name: str, bases: tuple, namespace: dict):
        """"""
        if name == cls.BASE_CLASS:
            if cls.base_class is None:
                cls.base_class = type.__new__(
                    cls, name, bases, {**namespace, "subclasses": cls.subclasses}
                )
                return cls.base_class
            else:
                raise NameError("'SatAPI' base class is already implemented.")
        elif name in cls.subclasses:
            raise NameError(f"API Interface '{name}' is already defined.")
        elif cls.base_class is None:
            raise NameError("'SatAPI' base class is not implemented yet.")
        elif "solve" not in namespace:
            raise NotImplementedError(
                f"Method solve(self, posiform: Posiform, **params: dict) -> tuple[dict, float] | object must be implemented for '{name}'."
            )
        else:
            cls.subclasses[name] = type.__new__(cls, name, bases, namespace)
            return cls.subclasses[name]


class SatAPI(metaclass=MetaSatAPI):

    subclasses = {}

    @abstractmethod
    def solve(self, posiform: Posiform, **params: dict) -> tuple[dict, float] | object:
        pass

    def __init__(self, source_path: str, **params: dict):
        """\
        Parameters
        ----------

        source_path : str
            Path to ``.sat`` source code file.
        **kwargs : dict
            Keyword arguments for compiler.

        To define a new interface one must write, in a separate Python file (``.py``, ``.pyw``), a ``SatAPI`` subclass that implements the ``_solve(self, posiform: Posiform) -> {(dict, float), object}`` method.

        There are two types of interface: partial and complete. Complete ones must return a ``tuple`` containing a ``dict`` (mapping between variables and binary state) and a ``float`` (total energy for the given configuration). Any implementation that does not return as specified by this signature will be considered partial, leading to its output being returned as in string formating.

        Example
        -------
        As found in ``examples/myapi.py``::

            class MyPartialAPI(SatAPI):

                def solve(self, posiform: Posiform) -> object:
                    info = get_information(posiform)
                    return info

            class MyCompleteAPI(SatAPI):

                def solve(self, posiform: Posiform) -> tuple[dict, float]:
                    x = get_solution(posiform)
                    e = get_energy(posiform)
                    return (x, e)

        Note
        ----
        It is not necessary to import SatAPI in this case.
        
        """
        self.satyrus = Satyrus(source_path, **params)

    def __getitem__(self, key: str):
        if key in self.subclasses:
            return self.subclasses[key](source_path=self.source_path, **self.kwargs)
        else:
            raise NotImplementedError(
                f"Unknown solver interface `{key}`. Available options are: {set(self.options)}"
            )

    @classmethod
    def options(cls) -> set:
        return set(cls.subclasses.keys())

# NOTE: DO NOT EDIT ABOVE THIS LINE
# ---------------------------------

# Text Output
class text(SatAPI):
    """"""

    def solve(self, posiform: Posiform, **params: dict) -> str:
        return str(posiform)