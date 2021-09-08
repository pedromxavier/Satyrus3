from ..api import SatAPI

HELP = {
    "debug": "Enters debug mode. (Also sets verbosity to maximum level)",
    "source": "Source code file path.",
    "legacy": "Intended to compile SATish code in legacy syntax.",
    "solver": f"Solver Selection, choose from {SatAPI.options()!r}. Declare extra interfaces with the '-a, --api' parameter.",
    "output": "Output file destination",
    "verbose": "Compiler output verbosity, from 0 (default, no output, except errors and results) to 3 (complete compiler log).",
    "report": "Shows detailed sectioned elapsed time.",
    "params": "Path to JSON file containing parameters for passing to Solver API.",
    "api": "Selects Python file (.py, .pyw) where SatAPI interfaces are declared.",
}
