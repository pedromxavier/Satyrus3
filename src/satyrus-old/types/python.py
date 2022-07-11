from .base import SATType
from ..satlib import Source

class PythonObject(SATType):
    """"""

    def __init__(self, obj: object, *, source: Source = None, lexpos: int = None):
        SATType.__init__(self, source=source, lexpos=lexpos)
        self.obj = obj

__all__ = ['PythonObject']