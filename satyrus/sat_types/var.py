from .main import SatType

class Var(SatType, str):

    __ref__ = {} # works as 'intern'

    def __new__(cls, name):
        if name not in cls.__ref__:
            obj = str.__new__(cls, name)
            cls.__ref__[name] = obj
        return cls.__ref__[name]

    def __hash__(self):
        return str.__hash__(self)

    def __repr__(self):
        return f"Var('{self}')"

    def __idx__(self, i):
        return Var(f"{self}_{i}")

    @property
    def tail(self):
        return None

    @property
    def vars(self):
        return {self}

    @property
    def expr(self):
        return False

    @property
    def var(self):
        return True