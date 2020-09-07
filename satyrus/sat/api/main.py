""" :: SATyrus Python API ::
    ========================

    Example:

    >>> sat = SatAPI.load_source('~/path/source.sat')
    >>> # - Mosel Xpress Solver -
    >>> sat['mosel'].solve()
    >>> # - DWave Quantum Annealing Solver -
    >>> sat['dwave'].solve()
""" 

from ...satlib import Source

class MetaSatAPI(type):

    name = 'SatAPI'

    base_class = None

    subclasses = {

    }

    options = []

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if name == cls.name:
            cls.base_class = new_class = type(name, bases, {**attrs, 'subclasses': cls.subclasses, 'options' : cls.options})
        else:
            if attrs['key'] not in cls.options:
                cls.subclasses[attrs['key']] = new_class = type(name, bases, attrs)
                cls.options.append(attrs['key'])
            else:
                raise ValueError(f"Key {attrs['key']} defined twice.")
        return new_class

class SatAPI(metaclass=MetaSatAPI):

    key = None

    subclasses = {

    }

    options = []

    def __init__(self, source_path: str):
        self.source = Source(source_path)

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