from dataclasses import dataclass

from ...types import String, Var, Expr

@dataclass
class Loop:
    type: String
    var: Var
    bounds: tuple
    cond: Expr

    def __iter__(self):
        return iter([self.type, self.var, self.bounds, self.cond])

    def __str__(self):
        start, stop, step = self.bounds
        return f"{self.type} {self.var} [{start}:{stop}:{step}] ? {'Ø' if self.cond is None else self.cond}"