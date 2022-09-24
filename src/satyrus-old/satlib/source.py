"""
"""
# Future Imports
from __future__ import annotations

# Standard Library
import itertools as it
from pathlib import Path


class Source(str):
    """This source code object aids the tracking of tokens in order to
    indicate error position on exception handling.
    """

    LEXKEYS = {"lexpos", "chrpos", "lineno", "source"}

    def __new__(
        cls,
        *,
        fname: str = None,
        buffer: str = None,
        offset: int = 0,
        length: int = None,
    ):
        """This object is a string itself with additional features for
        position tracking.
        """
        if fname is not None and buffer is not None:
            raise ValueError(
                "Can't work with both 'fname' and 'buffer' parameters, choose one option."
            )

        elif fname is not None:
            if not isinstance(fname, (str, Path)):
                raise TypeError(
                    f"Invalid type '{type(fname)}' for 'fname'. Must be 'str' or 'Path'."
                )

            fpath = Path(fname)

            if not fpath.exists() or not fpath.is_file():
                raise FileNotFoundError(f"Invalid file path '{fname}'.")

            with open(fpath, mode="r", encoding="utf-8") as file:
                return super(Source, cls).__new__(cls, file.read())

        elif buffer is not None:
            if not isinstance(buffer, str):
                raise TypeError(
                    f"Invalid type '{type(buffer)}' for 'buffer'. Must be 'str'."
                )

            return super(Source, cls).__new__(cls, buffer)
        else:
            raise ValueError("Either 'fname' or 'buffer' must be provided.")

    def __init__(
        self,
        *,
        fname: str = None,
        buffer: str = None,
        offset: int = 0,
        length: int = None,
    ):
        """Separates the source code in multiple lines. A blank first line is added for the indexing to start at 1 instead of 0. `self.table` keeps track of the (cumulative) character count."""
        if not isinstance(offset, int) or offset < 0:
            raise TypeError("'offset' must be a positive integer (int).")
        elif length is None:
            length = len(self)
        elif not isinstance(length, int) or length < 0:
            raise TypeError("'length' must be a positive integer (int) or 'None'.")

        self.offset = min(offset, len(self))
        self.length = min(length, len(self) - self.offset)

        self.fpath = (
            Path(fname).resolve(strict=True) if (fname is not None) else "<string>"
        )
        self.lines = [""] + self.split("\n")
        self.table = list(it.accumulate([(len(line) + 1) for line in self.lines]))

    def __str__(self):
        return self[self.offset : self.offset + self.length]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.fpath!r})"

    def __bool__(self):
        """Truth-value for emptiness checking."""
        return self.__len__() > 0

    def getlex(self, lexpos: int = None) -> dict:
        """Retrieves lexinfo dictionary from lexpos."""
        if lexpos is None:
            return self.eof.lexinfo
        elif not isinstance(lexpos, int):
            raise TypeError(f"'lexpos' must be an integer (int), not ({type(lexpos)}).")
        elif not 0 <= lexpos <= self.length:
            return self.eof.lexinfo

        lexpos = lexpos + self.offset + 1

        lineno = 1
        while lineno < len(self.table) and lexpos >= self.table[lineno]:
            lineno += 1

        if lineno == len(self.table):
            return self.eof.lexinfo
        else:
            return {
                "lineno": lineno,
                "lexpos": lexpos,
                "chrpos": lexpos - self.table[lineno - 1],
                "source": self,
            }

    def slice(self, offset: int = 0, length: int = None):
        return self.__class__(fname=self.fpath, offset=offset, length=length)

    def error(self, msg: str, *, target: object = None, name: str = None):
        if target is None or not self.trackable(target):
            if name is not None:
                return f"In '{self.fpath}':\n" f"{name}: {msg}\n"
            else:
                return f"In '{self.fpath}':\n" f"{msg}\n"
        else:
            if name is not None:
                return (
                    f"In '{self.fpath}' at line {target.lineno}:\n"
                    f"{self.lines[target.lineno]}\n"
                    f"{' ' * target.chrpos}^\n"
                    f"{name}: {msg}\n"
                )
            else:
                return (
                    f"In '{self.fpath}' at line {target.lineno}:\n"
                    f"{self.lines[target.lineno]}\n"
                    f"{' ' * target.chrpos}^\n"
                    f"{msg}\n"
                )

    class EOF(object):
        pass

    @property
    def eof(self):
        """Virtual object to represent the End-of-File for the given source
        object. It's an anonymously created EOFType instance.
        """
        eof = self.EOF()

        self.track(eof, len(self))

        return eof

    # -*- Tracking -*-
    def track(self, o: object, lexpos: int = None):
        """"""
        setattr(o, "lexinfo", self.getlex(lexpos))

        if not hasattr(o.__class__, "__lextrack__"):
            setattr(
                o.__class__, "chrpos", property(lambda this: this.lexinfo["chrpos"])
            )
            setattr(
                o.__class__, "lineno", property(lambda this: this.lexinfo["lineno"])
            )
            setattr(
                o.__class__, "lexpos", property(lambda this: this.lexinfo["lexpos"])
            )
            setattr(
                o.__class__, "source", property(lambda this: this.lexinfo["source"])
            )
            setattr(o.__class__, "__lextrack__", None)

    @classmethod
    def blank(cls, o: object):
        setattr(o, "lexinfo", {"chrpos": 0, "lineno": 0, "lexpos": 0, "source": None})

        if not hasattr(o.__class__, "__lextrack__"):
            setattr(
                o.__class__, "chrpos", property(lambda this: this.lexinfo["chrpos"])
            )
            setattr(
                o.__class__, "lineno", property(lambda this: this.lexinfo["lineno"])
            )
            setattr(
                o.__class__, "lexpos", property(lambda this: this.lexinfo["lexpos"])
            )
            setattr(
                o.__class__, "source", property(lambda this: this.lexinfo["source"])
            )
            setattr(o.__class__, "__lextrack__", None)

    def propagate(self, x: object, y: object, *, out: bool = False) -> object | None:
        if self.trackable(x, strict=True) and self.trackable(y):
            y.lexinfo.update(x.lexinfo)
            if out:
                return y
            else:
                return None
        else:
            raise TypeError(
                f"Can't propagate lexinfo between types {type(x)} and {type(y)}"
            )

    @classmethod
    def trackable(cls, o: object, *, strict: bool = False):
        if cls._trackable(o):
            return True
        elif strict:
            print(o, o.lexinfo)
            raise TypeError(f"Object '{o}' of type '{type(o)}' is not trackable.")
        else:
            return False

    @classmethod
    def _trackable(cls, o: object):
        if not hasattr(o, "lexinfo") or not isinstance(o.lexinfo, dict):
            return False
        else:
            if any(key not in o.lexinfo for key in cls.LEXKEYS):
                return False
            else:
                if (
                    not hasattr(o, "lineno")
                    or not isinstance(o.lineno, int)
                    or o.lineno < 0
                ):
                    return False
                elif (
                    not hasattr(o, "lexpos")
                    or not isinstance(o.lexpos, int)
                    or o.lexpos < 0
                ):
                    return False
                elif (
                    not hasattr(o, "chrpos")
                    or not isinstance(o.chrpos, int)
                    or o.chrpos < 0
                ):
                    return False
                elif (
                    not hasattr(o, "source")
                    or not isinstance(o.source, Source)
                    and not o.source is None
                ):
                    return False
                else:
                    return True


__all__ = ["Source"]
