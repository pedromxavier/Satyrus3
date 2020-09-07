""" DEF_ARRAY
    =========

    STATUS: OK
"""

from ...types import Var, Array, Number
from ...types.error import SatTypeError, SatValueError

def def_array(compiler, name: Var, shape: tuple, buffer: list):
    """ Array definition
        ================

        1. Evaluate every shape component
        2. Evaluate buffer content
        3. Set Array to memory
    """
    ## Evaluates shape values and variables
    shape = tuple(compiler.eval(n) for n in shape)
    
    ## Checks for array shape consistency.
    def_array_shape(compiler, shape)

    ## Creates dict object to be filled right away.    
    array = {}

    ## Runs correction checking and normalization
    ## of the buffer data, storing at `array` dict.
    def_array_buffer(compiler, shape, buffer, array)

    ## Sets new `types.Array` to memory.
    ## Also runs automatic compiler.checkpoint()
    compiler.memset(name, Array(name, shape, array))

def def_array_shape(compiler, shape: tuple):
    """ DEF_ARRAY_SHAPE
        ===============
    """
    for n in shape:
        if not (n.is_int and int(n) > 0):
            compiler << SatTypeError(f'Array dimensions must be positive integers.', target=n)

    compiler.checkpoint()

def def_array_buffer(compiler, shape: tuple, buffer: list, array: dict):
    """ DEF_ARRAY_BUFFER
        ================
    """
    for idx, val in buffer:
        idx = tuple(compiler.eval(i) for i in idx)

        if len(idx) > len(shape):
            compiler << SatValueError(f'Too much indices for {len(shape)}-dimensional array', target=idx[len(shape)])
            
        for i, n in zip(idx, shape):
            if not i.is_int:
                compiler << SatTypeError(f'Array indices must be integers.', target=i)
                
            if not 1 <= int(i) <= int(n):
                compiler << SatValueError(f'Indexing ´{i}´ is out of bounds [1, {n}]', target=i)

        val = compiler.eval(val)

        if type(val) is not Number:
            compiler << SatValueError(f'Array elements must be numbers.', target=val)
        else:
            array[tuple(map(int, idx))] = val

    compiler.checkpoint()