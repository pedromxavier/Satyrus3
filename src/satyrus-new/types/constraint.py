from .expr import Expr
from .number import Number
from .string import String
from .var import Var

class Constraint(object):

    def __init__(self, name: Var, cons_type: String, level: Number=None):
        self._name = name
        self._type = cons_type
        self._level = (level if level is not None else Number('0'))

        self._expr = None
        self._clauses = None
        
    def set_expr(self, expr: Expr):
        self._expr = expr

        if isinstance(self._expr, Expr):
            if (self._expr.head == T_OR):
                clauses = [([*p.tail] if (isinstance(p, Expr) and p.head == T_AND) else [p]) for p in self._expr.tail]
            elif (self._expr.head == T_AND):
                clauses = [[*self._expr.tail]]
            else:
                clauses = [[self._expr]]
        else:
            clauses = [[self._expr]]

        self._clauses = clauses

    @property
    def var(self) -> Var:
        return self._name

    @property
    def name(self) -> str:
        return str(self._name)

    @property
    def type(self) -> str:
        return str(self._type)

    @property
    def level(self):
        return int(self._level)

    @property
    def clauses(self):
        return self._clauses
    
    @property
    def expr(self) -> Expr:
        return self._expr