from .main import SatType

class String(SatType, str):
    
    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        SatType.__init__(self)