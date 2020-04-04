"""
"""
## Standard Library
import itertools as it

## Local
from .main import SatType
from .error import SatError
from .var import Var

class SatIndexError(SatError):
    ...

class Array(SatType, dict):
    ''' Sparse Array
    '''
    def __init__(self, name, shape, buffer):
        SatType.__init__(self)
        dict.__init__(self, buffer)
        self.name = name
        self.shape = shape

    def __idx__(self, idx):
        ...

    def __getitem__(self, idx):
        ...

    def __str__(self):
        return f"{{{', '.join(f'{i} : {self[i]}' for i in self.get_indexes())}}}"

    def __repr__(self):
        return f"{{{', '.join([f'{k} : {self[k].__repr__()}' for k in self])}}}"

    def get_indexes(self):
        return it.product(*(range(1, n+1) for n in self.shape))

    def inside(self, idx):
        return all(1 <= i <= n for i, n in zip(idx, self.shape))
    
    @property
    def dim(self):
        return len(self.shape)

    @property
    def bounds(self):
        return u" × ".join([f"[1, {i}]" for i in self.shape])