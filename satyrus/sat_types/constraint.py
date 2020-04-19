from .symbols.tokens import T_FORALL, T_EXISTS, T_EXISTS_ONE


class Loop:

    def __init__(self, type_, var, range_, cond, inner):
        self.var = var
        self.range = range_
        self.cond = cond
        self.inner = inner

class Constraint(object):
    
    def __init__(self, type_, name, loops, expr, level):
        self.type = type_
        self.name = name
        self.loops = loops
        self.expr = expr
        self.level = level

    def __str__(self):
        return f"({self.type}) [{self.level}] {self.loops} {self.expr}"
    