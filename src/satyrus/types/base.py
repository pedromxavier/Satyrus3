"""
"""
## Local
from ..satlib import Source


class MetaSatType(type):

    base_type = None

    def __new__(cls, name: str, bases: tuple, namespace: dict):
        if cls.base_type is None:
            if name == "SatType":
                cls.base_type = type(name, bases, namespace)
                return cls.base_type
            else:
                raise NotImplementedError(
                    f"'SatType must be implemented before '{name}'"
                )
        else:
            if name == "Number":
                cls.base_type.Number = type(name, bases, namespace)
                return cls.base_type.Number
            else:
                return type(name, bases, namespace)

class SatType(metaclass=MetaSatType):
    """"""

    def __init__(self, *, source: Source = None, lexpos: int = None):
        if isinstance(source, Source):
            source.track(self, lexpos)
        elif source is None:
            Source.blank(self)
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
