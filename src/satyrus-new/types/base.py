""" :: Sat Types ::
    ===============
"""
## Local
from ..satlib import Source, TrackType

class SatType(TrackType):
    """"""

    def __init__(self, *, source: Source = None, lexpos: int = None):
        if isinstance(source, Source):
            TrackType.__init__(self, source, lexpos)
        elif source is None:
            pass
        else:
            raise TypeError(f"Invalid type '{type(source)}' for 'source' argument.")

    @property
    def is_number(self) -> bool:
        return False

    @property
    def is_array(self) -> bool:
        return False

    @property
    def is_expr(self) -> bool:
        return False

    @property
    def is_var(self) -> bool:
        return False


__all__ = ["SatType"]