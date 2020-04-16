## Standard Library
import itertools as it

## Local
from .main import load

class Source(str):

    def __init__(self, fname : str):
        str.__init__(self, load(fname))
        self.fname = fname
        self.lines = str.split(self, '\n')
        self.table = list(it.accumulate([len(line) for line in self.lines]))

    @staticmethod
    def load(fname : str):
        return Source(fname)