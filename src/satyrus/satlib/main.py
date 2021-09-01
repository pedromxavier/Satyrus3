"""
"""
## Standard Library
import sys
import os
import re
import posixpath
import traceback
import pickle
import shutil
import warnings
import itertools as it
import _thread as thread
from io import StringIO
from functools import wraps, reduce

os.path.join = posixpath.join

def compose(*funcs: callable):
    """`compose(f, g, h)` is equivalent to `lambda *args, **kwargs: f(g(h(*args, **kwargs)))`"""
    return reduce(lambda f, g: (lambda *x, **kw: f(g(*x, **kw))), funcs)

def join(glue: str, args: list, func=str, enum: bool = False) -> str:
    """"""
    if type(glue) is str:
        if enum:
            return glue.join(map(lambda x: func(*x), enumerate(args)))
        else:
            return glue.join(map(func, args))
    elif callable(glue):
        fstr = StringIO()

        if enum:
            smap = zip(
                map(lambda x: glue(*x), enumerate(args)),
                map(lambda x: func(*x), enumerate(args)),
            )
        else:
            smap = zip(map(glue, args), map(func, args))

        for g, s in smap:
            fstr.write(f"{g}{s}")
        else:
            return fstr.getvalue()
    else:
        raise TypeError()

def arange(start: object, stop: object = None, step: object = None):
    """arange(stop) -> [0, 1, ..., stop]
    arange(start, stop) -> [start, start + 1, ..., stop]
    arange(start, stop, step) -> [start, start + step, ..., stop]
    """
    ## Value Checking
    if step == 0:
        raise ValueError("Step must be non-zero.")

    ## Defaults
    if stop is None:
        stop = start
        start = 0

    if step is None:
        if start > stop:
            step = -1
        elif start <= stop:
            step = 1

    ## A bit more Value Checking
    if start > stop and step > 0 or start < stop and step < 0:
        raise ValueError(f"Infinite range in [{start}:{stop}:{step}].")

    ## Type Coercing
    if any(type(s) is float for s in {start, stop, step}):
        x = float(start)
        stop = float(stop)
        step = float(step)
    elif any(type(s) is int for s in {start, stop, step}):
        x = int(start)
        stop = int(stop)
        step = int(step)
    else:
        x = start

    ## Iterator Loop
    if step > 0:
        while x <= stop:
            yield x
            x += step
    else:
        while x >= stop:
            yield x
            x += step

__all__ = ['arange', 'join', 'compose']