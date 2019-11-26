# From Expr @ sat_base.py

def rmv_or(expr):
    expr = Expr.apply(expr, Expr.s_rmv_not)
    return Expr.back_apply(expr, Expr.s_rmv_or)

def rmv_and(expr):
    expr = Expr.apply(expr, Expr.s_rmv_not)
    return Expr.back_apply(expr, Expr.s_rmv_and)

def dist_and_or(expr):
    return Expr.back_apply(expr, Expr.s_dist_and_or)

def dist_or_and(expr):
    return Expr.back_apply(expr, Expr.s_dist_or_and)

@staticmethod
def s_dist_and_or(expr):
    ''' Distributes ANDs over ORs.
        A & [B | C] : [A & B] | [A & C]
        [A | B] & C : [A & C] | [B & C]
        also:
        [A | B] & [C | D] : [A & C] | [A & D] | [B & C] | [B & D]
    '''
    if expr.token is T_AND:
        A, C = expr.tail

        a = A.expr and (A.token is T_OR)
        c = C.expr and (C.token is T_OR)

        if a and c:
            A, B = A.tail
            C, D = C.tail
            return ((A & C) | (A & D)) | ((B & C) | (B & D))

        if a:
            A, B = A.tail
            return (A & C) | (B & C)

        if c:
            B, C = C.tail
            return (A & B) | (A & C)

    return expr

@staticmethod
def s_dist_or_and(expr):
    ''' Distributes ORs over ANDs.
        A | [B & C] : [A | B] & [A | C]
        [A & B] | C : [A | C] & [B | C]
        also:
        [A & B] | [C & D] : [A | C] & [A | D] & [B | C] & [B | D]
    '''
    if expr.token is T_OR:
        A, C = expr.tail

        a = A.expr and (A.token is T_AND)
        c = C.expr and (C.token is T_AND)

        if a and c:
            A, B = A.tail
            C, D = C.tail
            return ((A | C) & (A | D)) & ((B | C) & (B | D))

        if a:
            A, B = A.tail
            return (A | B) & (A | C)

        if c:
            B, C = C.tail
            return (A | C) & (B | C)

    return expr

@staticmethod
def s_rmv_and(expr):
    ''' Solves AND clauses where:
        ~A & A : 0
         0 & A : 0
         1 & A : A
         A & A : A
    '''
    if expr.token is T_AND:
        A, B = expr.tail

        if A == Number.TRUE:
            return B

        if B == Number.TRUE:
            return A

        if Expr.equal(A, B):
            return A

        if A == Number.FALSE:
            return Number.FALSE

        if B == Number.FALSE:
            return Number.FALSE

        if Expr.equal(~A, B):
            return Number.FALSE

    return expr

@staticmethod
def s_rmv_or(expr):
    ''' Solves OR clauses where:
        ~A | A : 1
         0 | A : A
         1 | A : 1
         A | A : A
    '''
    if expr.token is T_OR:
        A, B = expr.tail

        if A == Number.TRUE:
            return Number.TRUE

        if B == Number.TRUE:
            return Number.TRUE

        if Expr.equal(A, B):
            return A

        if A == Number.FALSE:
            return B

        if B == Number.FALSE:
            return A

        if Expr.equal(~A, B):
            return Number.TRUE

    return expr

class Domain(object):

    def __init__(self, start, stop, step=None):
        self.start = start
        self.stop = stop
        self.step = step if step is not None else Number.TRUE

    def __iter__(self):
        j = self.start
        while j <= self.stop:
            yield j
            j = j + self.step

    def __str__(self):
        if self.step == Number.TRUE:
            return f"[{self.start}:{self.stop}]"
        else:
            return f"[{self.start}:{self.stop}:{self.step}]"

class condition(BaseExpr):

    def __call__(self):
        ...

class Condition(list):
    ...

class loop:

    OPS = { # operators
        T_FORALL     : AND,
        T_EXISTS     : OR ,
        T_EXISTS_ONE : XOR,
    }

    def __init__(self, type, var, dom, con):
        self.type = type
        self.op = self.OPS[self.type]

        self.var = var
        self.dom = dom
        self.con = con

    def __str__(self):
        return f"{self.type}{'{'}{self.var} = {self.dom}{','.join(self.con)}{'}'}"

class Loop(list):

    def __init__(loop, buffer):
        list.__init__(loop, buffer)

    def __str__(loop):
        return " ".join(map(str, loop))

    @property
    def vars(loop):
        return tuple(l.var for l in loop)

class Constraint:

    def __init__(self, type : type, name : str, loop : Loop, expr : Expr):
        self.type = type
        self.name = name
        self.loop = loop
        self.expr = expr

    def __str__(self):
        return f"""
[Constraint]------------
Type : {self.type};

Name : {self.name};

Loop : {" ".join(map(str, self.loop))};

Expr : {self.expr};
------------[Constraint]
"""

    def compile(self):
        E = self.expr.index(self.loop.vars)
        I = self.loop

        return Constraint.build(E, I)

    @staticmethod
    def build(E, I):
        return Constraint.calc(E, I, (), len(I))

    @staticmethod
    def calc(E, I, i, n):
        J, *I = I
        if n == 1:
            return J.op([E[j] for j in J(i)])
        else:
            return J.op([calc(E, I, (*i, j), n-1) for j in J(i)])
