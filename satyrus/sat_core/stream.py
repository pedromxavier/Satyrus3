import colorama

class stream:

    ECHO = True

    def __init__(self, **kwargs):
        self.echo = True

        self.kw = kwargs['kw'] if 'kw' in kwargs else {}
        self.fg = kwargs['fg'] if 'fg' in kwargs else None
        self.sty = kwargs['sty'] if 'sty' in kwargs else None

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
            fg = getattr(colorama.Fore, fg);sty = getattr(colorama.Style, sty)
            print(f"{fg}{sty}", *txt, f"{colorama.Style.RESET_ALL}", **kwargs)

    def __lshift__(self, txt):
        if self.echo and self.ECHO:
            if type(txt) is not tuple:
                txt = (txt,)
            stream.cprint(txt, self.fg, self.sty, **self.kw)
        return self

    def __pos__(self):
        if self.echo and self.ECHO: print()

    def __neg__(self):
        if self.echo and self.ECHO: print()

    def __invert__(self):
        if self.echo and self.ECHO: print()

    def echo_off(self):
        self.echo = False

    def echo_on(self):
        self.echo = True

    @classmethod
    def ECHO_OFF(cls):
        cls.ECHO = False

    @classmethod
    def ECHO_ON(cls):
        cls.ECHO = True

colorama.init()

## default stream configs
__stdsys__ = { 'fg' : 'BLUE', 'sty' : 'DIM'}
__stdout__ = { 'fg' : 'CYAN', 'sty' : None }
__stderr__ = { 'fg' : 'RED' , 'sty' : None }

stdsys = stream(**__stdsys__)
stdout = stream(**__stdout__)
stderr = stream(**__stderr__)