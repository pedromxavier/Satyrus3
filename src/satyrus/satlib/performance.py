from time import perf_counter as clock
from functools import wraps

from .stream import stdlog


class Timing:

    class Timer:

        def __init__(self, prec=2):
            self.pattern = f"Time elapsed @ {{}}:  {{:.{prec}f}}s"
            self.sections = {}

        def __call__(self, level: {int, callable}=0, section: str=None):
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
            return [(k, v) for k, v in self.sections.items() if k is not None]

    timeit = Timer()
