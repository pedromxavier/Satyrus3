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
import importlib
import os
from functools import wraps

## Local
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
        elif 'solve' not in attrs:
            raise NotImplementedError(f"Method solve(self, posiform: dict) must be implemented for class {name}.")
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
                for import_, as_ in imports:
                    globals()[as_] = importlib.import_module(import_)

                ## Define interface
                attrs['_solve'] = cls.solve_func(attrs['solve'])
                attrs['solve'] = cls.base_class.solve

                ## Register new class
                new_class = cls.subclasses[name] = type.__new__(cls, name, bases, attrs)
                cls.options.append(name)
        return new_class

    class missing:
        
        def __init__(self, name: str, packages: list):
            self.name = name
            self.packages = [package['package'] if 'package' in package else package['import'] for package in packages]

        def __call__(self, *args, **kwargs):
            stderr[0] << f"Missing packages for this solver ({self.name}). Try running:"
            for package in self.packages:
                stderr[0] << f"\t$ pip install {package}"
            return self

        def solve(self, *args, **kwargs):
            return None

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
        if key in self.subclasses:
            subclass = self.subclasses[key](source_path=self.source_path, solve=False, **self.kwargs)
            subclass.satyrus = self.satyrus
            return subclass
        else:
            raise NotImplementedError(f"Unknown solver interface `{key}`. Available options are: {set(self.options)}")

    @classmethod
    def augment(self, fname: str):
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
    def results(self):
        return Posiform(self.satyrus.results)

    @property
    def code(self):
        return self.satyrus.code

    def _solve(self, posiform: Posiform):
        raise NotImplementedError

    @Timing.timeit(level=1, section="SatAPI.solve")
    def solve(self):
        return self._solve(self.results)

## NOTE: DO NOT EDIT ABOVE THIS LINE
## ---------------------------------

## Text Output
class text(SatAPI):

    def solve(self, posiform: dict) -> (None, str):
        """
        """
        expr = Expr(T_ADD, *(Number(cons) if term is None else Expr(T_MUL, Number(cons), *term) for (term, cons) in posiform.items()))
        return (None, str(Expr.calculate(expr)))

# ## CSV Output
class csv(SatAPI):
    
    def solve(self, posiform: Posiform):
        lines = []

        for term, cons in posiform:
            if term is None:
                lines.append(f"{cons:.4f}")
            else:
                lines.append(",".join([f"{cons:.4f}", *term]))

        s = "\n".join(lines)

        return (None, s)

class glpk(SatAPI):

    require = [ {'import': 'numpy', 'as': 'np'},
                {'import': 'cvxpy', 'as': 'cp'},
                {'import': 'cvxopt', 'check': True} ]

    def solve(self, posiform: Posiform):
        x, Q, c = posiform.qubo()

        X = cp.Variable(len(x), boolean=True)
        P = cp.Problem(cp.Minimize(cp.quad_form(X, Q)), constraints=None)

        try:
            with devnull: P.solve(solver=cp.GLPK_MI) ## Silenced output
            
            y, e = X.value, P.value
            s = {k: int(y[i]) for k, i in x.items()}
            return (s, e + c)
        except cp.error.DCPError:
            stderr[0] << "Solver Error: Function is not convex."
            return None
        except Exception as error:
            stderr[0] << error
            return None

## cvxpy - gurobi
class gurobi(SatAPI):
    ## https://www.cvxpy.org/tutorial/advanced/index.html#mixed-integer-programs
    
    require = [ {'import': 'numpy', 'as': 'np'},
                {'import': 'cvxpy', 'as': 'cp'},
                {'import': 'gurobipy', 'package': '-i https://pypi.gurobi.com gurobipy', 'check': True} ]

    def solve(self, posiform: Posiform):
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

    require = [{'import': 'neal', 'package': 'dwave-neal'}]
    
    def solve(self, posiform: Posiform):
        stdwar[0] << "Warning: D-Wave option currently running local simulated annealing since remote connection to quantum host is unavailable."

        sampler = neal.SimulatedAnnealingSampler()

        x, Q, c = posiform.qubo()

        sampleset = sampler.sample_qubo(Q, num_reads=100, num_sweeps=2_000)

        y, e, *_ = sampleset.record[0]

        s = {k: y[i] for k, i in x.items()}

        return (s, e + c)