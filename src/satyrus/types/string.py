from .base import SatType
from ..satlib import Source

class String(SatType, str):
    """ 
    Parameters
    ----------
    buffer : str
    """
    def __new__(cls, buffer: str, source: Source = None, lexpos: int = None):
        return str.__new__(cls, buffer)

    def __init__(self, buffer: str, source: Source = None, lexpos: int = None):
        SatType.__init__(self, source=source, lexpos=lexpos)