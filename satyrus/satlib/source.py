## Standard Library
from functools import wraps
import itertools as it

## Local
from .main import load

class Source(str):

    def __new__(self, fname : str):
        return str.__new__(self, load(fname))

    def __repr__(self):
        return f"<source @ {self.fname}>"

    def __init__(self, fname : str):
        self.fname = fname
        self.lines = [''] + str.split(self, '\n')
        self.table = list(it.accumulate([len(line) + 1 for line in self.lines]))

    @staticmethod
    def load(fname : str):
        return Source(fname)

    @property
    def eof(self):
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
        name = 'SAT_EOF'
        bases = (object,)
        attrs = {**lexinfo, 'lexinfo': lexinfo}

        return type(name, bases, attrs)()

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