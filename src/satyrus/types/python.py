from .base import SatType
from ..satlib import Source

class PythonObject(SatType):
    """"""

    def __init__(self, obj: object, *, source: Source = None, lexpos: int = None):
        SatType.__init__(self, source=source, lexpos=lexpos)
        self.obj = obj

__all__ = ['PythonObject']