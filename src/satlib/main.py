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
from functools import wraps, reduce

os.path.join = posixpath.join

def kwget(key, kwargs : dict, default=None):
    try:
        return kwargs[key]
    except KeyError:
        return default

def load(fname : str, **kwargs):
    with open(fname, 'r', **kwargs) as file:
        return file.read()

def dump(fname : str, s : str, **kwargs):
    with open(fname, 'w', **kwargs) as file:
        file.write(s)

def pkload(fname : str, **kwargs):
    with open(fname, 'rb', **kwargs) as pkfile:
        while True:
            try:
                yield pickle.load(pkfile)
            except EOFError:
                break

def pkdump(fname : str, *args, **kwargs):
    with open(fname, 'wb', **kwargs) as pkfile:
        for obj in args:
            pickle.dump(obj, pkfile)

def threaded(callback):
    @wraps(callback)
    def new_callback(*args, **kwargs):
        return thread.start_new_thread(callback, args, kwargs)
    return new_callback

def func_type(cls):
    def decor(callback):
        @wraps(callback)
        def new_callback(*args, **kwargs):
            return cls(callback(*args, **kwargs))
        return new_callback
    return decor

def keep_type(callbacks : set):
    def class_decor(cls):
        ftype = func_type(cls)
        for name in callbacks:
            if hasattr(cls, name):
                setattr(cls, name, ftype(getattr(cls, name)))
        return cls
    return class_decor

def join(glue : str, args : list):
    return glue.join(map(str, args))

def log():
    return traceback.format_exc()

def arange(start, stop=None, step=None):
    """ arange(stop) -> [0, 1, ..., stop]
        arange(start, stop) -> [start, start + 1, ..., stop]
        arange(start, stop, step) -> [start, start + step, ..., stop]
    """
    ## Value Checking
    if step == 0:
        raise ValueError('Step must be non-zero.')

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
        raise ValueError('Infinite range.')

    ## Type Coercing
    if any(type(s) is float for s in {start, stop, step}):
        x = float(start)
        stop = float(stop)
        step = float(step)
    else:
        x = int(start)
        stop = int(stop)
        step = int(step)

    ## Iterator Loop
    if step > 0:
        while x <= stop:
            yield x
            x += step
    else:
        while x >= stop:
            yield x
            x += step