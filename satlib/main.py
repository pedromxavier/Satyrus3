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
from collections import deque
from functools import wraps, reduce

def init_system():
    global os
    if sys.platform != 'win32':
        os.path.join = posixpath.join
    else:
        os.sep = '\\'

def kwget(key, kwargs : dict, default=None):
    try:
        return kwargs[key]
    except KeyError:
        return default

def load(fname : str, **kwargs):
    with open(fname, 'r', **kwargs) as file:
        return file.read()

def dump(fname : str, s : str):
    with open(fname, 'w') as file:
        file.write(s)

def pkload(fname : str):
    with open(fname, 'rb') as pkfile:
        while True:
            try:
                yield pickle.load(pkfile)
            except EOFError:
                break

def pkdump(fname : str, *args):
    with open(fname, 'wb') as pkfile:
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

def log(data):
    raise NotImplementedError('Error Logging is under the way...')

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

class Stack:

    def __init__(self, buffer=None, limit=None):
        self.__stack = deque([] if buffer is None else buffer, limit)

    def add(self, x):
        return self.__stack.append(x)

    def pop(self):
        return self.__stack.pop()

    def __iter__(self):
        return iter(self.__stack)

    def __bool__(self):
        return bool(self.__stack)

