from collections import deque

## Local
from ...satlib import arange
from .expr import Expr
from .main import Var, Number

from .symbols import CONS_INT, CONS_OPT
from .symbols.tokens import T_FORALL, T_EXISTS, T_EXISTS_ONE, T_AND, T_OR

class Loop(object):
    """ :: LOOP ::
        ==========
    """

    def __init__(self, var: Var, loop_type: str, start: Number, stop: Number, step: Number, conds: list=None):
        self.var = var
        self.type = str(loop_type)

        self.start = start
        self.stop = stop
        self.step = step

        self.conds = conds

    def cond_func(self, compiler):
        """
        """
        if self.conds is None:
            return True

        conds = [compiler.eval_expr(cond, calc=True) for cond in self.conds]
        return all([type(conds) is Number and (conds != Number('0')) for cond in conds])

    def indices(self, compiler):
        I = []
        start = compiler.eval_expr(self.start, calc=True)
        stop = compiler.eval_expr(self.stop, calc=True)
        step = compiler.eval_expr(self.step, calc=True)

        for i in arange(start, stop, step):
            i = Number(i)
            compiler.memset(self.var, i)
            if self.cond_func(compiler):
                I.append(i)
            else:
                continue
        return I

class Constraint(object):
    """ :: CONSTRAINT ::
        ================
    """

    HEAD_TABLE = {
        T_FORALL: T_AND,
        T_EXISTS: T_OR,
        T_EXISTS_ONE: None,
    }

    def __init__(self, name: Var, cons_type: Var, level: int):
        """
        """
        self.name = str(name)
        self.type = str(cons_type)
        self.level = int(level)

        self.loop_stack = deque([])
        self.expr = None

    def __repr__(self):
        return f"({self.type}) {self.name} [{self.level}]"

    def add_loop(self, var: Var, loop_type: Var, start: Number, stop: Number, step: Number, conds: list):
        """ ADD_LOOP
            ========
        """
        self.loop_stack.append(Loop(var, loop_type, start, stop, step, conds))

    def set_expr(self, expr: Expr):
        """ SET_EXPR
            ========

            Sets the expr of this constraint in the C.N.F.
        """
        self.expr = Expr.cnf(expr)

    def get_expr(self, compiler):
        """ GET_EXPR
            ========
        """
        return self._get_expr(compiler)

    def _get_expr(self, compiler):
        """
        """
        if not self.loop_stack:
            return self.expr
        
        ## Retrieves the outermost loop from the stack
        loop = self.loop_stack.popleft()

        ## Expression
        head = self.HEAD_TABLE[loop.type]
        tail = []

        ## Push compiler memory scope
        compiler.push()

        for i in loop.indices(compiler):
            compiler.memset(loop.var, i)
            expr = compiler.eval_expr(self._get_expr(compiler))
            tail.append(expr)
        else:
            self.loop_stack.appendleft(loop)
            compiler.pop()
            return Expr(head, *tail)
        
