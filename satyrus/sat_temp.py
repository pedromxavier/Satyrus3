from sat_types import *;

class TempConst(object):

    def __init__(self, name):
        self.name = name

    def compile(self, engine):
        if self.name in engine:
            return engine[self.name]
        else:
            raise SatCompilation_Error(error_msg)

class TempArray(object):

    def __init__(self, name, size, buffer):
        self.name = name
        self.size = size
        self.buffer = buffer


    def compile(self, engine):
        ...
