## Standard Library
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