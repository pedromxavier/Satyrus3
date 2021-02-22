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

## Local
from ..satlib import Stream, stdout, stderr, stdwar, devnull
from ..types import Expr, Number, Var
from ..types.symbols.tokens import T_ADD, T_MUL, T_AUX

## Disable unecessary output
Stream.set_lvl(0)

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
            from ..satyrus import Satyrus
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

    def solve(self, posiform: dict) -> (None, str):
        """
        """
        expr = Expr(T_ADD, *(cons if term is None else Expr(T_MUL, cons, *term) for (term, cons) in posiform.items()))
        return (None, str(Expr.calculate(expr)))

# ## CSV Output
# class csv(SatAPI):
#     ...

## cvxpy - gurobi
class gurobi(SatAPI):
    ## https://www.cvxpy.org/tutorial/advanced/index.html#mixed-integer-programs
    ## import cvxpy as cp

    def solve(self, posiform: dict):
        import cvxpy as cp
        import numpy as np

        from ..satlib import qubo

        x, Q, c = qubo().solve(posiform)

        X = cp.Variable(len(x), boolean=True)
        P = cp.Problem(cp.Minimize(cp.quad_form(X, Q)), constraints=None)
        
        try:
            with devnull: P.solve(solver=cp.GUROBI) ## Silenced output
            
            y, e = X.value, P.value
            s = {k: int(y[i]) for k, i in x.items()}
            return (s, e + c)
        except cp.error.DCPError:
            stderr[0] << "Solver Error: Function is not convex."
            return None
        except Exception as error:
            stderr[0] << error
            return None
            

class dwave(SatAPI):
    
    def solve(self, posiform: dict):
        import neal

        stdwar[0] << "Warning: D-Wave option currently running local simulated annealing since remote connection to quantum host is unavailable."

        from ..satlib import qubo

        sampler = neal.SimulatedAnnealingSampler()

        x, Q, c = qubo().solve(posiform)

        sampleset = sampler.sample_qubo(Q)

        y, e, *_ = sampleset.record[0]

        s = {k: y[i] for k, i in x.items()}

        return (s, e + c)