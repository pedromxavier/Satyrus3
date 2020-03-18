from .error import SatError
from .var import Var

class SatIndexError(SatError):
    ...

class Array(dict):
    ''' Sparse Array
    '''

    def __init__(self, name, shape, buffer):
        dict.__init__(self)

        self.shape = shape
        self.dim = len(shape)

        self.init_buffer(buffer)
        
        self.var = Var(name)

    def init_buffer(self, buffer):
        for idx, val in buffer:
            idx = self.valid(idx)
            self[idx] = val

    def __idx__(self, _i):

        i = self.valid(_i)

        if len(i) == self.dim:

            if i in self:
                return dict.__getitem__(self, i)

            else:
                var = self.var
                while len(i):
                    j, *i = i
                    var = var.__idx__(j)
                return var

        else: # len(i) < self.dim FUTURE

            ...

    def __getitem__(self, i):
        return self.__idx__(i)

    def __str__(self):
        return "{{{}}}".format(", ".join(f"{i} : {self[i]}" for i in self.get_indexes(self.shape)))

    def __repr__(self):
        return "{{{}}}".format(", ".join([f"{k} : {self[k].__repr__()}" for k in self]))

    @staticmethod
    def get_indexes(size):
        if len(size) == 1:
            return ((i,) for i in range(1, size[0]+1))
        else:
            return ((i, *J) for i in range(1, size[0]+1) for J in Array.get_indexes(size[1:]))

    def inside(self, idx):
        return all(1 <= i <= n for i,n in zip(idx, self.shape))

    def valid(self, idx):
        if len(idx) > self.dim:
            error_msg = f'Too much indexes for {self.dim}-dimensional array'
            raise SatIndexError(error_msg)
        elif len(idx) < self.dim:
            error_msg = f'Too few indexes for {self.dim}-dimensional array'
            raise SatIndexError(error_msg)
        elif not self.inside(idx):
            error_msg = f'Index {idx} is out of bounds {self.bounds}'
            raise SatIndexError(error_msg)
        elif not all((type(i) is int) for i in idx):
            error_msg = f'Array indices must be integers, not {list(map(type, idx))}'
            raise SatIndexError(error_msg)

        return tuple(map(int, idx))

    @property
    def bounds(self):
        return u" × ".join([f"[1, {i}]" for i in self.shape])

    @property
    def name(self):
        return str(self.var)