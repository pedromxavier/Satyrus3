""" SATyrus Python API
    ==================

    Example
    -------

    >>> sat = SatAPI('source.sat')
    >>> # - Gurobi Solver -
    >>> x, e = sat['mosel'].solve()
    >>> # - DWave Quantum Annealing Solver -
    >>> x, e = sat['dwave'].solve()
""" 
## Standard Library
import importlib
import os
from functools import wraps

## Local
from ..satyrus import Satyrus
from ..satlib import Stream, stdout, stderr, stdwar, stdlog, devnull, Posiform, Timing
from ..types import Expr, Number, Var
from ..types.symbols.tokens import T_ADD, T_MUL, T_AUX

## Eventual imports
np = cp = neal = None

## Disable unecessary output when imported
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
            raise NameError(f"Class `{name}` is already defined.")
        elif cls.base_class is None:
            raise NotImplementedError(f"Base class `{cls.base_class_name}` was not implemented.")
        elif '_solve' not in attrs:
            raise NotImplementedError(f"Method _solve(self, posiform: dict) must be implemented for class {name}.")
        else:
            imports = []
            missing = []
            if 'require' in attrs:
                for package in attrs['require']:
                    if importlib.util.find_spec(package['import']) is None:
                        missing.append(package)
                    elif 'check' in package and package['check']:
                        continue
                    else:
                        if 'as' in package:
                            imports.append((package['import'], package['as']))
                        else:
                            imports.append((package['import'], package['import']))

            if missing:
                new_class = cls.subclasses[name] = cls.missing(name, missing)
            else:
                ## Import required packages
                for import_, as_ in imports:
                    globals()[as_] = importlib.import_module(import_)

                ## Register new class
                new_class = cls.subclasses[name] = type.__new__(cls, name, bases, attrs)
                cls.options.append(name)
        return new_class

    class missing:
        
        def __init__(self, name: str, packages: list):
            self.name = name
            self.packages = [package['pip'] if 'pip' in package else package['import'] for package in packages]

        def __call__(self, *args, **kwargs):
            stderr[0] << f"There are missing packages for this solver ({self.name}). Try running:"
            for package in self.packages:
                stderr[0] << f"\t$ pip install {package}"
            return self

        def solve(self, *args, **kwargs):
            return None

class SatAPI(metaclass=MetaSatAPI):
    """
    To define a new interface one must write, in a separate Python file (``.py``, ``.pyw``), a ``SatAPI`` subclass that implements the ``_solve(self, posiform: Posiform) -> {(dict, float), object}`` method.
    
    There are two types of interface: partial and complete. Complete ones must return a ``tuple`` containing a ``dict`` (mapping between variables and binary state) and a ``float`` (total energy for the given configuration). Any implementation that does not return as specified by this signature will be considered partial, leading to its output being returned as in string formating.

    Example
    -------
    As found in ``examples/myapi.py``::

        class MyPartialAPI(SatAPI):

            def _solve(self, posiform: Posiform) -> object:
                return "My Solution"

        class MyCompleteAPI(SatAPI):

            def _solve(self, posiform: Posiform) -> (dict, float):
                x = {'x': 0, 'y': 1, 'z': 0}
                e = 2.0
                return (x, e)

    Note
    ----
    It is not necessary to import SatAPI in this case.
    """

    subclasses = {}

    options = []

    def __init__(self, source_path: str, satyrus: Satyrus=None, **kwargs: dict):
        """
        Parameters
        ----------

        source_path : str
            Path to ``.sat`` source code file.
        **kwargs : dict
            Keyword arguments for compiler.
        """
        self.source_path: str = source_path
        self.kwargs: dict = kwargs

        if satyrus is None:
            self.satyrus = Satyrus(self.source_path, **self.kwargs)
        else:
            self.satyrus = satyrus

    def __getitem__(self, key: str):
        if key in self.subclasses:
            return self.subclasses[key](source_path=self.source_path, satyrus=self.satyrus, **self.kwargs)
        else:
            raise NotImplementedError(f"Unknown solver interface `{key}`. Available options are: {set(self.options)}")

    @classmethod
    def include(self, fname: str):
        """Includes new SatAPI interfaces given a separate Python file (``.py``, ``.pyw``).

        Parameters
        ----------
        fname : str
            Path to Python file.
        """
        stdlog[1] << f"Augmenting API with content from {fname}"

        old_options = set(self.options)

        if os.path.exists(fname):
            path: str = os.path.abspath(fname)
        else:
            raise FileNotFoundError(f"File {fname} does not exists.")

        if not path.endswith(('.py', 'pyw')):
            raise FileExistsError(f"File {fname} must be a Python file. (.py, .pyw)")
        else:
            with open(path, 'r') as file:
                source = file.read()
            
            code = compile(source, filename=fname, mode='exec')

            exec(code, globals())

            all_options = set(self.options)

            new_options = all_options - old_options

            if new_options:
                stdlog[1] << "External API interfaces defined:"
                for i, option in enumerate(sorted(new_options, key=self.options.index), 1):
                    stdlog[1] << f"\t{i}. {option}"
            else:
                stdwar[0] << "Warning: No API interfaces added."

    @property
    def output(self) -> Posiform:
        return self.satyrus.output

    @property
    def code(self) -> int:
        return self.satyrus.code

    def _solve(self, posiform: Posiform) -> {(dict, float), object}:
        """
        Parameters
        ----------
        posiform : Posiform
            Object that represents a sum of products of variable terms.

        Returns
        -------
        dict
            Mapping between variables and binary states of the solution.
        float
            Total energy for given configuration.
        """
        raise NotImplementedError

    @Timing.timeit(level=1, section="SatAPI.solve")
    def solve(self):
        """Wraps specific ``_solve(self, posiform: Posiform)`` methods, bounding method to api subclass and, more specifically, instantiated problem.

        Returns
        -------
        dict
            Mapping between variables and binary states of the solution.
        float
            Total energy for given configuration.
        """

        stdlog[2] << "POSIFORM:"
        stdlog[2] << self.output

        if not self.code:
            answer: (dict, float) = self._solve(self.output)
            if self.complete(answer):
                x, e = answer
                ## Discard Ancillary variables
                x = {k: v for k, v in x.items() if not k.startswith(T_AUX)}
                return (x, e)
            else: ## Partial solution
                return answer
        else:
            return None

    @staticmethod
    def complete(answer: object):
        return (isinstance(answer, tuple) and len(answer) == 2 and isinstance(answer[0], (dict, Posiform)) and isinstance(answer[1], float))

## NOTE: DO NOT EDIT ABOVE THIS LINE
## ---------------------------------

## Text Output
class text(SatAPI):

    def _solve(self, posiform: Posiform) -> str:
        return str(Expr.calculate(Expr(T_ADD, *(Number(cons) if term is None else Expr(T_MUL, Number(cons), *map(Var, term)) for (term, cons) in posiform))))

# ## CSV Output
class csv(SatAPI):
    
    def _solve(self, posiform: Posiform) -> str:
        lines = []

        for term, cons in posiform:
            if term is None:
                lines.append(f"{cons:.5f}")
            else:
                lines.append(",".join([f"{cons:.5f}", *term]))

        return "\n".join(lines)

# class glpk(SatAPI):

#     require = [ {'import': 'numpy', 'as': 'np'},
#                 {'import': 'cvxpy', 'as': 'cp'},
#                 {'import': 'cvxopt', 'check': True} ]

#     def _solve(self, posiform: Posiform):
#         x, Q, c = posiform.qubo()

#         X = cp.Variable(len(x), boolean=True)
#         P = cp.Problem(cp.Minimize(cp.quad_form(X, Q)), constraints=None)

#         try:
#             P.solve(solver=cp.GLPK_MI) ## Silenced output
            
#             y, e = X.value, P.value
#             s = {k: int(y[i]) for k, i in x.items()}

#             return (s, e + c)
#         except cp.error.DCPError:
#             stderr[0] << "Solver Error: Function is not convex."
#             return None

## cvxpy - gurobi
class gurobi(SatAPI):
    ## https://www.cvxpy.org/tutorial/advanced/index.html#mixed-integer-programs
    
    require = [ {'import': 'numpy', 'as': 'np'},
                {'import': 'cvxpy', 'as': 'cp'},
                {'import': 'gurobipy', 'pip': '-i https://pypi.gurobi.com gurobipy', 'check': True} ]

    def _solve(self, posiform: Posiform) -> (dict, float):
        x, Q, c = posiform.qubo()

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

    require = [{'import': 'neal', 'pip': 'dwave-neal'}]
    
    def _solve(self, posiform: Posiform) -> (dict, float):
        stdwar[0] << "Warning: D-Wave option currently running local simulated annealing since remote connection to quantum host is unavailable."

        sampler = neal.SimulatedAnnealingSampler()

        x, Q, c = posiform.qubo()

        sampleset = sampler.sample_qubo(Q, num_reads=2_000, num_sweeps=2_000)

        y, e, *_ = sampleset.record[0]

        s = {k: y[i] for k, i in x.items()}

        return (s, e + c)

__all__ = ['SatAPI']