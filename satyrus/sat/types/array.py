"""
"""
## Standard Library
import itertools as it

## Local
from .main import SatType, Var, Number
from .error import SatIndexError

class Array(SatType):
    """ :: Array ::
        ===========
    """
    def __init__(self, name, shape):
        SatType.__init__(self)
        
        self.array = {}

        self.name = name
        self.shape = shape
        self.dim = len(shape)

    def __idx__(self, idx: Number):
        return self[idx]

    def __getitem__(self, idx: Number):
        if type(idx) is Number and idx.is_int:
            i = int(idx)
            if i in self.array:
                return self.array[i]
            else:
                n = int(self.shape[0])
                if 1 <= i <= n:
                    if len(self.shape) > 1:
                        self.array[i] = Array(self.name.__idx__(idx), self.shape[1:])
                        return self.array[i]
                    else:
                        return self.name.__idx__(idx)
                else:
                    raise SatIndexError(f"Index {idx} is out of bounds [1, {n}].", target=idx)
        else:
            raise SatIndexError(f"Invalid index {idx}.", target=idx)

    def __setitem__(self, idx: Number, value: SatType):
        if type(idx) is Number and idx.is_int:
            if self.dim > 1:
                raise SatIndexError(f"Attempt to assign to {self.dim}-dimensional array.", target=idx)
            else:
                i = int(idx)
                n = int(self.shape[0])
                if 1 <= i <= n:
                    self.array[i] = value
                else:
                    raise SatIndexError(f"Index {idx} is out of bounds [1, {n}].", target=idx)                 
        else:
            raise SatIndexError(f"Invalid index {idx}.", target=idx)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}" + "".join([f"[{n}]" for n in self.shape])
        
    @classmethod
    def from_buffer(cls, name, shape, buffer: dict):
        array = cls(name, shape)
        for idx in buffer:
            subarray = array
            for i in idx[:-1]:
                subarray = subarray[Number(i)]
            subarray[Number(idx[-1])] = buffer[idx]
        return array
