from .expr import Expr

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
        self.int = [c for c in constraints if (c.constype == 'int')]
        self.opt = [c for c in constraints if (c.constype == 'opt')]
        
        self.env = {

        }


class Constraint(object):
    """ :: CONSTRAINT ::
        ================
    """

    def __init__(self, constype: str, level: int, loops: list, expr: Expr):
        self.constype = constype
        self.level = level
        self.loops = loops
        self.expr = expr