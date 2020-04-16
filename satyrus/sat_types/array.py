"""
"""
## Standard Library
import itertools as it

## Local
from .main import SatType
from .error import SatIndexError
from .var import Var

class Array(SatType, dict):
    ''' Sparse Array
    '''
    def __init__(self, name, shape, buffer=None):
        SatType.__init__(self)
        dict.__init__(self, buffer if buffer is not None else {})
        self.name = name
        self.shape = shape

    def __idx__(self, idx):
        if len(idx) == self.dim:
            return self[idx]
        elif len(idx) < self.dim:
            raise NotImplementedError('Array slicing is under the way.')
        else:
            raise SatIndexError(f'Too much indices for {self.dim}-dimensional array.', target=idx[self.dim])

    def __getitem__(self, idx):
        for i, n in zip(idx, self.shape):
            if not (1 <= i <= n):
                raise SatIndexError(f'Index {i} is out of bounds [1, {n}]', target=i)
        else:
            try:
                return self[idx]
            except KeyError:
                return self.name.__idx__(idx)

    def __str__(self):
        return f"{{{', '.join(f'{i} : {self[i]}' for i in self.get_indexes())}}}"

    def __repr__(self):
        return f"{{{', '.join([f'{k} : {self[k].__repr__()}' for k in self])}}}"

    def get_indexes(self):
        return it.product(*(range(1, n+1) for n in self.shape))
    
    @property
    def dim(self):
        return len(self.shape)

    @property
    def bounds(self):
        return u" × ".join([f"[1, {i}]" for i in self.shape])