import sys
import os
import re

import posixpath
import traceback

os.path.join = posixpath.join

import pickle

import shutil

import warnings

import _thread as thread

from collections import deque

from functools import wraps, reduce
from operator import mul, add

def product(*args):
    if len(args) == 1:
        return _product(args[0])
    else:
        return _product(args)

def _product(args):
    return reduce(mul, args)

def summation(*args):
    if len(args) == 1:
        return _summation(args[0])
    else:
        return _summation(args)

def _summation(args):
    return reduce(add, args)

SUM = summation
MUL = product

def S(n : int, k : int):
    if not k:
        return ((i,) for i in range(1, n+1))
    else:
        return ((*I, j) for I in S(n, k-1) for j in range(I[k-1]+1, n))

def OMEGA(x : tuple, n : int, k : int):
    return SUM(MUL(x[i] for i in I) for I in S(n,k))

def OR(x : tuple):
    n = len(x)
    return SUM(pow(-1, k) * OMEGA(x, n, k) for k in range(n))

def XOR(x : tuple):
    n = len(x)
    return SUM(pow(-1, k) * (k+1) * OMEGA(x, n, k) for k in range(n))

def AND(x : tuple):
    return MUL(x)

def py_error():
    return traceback.format_exc()

def kwget(key, kwargs : dict, default=None):
    try:
        return kwargs[key]
    except KeyError:
        return default

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

class Stack:

    def __init__(self, buffer=None, limit=None):
        self.stack = deque([] if buffer is None else buffer, limit)

    def add(self, x):
        return self.stack.append(x)

    def pop(self):
        return self.stack.pop()

    def __iter__(self):
        return iter(self.stack)

    def __bool__(self):
        return bool(self.stack)

    def __str__(self):
        return "[{}]".format(", ".join(list(self.stack)))