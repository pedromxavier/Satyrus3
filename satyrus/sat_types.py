from sat_core import *;
from sat_errors import *;
from sat_base import *;

class Stmt(BaseExpr):

    def c_const(stmt, engine, name, value):
        ''' Constant definition:
            NAME = VALUE;
        '''
        engine.memory[name] = engine.eval(value);

        return stmt;

    def c_config(stmt, engine, name, value):
        ''' System config:
            > prec : INT;
            > dir  : "STR";
            # NAME : VALUE;
        '''
        if str(name) == 'prec':
            if type(value) is Number and value.int:
                dcm.context.prec = int(value)
            else:
                error_msg = ERROR_MSGS['Stmt.c_config'][0]
                raise SatCompilation_Error(error_msg)

        elif str(name) == 'dir':
            if type(value) is str:
                if os.path.exists(value):
                    os.chdir(value)
                else:
                    error_msg = ERROR_MSGS['Stmt.c_config'][0].format(value)
                    raise SatCompilation_Error(error_msg)
            else:
                error_msg = ERROR_MSGS['Stmt.c_config'][1]
                raise SatCompilation_Error(error_msg)
        else:
            error_msg = ERROR_MSGS['Stmt.c_config'][-1].format(value)
            raise SatCompilation_Error(error_msg)

        return stmt;

    def c_array(stmt, engine, name, _shape, _buffer):
        ''' Array declaration
            NAME [m]...[n] = {(i, ..., j) : x, ..., (i, ..., k) : y};
            or
            NAME [m]...[n];
        '''
        # evaluate shape
        shape = []
        for _size in _shape:
            size = engine.eval(_size, {Number})
            if not size.int:
                raise SatType_Error(ERROR_MSGS['Stmt.c_array'][0])
            else:
                shape.append(int(size))
        shape = tuple(shape)

        # evaluate buffer
        buffer = []
        for _item in _buffer: # _buffer [(i,x), ..., (j, y)];
            _i, _x = _item # _i (i1, i2, ..., ik);
            i = []
            for _j in _i:
                j = engine.eval(_j, {Number})
                if not j.int:
                    raise SatType_Error(ERROR_MSGS['Stmt.c_array'][1])
                else:
                    i.append(int(j))
            x = engine.eval(_x, {Number}) # x just need to be a number.
            buffer.append((tuple(i), x))

        engine.memory[name] = Array(name, shape, buffer)

        return stmt;

    COMPILE = {
        H_CONST : c_const,
        H_CONFIG: c_config,
        H_ARRAY : c_array,
    }

    def e_const(stmt, engine, name, value):
        """ Constants are defined at compilation time.
        """
        ...

    def e_config(stmt, engine, name, value):
        """ System env variables are set at compilation time.
        """
        ...

    def e_array(stmt, enfine, name, shape, buffer):
        """ Arrays are defined at compilation time.
        """
        ...

    EXECUTE = {
        H_CONST : e_const,
        H_CONFIG: e_config,
        H_ARRAY : e_array,
    }

    def compile(stmt, engine):
        return Stmt.COMPILE[stmt.head](stmt, engine, *stmt.tail)

    def execute(stmt, engine):
        return Stmt.EXECUTE[stmt.head](stmt, engine, *stmt.tail)

class Array(dict):
    ''' 1-indexed sparse array
    '''

    def __init__(self, name, shape, buffer):
        dict.__init__(self)

        self.shape = shape
        self.dim = len(shape)

        self.var = Var(name)

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
                    j, *i = i;
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
            raise SatIndex_Error(error_msg)
        elif len(idx) < self.dim:
            error_msg = f'Too few indexes for {self.dim}-dimensional array'
            raise SatIndex_Error(error_msg)
        elif not self.inside(idx):
            error_msg = f'Index {idx} is out of bounds {self.bounds}'
            raise SatIndex_Error(error_msg)
        elif not all((type(i) is int) for i in idx):
            error_msg = f'Array indices must be integers, not {list(map(type, idx))}'
            raise SatIndex_Error(error_msg)

        return tuple(map(int, idx))

    @property
    def bounds(self):
        return u" × ".join([f"[1, {i}]" for i in self.shape])

    @property
    def name(self):
        return str(self.var)

class Constraint(object):

    def __init__(self, type, name, level, loops, expr):
        self.type = type
        self.name = name
        self.level = level
        self.loops = loops
        self.expr = expr
