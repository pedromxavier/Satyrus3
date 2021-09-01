"""
"""
## Local
from ..satlib import Source, TrackType


class MetaSatType(type):

    __base_type__ = None

    def __new__(cls, name: str, bases: tuple, namespace: dict):
        if cls.__base_type__ is None:
            if name == "SatType":
                cls.__base_type__ = type.__new__(name, bases, namespace)
                return cls.__base_type__
            else:
                raise NotImplementedError(
                    f"'SatType must be implemented before '{name}'"
                )
        else:
            if name == "Number":
                cls.__base_type__.Number = type.__new__(name, bases, namespace)
                return cls.__base_type__.Number
            else:
                return type.__new__(name, bases, namespace)


class SatType(TrackType, metaclass=MetaSatType):
    """"""

    def __init__(self, *, source: Source = None, lexpos: int = None):
        if isinstance(source, Source):
            TrackType.__init__(self, source, lexpos)
        elif source is None:
            pass
        else:
            raise TypeError(f"Invalid type '{type(source)}' for 'source' argument")

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
