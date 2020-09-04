""" :: SATyrus Python API ::
    ========================

    Example:

    >>> sat = SatAPI.load_source('~/path/source.sat')
    >>> # - Mosel Xpress Solver -
    >>> sat['mosel'].solve()
    >>> # - DWave Quantum Annealing Solver -
    >>> sat['dwave'].solve()
""" 

class MetaSatAPI(type):

    name = 'SatAPI'

    base_class = None

    subclasses = {

    }

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if name == cls.name:
            cls.base_class = new_class = type(name, bases, {**attrs, 'subclasses': cls.subclasses})
        else:
            cls.subclasses[attrs['key']] = new_class = type(name, bases, attrs)
        
        return new_class

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
        ...

## NOTE: DO NOT EDIT ABOVE THIS LINE
## ---------------------------------
## 

class Text(SatAPI):

    key = 'text'

    def __init__(self):
        ...



