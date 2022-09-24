"""\
"""
from __future__ import annotations

from ..compiler import SATCompiler
from ...types import Var, Array, Number
from ...error import SATTypeError, SATValueError
from ...satlib import arange

def def_array(compiler: SATCompiler, name: Var, shape: tuple, buffer: list, dense: bool):
    """\
    """
    # Evaluates shape values and variables
    shape = tuple(compiler.evaluate(n, miss=True, calc=True, track=True) for n in shape)

    # Checks for array shape consistency.
    def_array_shape(compiler, shape)

    def_array_buffer(compiler, name, shape, buffer, dense)

    compiler.checkpoint()

def def_array_shape(compiler: SATCompiler, shape: tuple):   
    """\
    """
    for n in shape:
        if not isinstance(n, Number) or not (n.is_int and n > 0):
            compiler << SATTypeError('Array dimensions must be positive integers.', target=n)

def def_array_buffer(compiler: SATCompiler, name: Var, shape: tuple, buffer: list, dense: bool):
    """\
    """
    array = {}

    if buffer is None:
        pass
    elif dense:
        def_dense_array_buffer(compiler, shape, array, buffer)
    else:
        def_sparse_array_buffer(compiler, shape, array, buffer)
    
    compiler.checkpoint()

    ## Sets new `types.Array` to memory.
    ## Also runs automatic compiler.checkpoint()
    if dense:
        compiler.memset(name, Array.from_list(name, shape, array))
    else:
        compiler.memset(name, Array.from_dict(name, shape, array))

def def_dense_array_buffer_get(buffer: list | object, index: tuple):
    if index:
        i, *index = index
        return def_dense_array_buffer_get(buffer[int(i) - 1], index)
    else:
        return buffer

def def_dense_array_buffer(compiler: SATCompiler, shape: tuple, array: dict, buffer: list, index: tuple = None):
    """\
    """
    if not shape:
        array[index] = def_dense_array_buffer_get(buffer, index)
    else:
        n, *shape = shape

        if len(buffer) != n:
            compiler << SATValueError("Invalid dimension", target=n)
            return
        else:
            if index is None:
                index = ()

            for i in arange(Number('1'), n):
                def_dense_array_buffer(compiler, shape, array, buffer, (*index, i))
            

def def_sparse_array_buffer(compiler: SATCompiler, shape: tuple, array: dict, buffer: dict):
    """\
    """
    for idx, val in buffer:
        idx = tuple(compiler.evaluate(i, miss=True, calc=True, track=True) for i in idx)

        if len(idx) > len(shape):
            compiler << SATValueError(f'Too much indices for {len(shape)}-dimensional array', target=idx[len(shape)])
            
        for i, n in zip(idx, shape):
            if not (isinstance(i, Number) and i.is_int):
                compiler << SATTypeError('Array indices must be integers.', target=i)
                
            if not (1 <= i <= n):
                compiler << SATValueError(f"Indexing '{i}' is out of bounds [1, {n}]", target=i)

        val = compiler.evaluate(val, miss=True, calc=True)

        if type(val) is not Number:
            compiler << SATValueError('Array elements must be numbers.', target=val)
        else:
            array[tuple(map(int, idx))] = val
