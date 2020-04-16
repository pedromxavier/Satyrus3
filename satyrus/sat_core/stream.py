import colorama

class stream(object):

    __ref__ = {}
    __lvl__ = None

    def __new__(cls, fg, sty, level=0, **kwargs):
        if (fg, sty, level) not in cls.__ref__:
            cls.__ref__[(fg, sty, level)] = object.__new__(cls)
        return cls.__ref__[(fg, sty, level)]
        
    def __init__(self, fg, sty, level=0, **kwargs):
        self.fg = fg
        self.sty = sty
        self.level = level
        self.kwargs = kwargs

    @staticmethod
    def cprint(txt : tuple, fg : str = None, sty : str = None, **kwargs):
        if fg is None and sty is None:
            print(*txt, **kwargs)

        elif sty is None:
            fg = getattr(colorama.Fore, fg)
            print(f"{fg}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

        elif fg is None:
            sty = getattr(colorama.Style, sty)
            print(f"{sty}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

        else:
            fg = getattr(colorama.Fore, fg)
            sty = getattr(colorama.Style, sty)
            print(f"{fg}{sty}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

    def __lshift__(self, txt):
        if self.__lvl__ is None or self.level <= self.__lvl__:
            txt = (txt,) if type(txt) is not tuple else txt
            stream.cprint(txt, self.fg, self.sty, **self.kwargs)
        return None
    
    def __getitem__(self, level):
        return stream(self.fg, self.sty, level, **self.kwargs)

    @classmethod
    def set_lvl(cls, level : int):
        cls.__lvl__ = level

colorama.init()

## default stream configs
stdsys = stream('GREEN', 'DIM')
stdout = stream('CYAN', None)
stderr = stream('RED', None)