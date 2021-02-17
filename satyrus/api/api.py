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
from functools import wraps

## Third-Party
import numpy as np

## Local
from ..satlib import stdout
from ..sat.types import Expr
from ..sat.types.symbols.tokens import T_ADD, T_MUL

class MetaSatAPI(type):

    base_class_name = 'SatAPI'
    base_class = None

    subclasses = {

    }

    options = []

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if name == cls.base_class_name:
            new_class =cls.base_class = type.__new__(cls, name, bases, {**attrs, 'subclasses': cls.subclasses, 'options' : cls.options})
        elif name in cls.options:
            raise ValueError(f"Class `{name}` defined twice.")
        elif cls.base_class is None:
            raise NotImplementedError(f"Base class `{cls.base_class_name}` was not implemented.")
        elif 'solve' not in attrs:
            raise NotImplementedError(f"Method solve(self, posiform: dict) must be implemented for class {name}.")
        else:
            attrs['_solve'] = cls.solve_func(attrs['solve'])
            attrs['solve'] = cls.base_class.solve

            new_class = cls.subclasses[name] = type.__new__(cls, name, bases, attrs)
            cls.options.append(name)
        return new_class

    @classmethod
    def solve_func(cls, func: callable):
        """ func(api: SatAPI)
        """
        @wraps(func)
        def new_func(api, *args, **kwargs):
            if api.code:
                return None
            else:
                return func(api, *args, **kwargs)
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

    def _solve(self, posiform: dict):
        raise NotImplementedError

    def solve(self):
        return self._solve(self.results)

## NOTE: DO NOT EDIT ABOVE THIS LINE
## ---------------------------------

## Text Output
class text(SatAPI):

    def solve(self, posiform: dict) -> str:
        """
        """
        expr = Expr(T_ADD, *(cons if term is None else Expr(T_MUL, cons, *term) for (term, cons) in posiform.items()))
        return str(Expr.calculate(expr))

class qubo(SatAPI):

    def solve(self, posiform: dict) -> (dict, np.ndarray):
        """
        :param posiform:
        :type posiform: dict
        :returns: 
        :rtype: (dict, np.ndarray)
        """
        var = set()
        for term in posiform:
            if term is not None:
                if len(term) >= 3: ## check for degre
                    raise NotImplementedError('Degree reduction is not implemented yet.')
                else:
                    var.update(term)
            else:
                continue
        
        n = len(var)
        x = {v: i for i, v in enumerate(sorted(var))}
        Q = np.zeros((n, n), dtype=float)

        for term, cons in posiform.items():
            if term is not None:
                i = tuple(map(x.get, term))
                if len(i) == 1:
                    i = (*i, *i)
                elif len(i) >= 3:
                    raise ValueError('Degree reduction failed.')

                Q[i] += float(cons)
            else:
                continue ## Neglect constant.
        return x, Q

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