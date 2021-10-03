""""""
# Local
from .base import SatType
from .expr import Expr
from .number import Number
from .var import Var
from ..error import SatIndexError
from ..symbols import T_IDX

class Array(SatType):
    """ :: Array ::
        ===========
    """
    def __init__(self, var: Var, shape: tuple):
        SatType.__init__(self)
        
        self.array = {}

        self.var = var
        self.shape = shape
        self.dim = len(shape)

    def _IDX_(self, idx: tuple):
        if len(idx) > self.dim:
            raise SatIndexError(f"Too much indices for {self.dim}-dimensional array.", target=idx[-1])
        elif len(idx) == 1:
            return self[idx[0]]
        else:
            i, *idx = idx
            return self[i]._IDX_(idx)

    def __getitem__(self, i: Number):
        if type(i) is Number and i.is_int:
            j = int(i)
            if j in self.array:
                return self.array[j]
            else:
                n = int(self.shape[0])
                if 1 <= j <= n:
                    if len(self.shape) > 1:
                        self.array[j] = Array(self.var._IDX_((i,)), self.shape[1:])
                        return self.array[j]
                    else:
                        return self.var._IDX_((i,))
                else:
                    raise SatIndexError(f"Index {i} is out of bounds [1, {n}].", target=i)
        elif type(i) is Var:
            return Expr(T_IDX, self, i)
        else:
            raise SatIndexError(f"Invalid index `{i}` of type `{type(i)}`.", target=i)

    def __setitem__(self, i: Number, value: SatType):
        if type(i) is Number and i.is_int:
            if self.dim > 1:
                raise SatIndexError(f"Attempt to assign to {self.dim}-dimensional array.", target=i)
            else:
                j = int(i)
                n = int(self.shape[0])
                if 1 <= j <= n:
                    self.array[j] = value
                else:
                    raise SatIndexError(f"Index {i} is out of bounds [1, {n}].", target=i)                 
        else:
            raise SatIndexError(f"Invalid index {i}.", target=i)

    def __str__(self):
        return f"{self.var}" #+ "".join([f"[{n}]" for n in self.shape])

    def __repr__(self):
        return f"Array({self.var!r}, {self.shape!r})"

    def __hash__(self):
        return hash(sum(hash((k, hash(v))) for k, v in self.array.items()))
        
    @classmethod
    def from_buffer(cls, name, shape, buffer: dict):
        array = cls(name, shape)
        for idx in buffer:
            subarray = array
            for i in idx[:-1]:
                subarray = subarray[Number(i)]
            subarray[Number(idx[-1])] = buffer[idx]
        return array

    @classmethod
    def from_dict(cls, name: Var, shape: tuple, buffer: dict):
        """
        """
        return cls.from_buffer(name, shape, buffer)

    @classmethod
    def from_list(cls, name: Var, shape: tuple, buffer: dict):
        """
        """
        return cls.from_buffer(name, shape, { idx : val for (idx, val) in buffer })

    @property
    def is_array(self) -> bool:
        return True