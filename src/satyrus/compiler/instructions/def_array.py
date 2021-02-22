""" DEF_ARRAY
    =========

    STATUS: OK
"""

from ..compiler import SatCompiler
from ...types import Var, Array, Number, PythonObject
from ...types.error import SatTypeError, SatValueError

def def_array(compiler: SatCompiler, name: Var, shape: tuple, buffer: list):
    """ Array definition
        ================

        1. Evaluate every shape component
        2. Evaluate buffer content
        3. Set Array to memory
    """
    ## Evaluates shape values and variables
    shape = tuple(compiler.evaluate(n, miss=True, calc=True, track=True) for n in shape)

    compiler.checkpoint()
    
    ## Checks for array shape consistency.
    def_array_shape(compiler, shape)

    ## Special treatment for python object buffer
    if type(buffer) is PythonObject:
        def_python_buffer(compiler, name, shape, buffer)
    else:
        ## Runs correction checking and normalization
        def_array_buffer(compiler, name, shape, buffer)

    compiler.checkpoint()

def def_array_shape(compiler: SatCompiler, shape: tuple):   
    """ DEF_ARRAY_SHAPE
        ===============
    """
    for n in shape:
        if type(n) is not Number or not (n.is_int and n > 0):
            compiler << SatTypeError(f'Array dimensions must be positive integers.', target=n)

def def_python_buffer(compiler: SatCompiler, name: Var, shape: tuple, buffer: PythonObject):
    """ DEF_ARRAY_BUFFER
        ================
    """
    ## retrieve object
    if type(buffer.obj) is list:
        compiler.memset(name, Array.from_list(name, shape, buffer))
    elif type(buffer.obj) is dict:
        compiler.memset(name, Array.from_dict(name, shape, buffer))
    else:
        compiler << SatTypeError()

def def_array_buffer(compiler: SatCompiler, name: Var, shape: tuple, buffer: list):
    """ DEF_ARRAY_BUFFER
        ================
    """

    array = {}

    if buffer is None:
        pass
    else:
        for idx, val in buffer:
            idx = tuple(compiler.evaluate(i, miss=True, calc=True) for i in idx)

            if len(idx) > len(shape):
                compiler << SatValueError(f'Too much indices for {len(shape)}-dimensional array', target=idx[len(shape)])
                
            for i, n in zip(idx, shape):
                if not i.is_int:
                    compiler << SatTypeError(f'Array indices must be integers.', target=i)
                    
                if not (1 <= i <= n):
                    compiler << SatValueError(f'Indexing ´{i}´ is out of bounds [1, {n}]', target=i)

            val = compiler.evaluate(val, miss=True, calc=True)

            if type(val) is not Number:
                compiler << SatValueError(f'Array elements must be numbers.', target=val)
            else:
                array[tuple(map(int, idx))] = val

        compiler.checkpoint()

    ## Sets new `types.Array` to memory.
    ## Also runs automatic compiler.checkpoint()
    compiler.memset(name, Array.from_buffer(name, shape, array))