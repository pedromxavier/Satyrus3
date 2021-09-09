"""\
satyrus/api/api.py
------------------
"""
# Future Imports
from __future__ import annotations

# Standard Library
import importlib.util
from abc import abstractmethod
from os import stat
from pathlib import Path
from typing import Callable

# Third-Party
from cstream import devnull, stderr, stdwar, stdlog
from dimod.views.quadratic import Quadratic

# Local
from ..error import SatSolverError
from ..satyrus import Satyrus
from ..satlib import Posiform, Timing


class MetaSatAPI(type):
    """"""

    BASE_CLASS = "SatAPI"
    base_class = None
    subclasses = {}

    def __new__(cls, name: str, bases: tuple, namespace: dict):
        """"""
        if name == cls.BASE_CLASS:
            if cls.base_class is None:
                cls.base_class = type.__new__(cls, name, bases, {**namespace, "subclasses": cls.subclasses})
                return cls.base_class
            else:
                raise NameError("'SatAPI' base class is already implemented.")
        elif name in cls.subclasses:
            raise NameError(f"API Interface '{name}' is already defined.")
        elif cls.base_class is None:
            raise NameError("'SatAPI' base class is not implemented yet.")
        elif "solve" not in namespace:
            raise NotImplementedError(f"Method solve(self, posiform: Posiform, **params: dict) -> tuple[dict, float] | object must be implemented for '{name}'.")
        else:
            imports = []
            missing = []
            if "require" in namespace:
                for package in namespace["require"]:
                    if importlib.util.find_spec(package) is None:
                        missing.append(package)
                    else:
                        imports.append(package)

            if missing:
                cls.subclasses[name] = None
            else:
                # Import required packages - Not neccessary
                # globals().update(
                #     {package: importlib.import_module(package) for package in imports}
                # )

                # Register new class
                cls.subclasses[name] = type.__new__(cls, name, bases, namespace)

            return cls.subclasses[name]


class SatAPI(metaclass=MetaSatAPI):

    subclasses = {}

    class SatAPISolver:
        def __init__(self, energy: Posiform, method: Callable):
            self.method = method
            self.energy = energy

        @Timing.Timer(level=2, section="Solver.solve")
        def solve(self, **params: dict):
            return self.method(self.energy, **params)

    @classmethod
    def include(cls, fname: str):
        """Includes new SatAPI interfaces given a separate Python file (``.py``, ``.pyw``).

        Parameters
        ----------
        fname : str
            Path to Python file.
        """
        path = Path(fname)

        stdwar[1] << f"Augmenting API with content from '{path}'"

        interfaces = set(cls.subclasses)

        if not path.exists() or not path.is_file():
            cls.error(f"File {path} does not exists")
        elif path.suffix not in {".py", ".pyw"}:
            raise FileExistsError(f"File '{path}' must be a Python file i.e. {{.py, .pyw}}")
        else:
            with path.open(mode="r", encoding="utf8") as file:
                source = file.read()

            # -*- Compile & Execute API Code -*-
            code = compile(source, filename=path.name, mode="exec")

            exec(code)

            newly_added = set(cls.subclasses) - interfaces

            if newly_added:
                cls.log("External API interfaces defined:", level=2)
                for i, option in enumerate(newly_added, 1):
                    cls.log(f"\t{i}. {option}", level=2)
            else:
                cls.warn("No new API interfaces included")

    def __init__(self, *, path: str = None, satyrus: Satyrus = None, **params: dict):
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

        if isinstance(satyrus, Satyrus):
            if path is None:
                self.satyrus = satyrus
            else:
                raise ValueError("Can't handle both 'path' and 'satyrus' options")
        elif isinstance(path, Path):
            if satyrus is None:
                self.satyrus = Satyrus(path=path, **params)
            else:
                raise ValueError("Can't handle both 'path' and 'satyrus' options")
        else:
            raise ValueError("Either 'path' or 'satyrus' must be provided")

    def __getitem__(self, key: str):
        if key in self.subclasses:
            if self.subclasses[key] is not None:
                return self.subclasses[key](satyrus=self.satyrus).__solver()
            else:
                raise NotImplementedError(f"Missing requirements for Solver Interface '{key}'")
        else:
            raise NotImplementedError(f"Unknown solver interface '{key}'. Available options are: {self.options()}")

    def __solver(self) -> SatAPISolver:
        if not self.satyrus.ready():
            self.satyrus.compile()

        return self.SatAPISolver(self.satyrus.energy(), self.solve)

    @classmethod
    def options(cls) -> set:
        return set(cls.subclasses.keys())

    @classmethod
    def complete(cls, answer: tuple[dict, float] | object) -> bool:
        return isinstance(answer, tuple) and len(answer) == 2 and isinstance(answer[0], dict) and isinstance(answer[1], float)

    @abstractmethod
    def solve(self, posiform: Posiform, **params: dict) -> tuple[dict, float] | object:
        pass

    @staticmethod
    def error(message: str):
        if stderr[0]:
            stderr[0] << f"Solver Error: {message}"
        exit(1)

    @staticmethod
    def warn(message: str):
        if stdwar[1]:
            stdwar[1] << f"Warning: {message}"

    @staticmethod
    def log(message: str, level: int=3):
        stdlog[level] << message


# NOTE: DO NOT EDIT ABOVE THIS LINE
# ---------------------------------

# Text Output
class text(SatAPI):
    """"""

    def solve(self, posiform: Posiform, **params: dict) -> str:
        return posiform.toJSON()


# CSV Table Output
class csv(SatAPI):
    def solve(self, posiform: Posiform, **params: dict) -> str:
        lines = []

        for term, cons in posiform:
            if term is None:
                lines.append(f"{cons:.5f}")
            else:
                lines.append(",".join([f"{cons:.5f}", *term]))

        return "\n".join(lines)


## cvxpy - gurobi
class gurobi(SatAPI):
    ## https://www.cvxpy.org/tutorial/advanced/index.html#mixed-integer-programs

    requires = ["gurobipy"]

    def solve(self, posiform: Posiform, **params: dict) -> tuple[dict, float]:
        """"""
        import gurobipy as gp

        # Retrieve QUBO
        x, Q, c = posiform.qubo()

        # Create a new model
        model = gp.Model("MIP")

        X = model.addMVar(len(x), vtype=gp.GRB.BINARY, name="")

        model.setMObjective(Q, None, 0.0, X, X, None, sense=gp.GRB.MINIMIZE)

        try:
            with devnull:
                model.optimize()

            y = list(model.getVars())

            s = {k: int(y[i].x) for k, i in x.items()}
            e = model.objVal

            return (s, e + c)
        except gp.GurobiError as error:
            self.error(f"(Gurobi code {error.errno}) {error}")


class dwave(SatAPI):

    requires = ["neal"]

    def solve(self, posiform: Posiform, *, num_reads=1_000, num_sweeps=1_000, **params: dict) -> tuple[dict, float]:
        """
        Parameters
        ----------
        posiform : Posiform
            Input Expression
        params : dict (optional)
            num_reads : int = 1_000
            num_sweeps : int = 1_000
        """
        import neal

        # Parameter check
        self.check_params(num_reads=num_reads, num_sweeps=num_sweeps)

        self.warn("D-Wave option currently running local simulated annealing since remote connection to quantum host is unavailable")

        self.log(f"Dwave Parameters: num_reads={num_reads}; num_sweeps={num_sweeps}")

        sampler = neal.SimulatedAnnealingSampler()

        x, Q, c = posiform.qubo()

        sampleset = sampler.sample_qubo(Q, num_reads=num_reads, num_sweeps=num_sweeps)

        y, e, *_ = sampleset.record[0]

        s = {k: int(y[i]) for k, i in x.items()}

        return (s, e + c)

    def check_params(self, **params: dict):
        if "num_reads" in params:
            num_reads = params["num_reads"]
            if not isinstance(num_reads, int) or num_reads <= 0:
                self.error("Parameter 'num_reads' must be a positive integer")
        else:
            self.error("Missing parameter 'num_reads'")

        if "num_sweeps" in params:
            num_sweeps = params["num_sweeps"]
            if not isinstance(num_sweeps, int) or num_sweeps <= 0:
                self.error("Parameter 'num_sweeps' must be a positive integer")
        else:
            self.error("Missing parameter 'num_sweeps'")
