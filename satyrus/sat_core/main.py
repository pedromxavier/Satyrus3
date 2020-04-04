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

os.path.join = posixpath.join

def kwget(key, kwargs : dict, default=None):
    try:
        return kwargs[key]
    except KeyError:
        return default

def load(fname : str):
    with open(fname, 'r') as file:
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

def trackable(cls : type):
    @wraps(cls)
    class new_cls(cls):
        def __init__(self, *args, **kwargs):
            cls.__init__(self, *args, **kwargs)
            self.lineno = None
            self.lexpos = None
            self.chrpos = None
    return new_cls

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

