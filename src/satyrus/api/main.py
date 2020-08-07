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

class MetaSatAPI(type):

    name = 'SatAPI'

    base_class = None

    subclasses = {

    }

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if name == cls.name:
            cls.base_class = type(name, bases, {**attrs, 'subclasses': cls.subclasses})
        else:
            cls.subclasses[attrs['key']] = type(name, bases, attrs)

class SatAPI(metaclass=MetaSatAPI):

    key = None

    subclasses = {

    }

    def __init__(self, source: str):
        self.source = self.load_source(source)

    def __getitem__(self, key: str):
        return self.subclasses[key]

    @classmethod
    def load_source(cls, source: str):
        return str()

class Text(SatAPI):

    key = 'text'

    def __init__(self):
        ...



