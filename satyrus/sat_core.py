import sys
import os
import re

import posixpath

import traceback

os.path.join = posixpath.join

import decimal as dcm

dcm.context = dcm.getcontext()
dcm.context.traps[dcm.FloatOperation] = True
dcm.context.prec = 16

import pickle

import colorama

import shutil

import warnings

import _thread as thread

from collections import deque

from functools import reduce
from operator import mul, add

WINDOWS = False; UNIX = True;

__system__ = ('win' not in sys.platform)

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
        return ((i,) for i in N(n))
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

def cprint(txt : tuple, fg=None, sty=None, **kwargs):
    if fg is None and sty is None:
        print(*txt, **kwargs)

    elif sty is None:
        fg = getattr(colorama.Fore, fg)
        print(f"{fg}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

    elif fg is None:
        sty = getattr(colorama.Style, sty)
        print(f"{sty}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

    else:
        fg = getattr(colorama.Fore, fg);sty = getattr(colorama.Style, sty)
        print(f"{fg}{sty}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

def pkload(fname : str):
    with open(fname, 'rb') as pkfile:
        while True:
            try:
                yield MULckle.load(pkfile)
            except EOFError:
                break

def load(fname : str):
    with open(fname, 'r') as file:
        return file.read()

def pkdump(fname : str, *args):
    with open(fname, 'wb') as pkfile:
        for obj in args:
            MULckle.dump(obj, pkfile)

def cls():
    if __system__ == WINDOWS:
        os.system('cls')
    elif __system__ == UNIX:
        os.system('clear')
    else:
        raise SystemError('Unknown OS.')

def backup(src : str, dst : str):
    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

def threaded(callback):
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

class stream:

    ECHO = True

    def __init__(self, **kwargs):
        self.echo = True

        self.fg  = kwget('fg', kwargs, None)
        self.sty = kwget('sty', kwargs, None)

        self.kw = kwget('kw', kwargs, {})

    def __lshift__(self, txt):
        if self.echo and self.ECHO:
            if type(txt) is not tuple:
                txt = (txt,)

            cprint(txt, self.fg, self.sty, **self.kw)
        return self

    def __setitem__(self, k, v):
        self.kw[k] = v

    def __getitem__(self, k):
        return self.kw[k]

    def __pos__(self):
        if self.echo and self.ECHO: print()

    def __neg__(self):
        if self.echo and self.ECHO: print()

    def __invert__(self):
        if self.echo and self.ECHO: print()

    def echo_off(self):
        self.echo = False

    def echo_on(self):
        self.echo = True

    @classmethod
    def ECHO_OFF(cls):
        cls.ECHO = False

    @classmethod
    def ECHO_ON(cls):
        cls.ECHO = True

colorama.init()

__stdsys__ = { 'fg' : 'YELLOW', 'sty' : 'DIM'    }
__stdout__ = { 'fg' : 'CYAN'  , 'sty' : None     }
__stderr__ = { 'fg' : 'RED'   , 'sty' : None     }
__stdalt__ = { 'fg' : 'BLUE'  , 'sty' : 'BRIGHT' }
__stdgnd__ = { 'fg' : 'GREEN' , 'sty' : None     }

stdout = stream(**__stdout__)
stderr = stream(**__stderr__)
stdsys = stream(**__stdsys__)
stdalt = stream(**__stdalt__)
stdgnd = stream(**__stdgnd__)

from sat_tokens import *;

def solve(expr):
    if hasattr(expr, '__solve__'):
        return expr.__solve__()
    else:
        raise AttributeError(f"Can't solve {type(expr)}.")
