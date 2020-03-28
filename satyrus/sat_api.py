""" :: SATyrus Python API ::
    ========================

    Example:

    >>> sco = {
        'int' : [...],
        'opt' : [...],
        ...
    }
    >>> sat = SatAPI(sco)
    >>> dump(sat['xpress'], 'sat.xpress')
    >>> dwave.neal.solve(sat['dwave'])
""" 

class SatAPI:

    def __init__(self, sco):
        self.sco = sco
