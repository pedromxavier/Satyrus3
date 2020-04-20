import colorama

class stream(object):

    __ref__ = {}
    __lvl__ = None

    KWARGS = {
        'sep' : ' ',
        'end' : '\n',
    }

    def __new__(cls, fg, sty, level=0, **kwargs):
        if (fg, sty, level) not in cls.__ref__:
            cls.__ref__[(fg, sty, level)] = object.__new__(cls)
        return cls.__ref__[(fg, sty, level)]
        
    def __init__(self, fg, sty, level=0, **kwargs):
        self.fg = fg
        self.sty = sty
        self.level = level
        self.kwargs = self.KWARGS.copy()
        self.kwargs.update(kwargs)

    @staticmethod
    def cstring(txt : tuple, fg : str = None, sty : str = None, **kwargs):
        string = kwargs['sep'].join(map(str, txt))

        if not (fg is None and sty is None):
            fg = "" if fg is None else getattr(colorama.Fore, fg)
            sty = "" if sty is None else getattr(colorama.Style, sty)
            string = f"{fg}{sty}{string}{colorama.Style.RESET_ALL}"

        return string
            
    @staticmethod
    def cprint(txt : tuple, fg : str = None, sty : str = None, **kwargs):
        string = stream.cstring(txt, fg, sty, **kwargs)
        print(string, end=kwargs['end'])

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