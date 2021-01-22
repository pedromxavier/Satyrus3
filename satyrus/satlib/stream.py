"""
"""
## Standard Library
import sys
from collections import namedtuple

## Third-Party
import colorama

class _stream(object):
    """ stream(level=0, bg=..., fg=..., )

        Examples:
        >>> stream.set_lvl(0)
        >>> stream[1] << "Hello."
        >>> stream[0] << "Hello."
        Hello.
        >>> stream << "Hello."
        Hello.
    """

    COLORS = {"BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", None}
    STYLES = {"DIM", "NORMAL", "BRIGHT", None}

    RESET = colorama.Style.RESET_ALL

    Params = namedtuple('params', ['bg', 'fg', 'sty', 'file'], defaults=[None, None, None, sys.stdout])

    __ref__ = {}
    __lvl__ = None

    def __new__(cls, lvl: int=0, **kwargs: dict):
        ## Gather parameters
        params = cls.Params(**kwargs)

        ## Check Background
        if params.bg not in cls.COLORS:
            raise ValueError(f'Color {params.bg} not available.\nOptions: {cls.COLORS}')
        ## Check Foreground
        if params.fg not in cls.COLORS:
            raise ValueError(f'Color {params.fg} not available.\nOptions: {cls.COLORS}')
        ## Check Style
        if params.sty not in cls.STYLES:
            raise ValueError(f'Style {params.sty} not available.\nOptions: {cls.STYLES}')

        if params not in cls.__ref__:
            cls.__ref__[params] = super().__new__(cls)
        return cls.__ref__[params]

    def __init__(self, lvl: int=0, **kwargs: dict):
        ## Set lvl
        self.lvl = lvl

        ## Gather parameters
        bg, fg, sty, file = self.params = self.Params(**kwargs)

        ## Gather escape sequences
        self.bg = "" if bg is None else getattr(colorama.Back, bg)
        self.fg = "" if fg is None else getattr(colorama.Fore, fg)
        self.sty = "" if sty is None else getattr(colorama.Style, sty)

        ## Set output file
        self.file = file

    def __repr__(self):
        params = ", ".join([f"{key}={getattr(self.params, key)!r}" for key in ('bg', 'fg', 'sty')])
        return f"{self.__class__.__name__}({self.lvl}, {params})"

    def printf(self, *args, **kwargs):
        if self.echo: self._printf(*args, **kwargs)

    def _printf(self, *args, **kwargs):
        print(self.bg, self.fg, self.sty, sep="", end="", file=self.file)
        print(*args, **kwargs, file=self.file)
        print(self.RESET, sep="", end="", file=self.file)

    def string(self, s: str):
        return f"{self.bg}{self.fg}{self.sty}{s}{self.RESET}"

    def __lshift__(self, s: str):
        if self.echo: print(self.string(s), file=self.file)
    
    def __getitem__(self, lvl: int):
        return self.__class__(lvl, **self.params._asdict())

    def __call__(self, **kwargs):
        return self.__class__(self.lvl, **kwargs)

    ## File interface
    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *args):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def write(self, s: str, *args, **kwargs):
        self.printf(s, **kwargs)
    ## File interface

    @property
    def echo(self):
        return (self.__lvl__ is None) or (self.__lvl__ >= self.lvl)

    @classmethod
    def set_lvl(cls, lvl : int = None):
        if lvl is None or type(lvl) is int:
            cls.__lvl__ = lvl
        else:
            raise TypeError(f'Invalid type `{type(lvl)}`` for debug lvl. Must be `int`.')
            
stream = _stream()
colorama.init()

stderr = stream(fg='RED', file=sys.stderr)
stdwar = stream(fg='YELLOW', file=sys.stderr)
stdout = stream(fg='CYAN', sty='BRIGHT', file=sys.stdout)