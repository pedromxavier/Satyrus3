## Standard Library
from functools import wraps
import itertools as it
import os

## Local
from .main import load

class EOFType(object):

    def __init__(self, lexinfo: dict):
        ## Add tracking information
        self.lineno = lexinfo['lineno']
        self.lexpos = lexinfo['lexpos']
        self.chrpos = lexinfo['chrpos']
        self.source = lexinfo['source']

        self.lexinfo = lexinfo

class Source(str):
    """ This source code object aids the tracking of tokens in order to
        indicate error position on exception handling.
    """

    def __new__(cls, fname :str, buffer: str=None):
        """ This object is a string itself with additional features for
            position tracking.
        """
        if fname is not None:
            return str.__new__(cls, load(fname))
        else:
            return str.__new__(cls, buffer)


    def __repr__(self):
        return f"<source @ {self.fname}>"

    def __bool__(self):
        """ Truth-value for emptiness checking.
        """
        return (str(self) != "")

    def __init__(self, fname : str, buffer: str=None):
        """ Separates the source code in multiple lines. First line is discarded for
            the indexing to start at 1 instead of 0. `self.table` keeps track of the
            (cumulative) character count.
        """
        self.fname = os.path.abspath(fname) if (fname is not None) else "string"
        self.lines = ['', *str.split(self, '\n')]
        self.table = list(it.accumulate([(len(line) + 1) for line in self.lines]))

    @classmethod
    def from_str(cls, buffer: str):
        return cls(None, buffer=buffer)

    @staticmethod
    def load(fname : str):
        return Source(fname)

    @property
    def eof(self):
        """ Virtual object to represent the End-of-File for the given source
            object. It's an anonymously created 
        """

        ## SatType lexinfo interface
        lineno = len(self.lines) - 1
        lexpos = len(self.lines[lineno]) - 1
        chrpos = (lexpos - self.table[lineno - 1] + 1)

        lexinfo = {
            'lineno': lineno,
            'lexpos': lexpos,
            'chrpos' : chrpos,
            'source' : self
        }

        ## Anonymous object
        return EOFType(lexinfo)

def trackable(cls: type):

    init_func = cls.__init__
    
    @wraps(init_func)
    def __init__(self, *args, **kwargs):
        init_func(self, *args, **kwargs)
        setattr(self, 'lexinfo', {
            'lineno': 0,
            'lexpos': 0,
            'chrpos': 0,
            'source': None
        })

    setattr(cls, '__init__', __init__)

    setattr(cls, 'lineno', property(lambda self: getattr(self, 'lexinfo')['lineno']))
    setattr(cls, 'lexpos', property(lambda self: getattr(self, 'lexinfo')['lexpos']))
    setattr(cls, 'chrpos', property(lambda self: getattr(self, 'lexinfo')['chrpos']))
    setattr(cls, 'source', property(lambda self: getattr(self, 'lexinfo')['source']))

    return cls

def track(from_: object, to_: object):
    if hasattr(from_, 'lexinfo'):
        if hasattr(to_, 'lexinfo'):
            from_.lexinfo.update(to_.lexinfo)
        else:
            raise AttributeError('`to_` is not trackable, i.e. has no attribute `lexinfo`.')
    else:
        raise AttributeError('`from_` is not trackable, i.e. has no attribute `lexinfo`.')