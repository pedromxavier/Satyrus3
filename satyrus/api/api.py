""" :: SATyrus Python API ::
    ========================

    Example:

    >>> sat = SatAPI.load_source('~/path/source.sat')
    >>> # - Mosel Xpress Solver -
    >>> sat['mosel'].solve()
    >>> # - DWave Quantum Annealing Solver -
    >>> sat['dwave'].solve()
""" 
## Standard Library
import abc
from functools import wraps

## Local
from ..satlib import stdout
from ..sat.types import Expr

class MetaSatAPI(abc.ABCMeta):

    name = 'SatAPI'

    base_class = None

    subclasses = {

    }

    options = []

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if 'solve' not in attrs:
            raise NotImplementedError(f"Method .solve(self) must be implemented for class {name}.")
        else:
            attrs['solve'] = cls.solve_func(attrs['solve'])

        if name == cls.name:
            cls.base_class = new_class = type.__new__(cls, name, bases, {**attrs, 'subclasses': cls.subclasses, 'options' : cls.options})
        else:
            if name not in cls.options:
                cls.subclasses[name] = new_class = type.__new__(cls, name, bases, attrs)
                cls.options.append(name)
            else:
                raise ValueError(f"Method `{name}` defined twice.")

        return new_class

    @classmethod
    def solve_func(cls, func: callable):
        """ func(api: SatAPI)
        """
        @wraps(func)
        def new_func(api):
            if api.code:
                return None
            else:
                return func(api)
        return new_func

class SatAPI(metaclass=MetaSatAPI):

    key = None

    subclasses = {

    }

    options = []

    def __init__(self, source_path: str, solve: bool=True, **kwargs: dict):
        """
        """
        self.source_path: str = source_path
        self.kwargs: dict = kwargs

        ## Regular usage
        if solve:
            from ..sat import Satyrus
            self.satyrus = Satyrus(self.source_path, **self.kwargs)
        else:
            self.satyrus = None

    def __getitem__(self, key: str):
        subclass = self.subclasses[key](source_path=self.source_path, solve=False, **self.kwargs)
        subclass.satyrus = self.satyrus
        return subclass

    @property
    def results(self):
        return self.satyrus.results

    @property
    def code(self):
        return self.satyrus.code

    @abc.abstractmethod
    def solve(self):
        raise NotImplementedError

## NOTE: DO NOT EDIT ABOVE THIS LINE
## ---------------------------------

## Text Output
class text(SatAPI):

    def solve(self) -> str:
        stdout[0] << self.results

# ## CSV Output
# class csv(SatAPI):
#     ...

# ## cvxpy
# class cvxpy(SatAPI):
#     ## https://www.cvxpy.org/tutorial/advanced/index.html#mixed-integer-programs
#     ## import cvxpy as cp
#     ...

# class dwave(SatAPI):
#     ...