"""
"""
# Future Imports
from __future__ import annotations

# Local
from ..satlib import Source
from ..symbols import (
    T_NOT,
    T_AND,
    T_OR,
    T_IMP,
    T_IFF,
    T_RIMP,
    T_EQ,
    T_NE,
    T_LT,
    T_LE,
    T_GT,
    T_GE,
    T_IDX,
)


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
            elif name == "Expr":
                cls.base_type.Expr = type(name, bases, namespace)
                # -*- Some Magic -*- A-bra-ca-da-bra -*-
                cls.base_type.Expr.RULES.update(cls.base_type.Expr.get_rules())
                return cls.base_type.Expr
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

    # -*- Operator Definition -*-

    # :: Logical
    def _NOT_(self) -> SatType:
        return self.__class__.Expr(T_NOT, self)

    def _AND_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_AND, self, other)

    def _OR_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_OR, self, other)

    def _IMP_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_IMP, self, other)

    def _IFF_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_IFF, self, other)

    def _RIMP_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_RIMP, self, other)

    # :: Comparison
    def _EQ_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_EQ, self, other)

    def _NE_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_NE, self, other)

    def _LT_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_LT, self, other)

    def _LE_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_LE, self, other)

    def _GT_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_GT, self, other)

    def _GE_(self, other: SatType) -> SatType:
        return self.__class__.Expr(T_GE, self, other)

    # :: Indexing
    def _IDX_(self, i: tuple) -> SatType:
        return self.__class__.Expr(T_IDX, self, *i)


__all__ = ["SatType"]
