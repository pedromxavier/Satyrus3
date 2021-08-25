## Standard Library
import itertools as it
from pathlib import Path

class Source(str):
    """This source code object aids the tracking of tokens in order to
    indicate error position on exception handling.
    """

    def __new__(cls, *, fname: str = None, buffer: str = None, offset: int = 0, length: int = None):
        """This object is a string itself with additional features for
        position tracking.
        """
        if fname is not None and buffer is not None:
            raise ValueError("Can't work with both 'fname' and 'buffer' parameters, choose one option.")

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

    def __init__(self, *, fname: str = None, buffer: str = None, offset: int = 0, length: int = None):
        """Separates the source code in multiple lines. A blank first line is added for the indexing to start at 1 instead of 0. `self.table` keeps track of the (cumulative) character count."""
        if not isinstance(offset, int) or offset < 0:
            raise TypeError("'offset' must be a positive integer (int).")
        elif length is None:
            length = len(self)
        elif not isinstance(length, int) or length < 0:
            raise TypeError("'length' must be a positive integer (int) or 'None'.")

        self.offset = min(offset, len(self))
        self.length = min(length, len(self) - self.offset)

        self.fpath = Path(fname).resolve(strict=True) if (fname is not None) else "<string>"
        self.lines = [""] + self.split("\n")
        self.table = list(it.accumulate([(len(line) + 1) for line in self.lines]))


    def __str__(self):
        return self[self.offset:self.offset+self.length]

    def __repr__(self):
        return f"Source @ '{self.fpath}'"

    def __bool__(self):
        """Truth-value for emptiness checking."""
        return self.__len__() > 0

    def getlex(self, lexpos: int = None) -> dict:
        """Retrieves lexinfo dictionary from lexpos."""
        if lexpos is None:
            return self.eof.lexinfo
        elif not isinstance(lexpos, int):
            raise TypeError("'lexpos' must be an integer (int).")
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
                'lineno': lineno,
                'lexpos': lexpos,
                'chrpos': lexpos - self.table[lineno - 1],
                'source': self,
            }

    def slice(self, offset: int = 0, length: int = None):
        return self.__class__(fname=self.fpath, offset=offset, length=length)

    def error(self, msg: str, *, target: object = None, name: str = None):
        if target is None or not TrackType.trackable(target):
            if name is not None:
                return (
                        f"In '{self.fpath}':\n"
                        f"{name}: {msg}\n"
                    )
            else:
                return (
                        f"In '{self.fpath}':\n"
                        f"{msg}\n"
                    )
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

    @property
    def eof(self):
        """Virtual object to represent the End-of-File for the given source
        object. It's an anonymously created EOFType instance.
        """
        ## Anonymous object
        return TrackType(self, len(self))

class TrackType(object):

    KEYS = {'lexpos', 'chrpos', 'lineno', 'source'}
    
    def __init__(self, source: Source, lexpos: int):
        ## Add tracking information
        self.lexinfo: dict = source.getlex(lexpos)

    @classmethod
    def trackable(cls, o: object, *, strict: bool = False):
        if cls._trackable(o):
            return True
        elif strict:
            raise TypeError(f"Object '{o}' of type '{type(o)}' is not trackable.")
        else:
            return False

    @classmethod
    def _trackable(cls, o: object):       
        if not hasattr(o, 'lexinfo') or not isinstance(o.lexinfo, dict):
            return False
        else:
            if any(key not in o.lexinfo for key in cls.KEYS):
                return False
            else:
                if not hasattr(o, 'lineno') or not isinstance(o.lineno, int) or o.lineno < 0:
                    return False
                elif not hasattr(o, 'lexpos') or not isinstance(o.lexpos, int) or o.lexpos < 0:
                    return False
                elif not hasattr(o, 'chrpos') or not isinstance(o.chrpos, int) or o.chrpos < 0:
                    return False
                elif not hasattr(o, 'source') or not isinstance(o.source, Source):
                    return False
                else:
                    return True
                
    @property
    def lineno(self):
        return self.lexinfo['lineno']

    @property
    def lexpos(self):
        return self.lexinfo['lexpos']

    @property
    def chrpos(self):
        return self.lexinfo['chrpos']

    @property
    def source(self):
        return self.lexinfo['source']


__all__ = ["Source", "TrackType"]