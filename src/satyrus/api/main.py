""" :: SATyrus Python API ::
    ========================

    Example:

    >>> source = load('source.sat')
    >>> sat = SatAPI(source)
    >>> # - Mosel Xpress Solver -
    >>> dump(sat['mosel'], 'sat.xpress')
    >>> # - DWave Quantum Annealing Solver -
    >>> dwave.neal.solve(sat['dwave'])
""" 

class SatAPI:

    def __init__(self, source):
        self.source = source

    def dwave(self):
        ...
