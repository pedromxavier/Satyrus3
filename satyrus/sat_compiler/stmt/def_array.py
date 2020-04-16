from ...sat_types import Array, Number
from ...sat_types.error import SatTypeError, SatValueError

def def_array(compiler, name, shape, buffer):
    shape = tuple(compiler.eval(n) for n in shape)
    shape_errors = list(def_array_shape(compiler, shape))

    if shape_errors:
        compiler.memory[name] = None
        yield from shape_errors
        yield StopIteration
    
    array_buffer = {}

    buffer_errors = list(def_array_buffer(compiler, shape, buffer, array_buffer))

    if buffer_errors:
        compiler.memory[name] = Array(name, shape)
        yield from buffer_errors
        yield StopIteration

    else:
        compiler.memory[name] = Array(name, shape, array_buffer)

def def_array_shape(compiler, shape):
    for n in shape:
        if not n.is_int:
            yield SatTypeError(f'Array dimensions must be integers.', target=n)
        if not n > 0:
            yield SatValueError(f'Array dimensions must be positive numbers.', target=n)

def def_array_buffer(compiler, shape, buffer, array_buffer):
    for idx, val in buffer:
        idx = tuple(compiler.eval(i) for i in idx)

        if len(idx) > len(shape):
            yield SatValueError(f'Too much indices for {len(shape)}-dimensional array', target=idx[len(shape)])
            
        for i, n in zip(idx, shape):
            if not i.is_int:
                yield SatTypeError(f'Array indices must be integers.', target=i)
                
            if not 1 <= i <= n:
                yield SatValueError(f'Indexing ´{i}´ is out of bounds [1, {n}]', target=i)

        val = compiler.eval(val)

        if type(val) is not Number:
            yield SatValueError(f'Array elements must be numbers.', target=val)
        else:
            array_buffer[idx] = val