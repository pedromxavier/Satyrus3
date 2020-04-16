from .main import SatType

class Var(SatType, str):

    __ref__ = {} # works as 'intern'

    def __new__(cls, name : str):
        if name not in cls.__ref__:
            obj = str.__new__(cls, name)
            cls.__ref__[name] = obj
        return cls.__ref__[name]

    def __init__(self, name : str):
        SatType.__init__(self)

    def __hash__(self):
        return str.__hash__(self)

    def __repr__(self):
        return f"Var('{self}')"

    def __idx__(self, i):
        return Var(f"{self}_{i}")