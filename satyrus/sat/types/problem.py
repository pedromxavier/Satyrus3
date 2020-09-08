from ...satlib import arange

from .expr import Expr
from .main import Var
from .number import Number

class Constraint(object):
    """ :: CONSTRAINT ::
        ================
    """

    TYPES = {'int', 'opt'}

    def __init__(self, cons_type: str, level: int):
        self.cons_type = str(cons_type)
        self.level = level

        self.loops = []
        self.expr = None

    def add_loop(self, var: Var, loop_type, start: int, stop: int, step: int, conds: list):
        self.loops.append([var, loop_type, [start, stop, step], [*conds] if conds is not None else None])

    def set_expr(self, expr: Expr):
        self.expr = expr.cnf

    def lms(self, compiler, p: Number):
        i = len(self.loops) - 1
        terms = []
        stack = []
        types = {}
        while i >= 0:
            compiler.push()
            var, loop_type, (start, stop, step), conds = self.loops[i]
            stack.append((var, loop_type, arange(start, stop, step)))
            i -= 1
        else:
            while stack:
                var, loop_type, idx = stack.pop()

                if str(loop_type) == '@':
                    token = '&'
                elif str(loop_type) == '&':
                    token = '|'
                else:
                    raise ValueError


                
