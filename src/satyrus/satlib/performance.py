# Standard Library
from time import perf_counter as clock
from functools import wraps

# Third-Party
from cstream import stdlog


class Timing(object):
    """"""

    class Timer(object):
        """"""

        ARROW = "■"
        BAR = "■"
        BARS = 25

        def __init__(self, prec=2, *, bar: str = None, arrow: str = None):
            self.pattern = f"Time elapsed @ {{}}:  {{:.{prec}f}}s"
            self.sections = {}

        def __call__(self, level: int = 0, section: str = None):
            if type(level) is int or section is not None:

                def decor(callback: callable) -> callable:
                    @wraps(callback)
                    def timed_callback(*args, **kwargs):
                        t = clock()
                        _ = callback(*args, **kwargs)
                        T = clock() - t
                        self.sections[section] = T
                        stdlog[level] << self.pattern.format(section, T)
                        return _

                    return timed_callback

                return decor
            elif callable(level):
                callback = level

                @wraps(callback)
                def timed_callback(*args, **kwargs):
                    t = clock()
                    _ = callback(*args, **kwargs)
                    T = clock() - t
                    self.sections[section] = T
                    stdlog[level] << self.pattern.format(section, T)
                    return _

                return timed_callback
            else:
                raise TypeError("Place some info here.")

        def reset(self):
            self.sections.clear()

        def report(self):
            return [(k, t) for k, t in self.sections.items() if k is not None]

        def show_report(self, level: int = 0):
            R = self.report()
            L = max(len(k) for k, _ in R)
            T = sum(t for _, t in R)
            stdlog[level] << f"Time elapsed: {T:.2f}s"
            for k, t in R:
                stdlog[level] << f"{self.__fill(k, L)}\t{self.__bar(t, T)}"

        @classmethod
        def __fill(cls, k: str, L: int):
            l = len(k)
            return k + " " * (L - l)

        @classmethod
        def __bar(cls, t: float, T: float):
            x = (t / T) if T else 0.0
            return f"[{cls.__full(x)}{cls.ARROW}{cls.__empty()}]{t:6.2f}s ({x * 100.0:6.2f}%)"

        @classmethod
        def __full(cls, x: float) -> str:
            return cls.BAR * int(cls.BARS * x - 1.0)

        @classmethod
        def __empty(cls, x: float) -> str:
            return " " * int(cls.BARS * (1.0 - x))

    timer = Timer()


__all__ = ["Timing"]
