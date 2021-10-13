from ..api import SatAPI

__SATYRUS_HELP = {
    "answer": "Initial answer",
    "debug": "Enters debug mode (Sets verbosity to maximum level)",
    "source": "Source code file path",
    "legacy": "Intended to compile SATish code in legacy syntax",
    "solver": "Selects solver interface. For more information, refer to the 'sat-api' command",
    "output": "Output file destination",
    "verbose": "Compiler output verbosity, from 0 (default, no output, except errors and results) to 3 (complete compiler log)",
    "version": "Displays compiler version",
    "report": "Shows detailed sectioned elapsed time",
    "params": "Path to JSON file containing parameters for passing to Solver API",
    "clear": "Clears compiler cache",
}

__SAT_API_HELP = {
    "add": "Selects Python files (.py) where SatAPI interfaces are declared",
    "build": "Compiles the Python files (.py) into (.pyc) files",
    "clear": "Clears all user-defined interfaces",
    "remove": "Selects interfaces for removal",
}

def satyrus_help(key: str, **kwargs) -> str:
    if key in __SATYRUS_HELP:
        return __SATYRUS_HELP[key].format(**kwargs)
    else:
        return ""

def sat_api_help(key: str, **kwargs) -> str:
    if key in __SAT_API_HELP:
        return __SAT_API_HELP[key].format(**kwargs)
    else:
        return ""

__all__ = ["satyrus_help", "sat_api_help"]