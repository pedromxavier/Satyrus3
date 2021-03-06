from ..api import SatAPI

HELP = {
    'debug': 'Enters debug mode. (Also sets verbosity to maximum level)',
    'source': 'Source code file path.',
    'legacy': 'Intended to compile SATish code in legacy syntax.',
    'out': f'Output method, choose from {SatAPI.options}. Declare extra interfaces with the `-a, --api` parameter.',
    'opt': 'Compiler optimization degree, from 0 (default, no actions taken) to 3.',
    'verbose': 'Compiler output verbosity, from 0 (default, no output, except errors and results) to 3 (complete compiler log).',
    'api': 'Selects Python file (.py, .pyw) where SatAPI interfaces are declared.'
}