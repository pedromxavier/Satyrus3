from .main import SatType

class NULL(SatType, object):

    __ref__ = None

    def __new__(cls):
        if cls.__ref__ is None:
            cls.__ref__ = object.__new__(cls)
        return cls.__ref__
        
    def __idx__(self, idx):
        return self

    