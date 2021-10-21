""" DEF_ARRAY
    =========

    STATUS: OK
"""

from ..compiler import SatCompiler
from ...types import Var, Array, Number, PythonObject
from ...error import SatTypeError, SatValueError

def def_array(compiler: SatCompiler, name: Var, shape: tuple, buffer: list, dense: bool):
    """ Array definition
        ================

        1. Evaluate every shape component
        2. Evaluate buffer content
        3. Set Array to memory
    """
    # Evaluates shape values and variables
    shape = tuple(compiler.evaluate(n, miss=True, calc=True, track=True) for n in shape)

    # Checks for array shape consistency.
    def_array_shape(compiler, shape)

    def_array_buffer(compiler, name, shape, buffer, dense)

    compiler.checkpoint()

def def_array_shape(compiler: SatCompiler, shape: tuple):   
    """ DEF_ARRAY_SHAPE
        ===============
    """
    for n in shape:
        if not isinstance(n, Number) or not (n.is_int and n > 0):
            compiler << SatTypeError(f'Array dimensions must be positive integers.', target=n)

def def_array_buffer(compiler: SatCompiler, name: Var, shape: tuple, buffer: list, dense: bool):
    """"""
    array = {}

    if buffer is None:
        pass
    else:
        for idx, val in buffer:
            idx = tuple(compiler.evaluate(i, miss=True, calc=True, track=True) for i in idx)

            if len(idx) > len(shape):
                compiler << SatValueError(f'Too much indices for {len(shape)}-dimensional array', target=idx[len(shape)])
                
            for i, n in zip(idx, shape):
                if not (isinstance(i, Number) and i.is_int):
                    compiler << SatTypeError('Array indices must be integers.', target=i)
                    
                if not (1 <= i <= n):
                    compiler << SatValueError(f"Indexing '{i}' is out of bounds [1, {n}]", target=i)

            val = compiler.evaluate(val, miss=True, calc=True)

            if type(val) is not Number:
                compiler << SatValueError('Array elements must be numbers.', target=val)
            else:
                array[tuple(map(int, idx))] = val

        compiler.checkpoint()

    ## Sets new `types.Array` to memory.
    ## Also runs automatic compiler.checkpoint()
    if dense:
        compiler.memset(name, Array.from_list(name, shape, array))
    else:
        compiler.memset(name, Array.from_dict(name, shape, array))