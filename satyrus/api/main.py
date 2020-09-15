""" :: SATyrus Python API ::
    ========================

    Example:

    >>> sat = SatAPI.load_source('~/path/source.sat')
    >>> # - Mosel Xpress Solver -
    >>> sat['mosel'].solve()
    >>> # - DWave Quantum Annealing Solver -
    >>> sat['dwave'].solve()
""" 

from ..satlib import stdout

class MetaSatAPI(type):

    name = 'SatAPI'

    base_class = None

    subclasses = {

    }

    options = []

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if 'solve' not in attrs:
            raise NotImplementedError(f"Method .solve(self) must be implemented for class {name}.")
        if name == cls.name:
            cls.base_class = new_class = type.__new__(cls, name, bases, {**attrs, 'subclasses': cls.subclasses, 'options' : cls.options})
        else:
            if attrs['key'] not in cls.options:
                cls.subclasses[attrs['key']] = new_class = type.__new__(cls, name, bases, attrs)
                cls.options.append(attrs['key'])
            else:
                raise ValueError(f"Key {attrs['key']} defined twice.")
        return new_class

class SatAPI(metaclass=MetaSatAPI):

    key = None

    subclasses = {

    }

    options = []

    def __init__(self, source_path: str=None):
        """
        """
        self.source_path = source_path

        ## Regular usage
        if source_path is not None:
            from ..sat import Satyrus
            self.satyrus = Satyrus(self.source_path)
        
            ## Gather results
            self.results = self.satyrus.results

    def __getitem__(self, key: str):
        subclass = self.subclasses[key](None)
        subclass.results = self.results
        return subclass

    def solve(self):
        return self.results

## NOTE: DO NOT EDIT ABOVE THIS LINE
## ---------------------------------
## 

## Text Output
class Text(SatAPI):

    key = 'text'

    def solve(self):
        return str(self.results)

## cvxpy
## https://www.cvxpy.org/tutorial/advanced/index.html#mixed-integer-programs
## import cvxpy as cp
class cvxpy(SatAPI):

    key = 'cvxpy'

    def solve(self):
        ...

class dwave(SatAPI):

    key = 'dwave'

    def solve(self):
       ...