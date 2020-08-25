from .expr import Expr
from .main import Var

class Problem(object):
    """ :: PROBLEM ::
        =============

        This is the last instance (the output) of the compiler pipeline.

        This is also the input for the Solver API.

        Requisites:
        - JSON-serializable
        
        {
            "int" : [

            ],

            "opt" : [

            ],

            "env" : {
                "prec"    : 16,
                "epsilon" : 0.001,
                .
                .
                .
            }
        }
    """

    def __init__(self, constraints: list, *args, **kwargs):
        self.int = [c for c in constraints if (c.cons_type == 'int')]
        self.opt = [c for c in constraints if (c.cons_type == 'opt')]
        
        self.env = {

        }

    def __json__(self):
        return {
            'int' : self.int,
            'opt' : self.opt,
            'env' : self.env
        }


class Constraint(object):
    """ :: CONSTRAINT ::
        ================
    """

    TYPES = {'int', 'opt'}

    def __init__(self, cons_type: str, level: int):
        self.cons_type = cons_type
        self.level = level

        self.loops = []
        self.expr = None

    def add_loop(self, var: Var, start: int, stop: int, step: int, conds: list):
        self.loops.append([var, [start, stop, step], [*conds]])

    def set_expr(self, expr: Expr):
        self.expr = expr