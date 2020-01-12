from sat_core import *;
from sat_errors import *;

import sat_treeview as STV;

class BaseSatType(object):

    def __solve__(a):
        return a

    def __gnd__(a):
        return a

    def __eq__(a, b):
        return Expr(T_EQ, a, b)

    def __le__(a, b):
        return Expr(T_LE, a, b)

    def __lt__(a, b):
        return Expr(T_LT, a, b)

    def __ge__(a, b):
        return Expr(T_GE, a, b)

    def __gt__(a, b):
        return Expr(T_GT, a, b)

    def __neg__(a):
        return Expr(T_SUB, a)

    def __pos__(a):
        return Expr(T_ADD, a)

    def __mul__(a, b):
        return Expr(T_MUL, a, b)

    def __rmul__(a, b):
        return Expr(T_MUL, b, a)

    def __add__(a, b):
        return Expr(T_ADD, a, b)

    def __radd__(a, b):
        return Expr(T_ADD, b, a)

    def __sub__(a, b):
        return Expr(T_SUB, a, b)

    def __rsub__(a, b):
        return Expr(T_SUB, b, a)

    def __truediv__(a, b):
        return Expr(T_DIV, a, b)

    def __rtruediv__(a, b):
        return Expr(T_DIV, b, a)

    # Logic
    def __and__(a, b):
        return Expr(T_AND, a, b)

    def __rand__(a, b):
        return Expr(T_AND, b, a)

    def __or__(a, b):
        return Expr(T_OR, a, b)

    def __ror__(a, b):
        return Expr(T_OR, b, a)

    def __xor__(a, b):
        return Expr(T_XOR, a, b)

    def __rxor__(a, b):
        return Expr(T_XOR, b, a)

    def __imp__(a, b):
        return Expr(T_IMP, a, b)

    def __rimp__(a, b):
        return Expr(T_RIMP, a, b)

    def __iff__(a, b):
        return Expr(T_IFF, a, b)

    def __not__(a):
        return Expr(T_NOT, a)

    def __idx__(a, b):
        return Expr(T_IDX, a, b)

    def __invert__(a):
        return a.__not__()

    @property
    def logic(a):
        return True

    @property
    def pseudo_logic(a):
        return True

    @property
    def token(a):
        return None

    @property
    def arity(a):
        return 0

    @property
    def head(a):
        return (a.token, a.arity)

    @property
    def expr(a):
        return False

    @property
    def height(a):
        return 1

    @property
    def width(a):
        return 1

    @property
    def vars(a):
        return set()

    @property
    def var(a):
        return False

class Number(BaseSatType, dcm.Decimal):

    regex = re.compile(r'(\.[0-9]*[1-9])(0+)|(\.0*)$')

    def __hash__(a):
        return hash(str(a))

    def __eq__(a, b):
        try:
            return Number(dcm.Decimal.__eq__(a, b))
        except:
            return BaseSatType.__eq__(a, b)

    def __le__(a, b):
        try:
            return Number(dcm.Decimal.__le__(a, b))
        except:
            return BaseSatType.__le__(a, b)

    def __lt__(a, b):
        try:
            return Number(dcm.Decimal.__lt__(a, b))
        except:
            return BaseSatType.__lt__(a, b)

    def __ge__(a, b):
        try:
            return Number(dcm.Decimal.__ge__(a, b))
        except:
            return BaseSatType.__ge__(a, b)

    def __gt__(a, b):
        try:
            return Number(dcm.Decimal.__gt__(a, b))
        except:
            return BaseSatType.__gt__(a, b)

    def __str__(self):
        return self.regex.sub(r'\1', dcm.Decimal.__str__(self))

    def __repr__(self):
        return f"Number('{self.__str__()}')"

    def __neg__(a):
        try:
            return Number(dcm.Decimal.__neg__(a))
        except:
            return BaseSatType.__neg__(a, b)

    def __pos__(a):
        try:
            return Number(dcm.Decimal.__pos__(a))
        except:
            return BaseSatType.__pos__(a, b)

    def __mul__(a, b):
        try:
            return Number(dcm.Decimal.__mul__(a, b))
        except:
            return BaseSatType.__mul__(a, b)

    def __rmul__(a, b):
        try:
            return Number(dcm.Decimal.__rmul__(a, b))
        except:
            return BaseSatType.__rmul__(a, b)

    def __add__(a, b):
        try:
            return Number(dcm.Decimal.__add__(a, b))
        except:
            return BaseSatType.__add__(a, b)

    def __radd__(a, b):
        try:
            return Number(dcm.Decimal.__radd__(a, b))
        except:
            return BaseSatType.__radd__(a, b)

    def __sub__(a, b):
        try:
            return Number(dcm.Decimal.__sub__(a, b))
        except:
            return BaseSatType.__sub__(a, b)

    def __rsub__(a, b):
        try:
            return Number(dcm.Decimal.__rsub__(a, b))
        except:
            return BaseSatType.__rsub__(a, b)

    def __truediv__(a, b):
        try:
            return Number(dcm.Decimal.__truediv__(a, b))
        except:
            return BaseSatType.__truediv__(a, b)

    def __rtruediv__(a, b):
        try:
            return Number(dcm.Decimal.__rtruediv__(a, b))
        except:
            return BaseSatType.__rtruediv__(a, b)

    def __and__(a, b):
        try:
            return a * b
        except:
            return BaseSatType.__and__(a, b)

    def __or__(a, b):
        try:
            return (a + b) - (a * b)
        except:
            return BaseSatType.__or__(a, b)

    def __xor__(a, b):
        try:
            return (a + b) - (2 * a * b)
        except:
            return BaseSatType.__xor__(a, b)

    def __imp__(a, b):
        try:
            return ~(a & ~b)
        except:
            return BaseSatType.__imp__(a, b)

    def __rimp__(a, b):
        try:
            return ~(~a & b)
        except:
            return BaseSatType.__rimp__(a, b)

    def __iff__(a, b):
        try:
            return (~a & ~b) | (a & b)
        except:
            return BaseSatType.__iff__(a, b)

    def __not__(a):
        try:
            return a.__invert__()
        except:
            return BaseSatType.__not__(a)

    def __invert__(a):
        try:
            return 1 - a
        except:
            return BaseSatType.__invert__(a)

    @property
    def int(a):
        return bool((a - Number(int(a))) == Number.FALSE)

    @property
    def bool(a):
        return a == Number.TRUE or a == Number.FALSE

Number.TRUE  = Number('1')
Number.FALSE = Number('0')

class BaseExpr(BaseSatType):

    def __init__(expr, token, *tail, **kwargs):
        BaseSatType.__init__(expr)

        expr.list = [intern(token), *tail]

        format = kwget('format', kwargs, None)

        if format is None:
            format = (" ".join(["{%d}" % i for i in range(len(expr.list))]))

        expr.format = format

    def __str__(expr):
        return expr.format.format(*expr.list)

    def __repr__(expr):
        classname = expr.__class__.__name__
        return f"{classname}('{expr.token}', {', '.join(map(repr, expr.tail))})"

    def __hash__(expr):
        return tuple.__hash__((expr.head, expr.tail))

    @property
    def arity(expr):
        return len(expr.tail)

    @property
    def token(expr):
        return expr.list[0]

    @property
    def tail(expr):
        return tuple(expr.list[1:])

    @property
    def expr(expr):
        return True

    @property
    def height(expr):
        return 1 + max(e.height for e in expr.tail)

    @property
    def width(expr):
        return expr.arity + max(e.width for e in expr.tail) - 1

    @threaded
    def tree_view(expr, **kwargs):
        STV.tree_view(expr, **kwargs)

class Expr(BaseExpr):

    # Arithmetic
    def r_ADD(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__add__(y)

    def r_SUB(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__sub__(y)

    def r_MUL(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__mul__(y)

    def r_DIV(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__truediv__(y)

    def r_POS(x):
        x = x.__solve__()
        return x.__pos__()

    def r_NEG(x):
        x = x.__solve__()
        return x.__neg__()

    def r_ADDX(x):
        return SUM(x)

    def r_MULX(x):
        return MUL(x)


    # Logic
    def r_AND(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__and__(y)

    def r_OR(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__or__(y)

    def r_XOR(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__xor__(y)

    def r_IMP(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__imp__(y)

    def r_RIMP(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__rimp__(y)

    def r_IFF(x, y):
        x, y = x.__solve__(), y.__solve__()
        return x.__iff__(y)

    def r_NOT(x):
        x = x.__solve__()
        return x.__not__()

    def r_IDX(x, i):
        return x.__idx__(i)

    RULES = {

        H_ADD : r_ADD, H_POS : r_POS,
        H_SUB : r_SUB, H_NEG : r_NEG,

        H_MUL : r_MUL,
        H_DIV : r_DIV,

        H_AND : r_AND,
        H_OR  : r_OR ,
        H_XOR : r_XOR,

        H_NOT : r_NOT,

        H_IMP : r_IMP,
        H_RIMP: r_RIMP,
        H_IFF : r_IFF,

        H_IDX : r_IDX,

    };

    FORMATS = {
        H_ADD : "{1} {0} {2}", H_POS : "{0}{1}",
        H_SUB : "{1} {0} {2}", H_NEG : "{0}{1}",

        H_MUL : "{1} {0} {2}",
        H_DIV : "{1} {0} {2}",

        H_AND : "{1} {0} {2}",
        H_OR  : "{1} {0} {2}",
        H_XOR : "{1} {0} {2}",

        H_NOT : "{0}{1}",

        H_IMP : "{1} {0} {2}",
        H_RIMP: "{1} {0} {2}",
        H_IFF : "{1} {0} {2}",

        H_IDX: "{1}[{2}]",
    };

    GROUPS = {
        H_ADD : 1, H_ADD : 1, H_SUB : 1,
        H_MUL : 2, H_DIV : 2,
        H_AND : 3,
        H_OR  : 4, H_XOR : 4,
        H_ADD : 5, H_SUB : 5,
        H_NOT : 6,
        H_IMP : 7, H_RIMP: 7, H_IFF : 7,
        H_IDX : 8,
    };

    LOGIC = {
        H_AND,
        H_OR ,
        H_XOR,
        H_NOT,
        H_IMP, H_RIMP, H_IFF,
        H_IDX,
    };

    PSEUDO_LOGIC = {
        H_MUL, H_ADD, H_SUB, H_POS, H_NEG,
    };

    IMP_TABLE = {
        H_IMP  : lambda A, B : ~A | B,
        H_RIMP : lambda A, B : A | ~B,
        H_IFF  : lambda A, B : (~A & ~B) | (A & B),
    };

    LMS_TABLE = {
        H_AND : lambda x, y : x * y,
        H_OR  : lambda x, y : x + y - x * y,
        H_NOT : lambda x : Number.TRUE - x, # 1 - x
    };

    NOT_TABLE = {
        # AND, OR, XOR:
        H_AND  : lambda A, B : ~A | ~B,
        H_OR   : lambda A, B : ~A & ~B,
        H_XOR  : lambda A, B : A.__iff__(B),
        # Implications:
        H_IMP  : lambda A, B : (~B).__imp__(~A),
        H_RIMP : lambda A, B : (~B).__rimp__(~A),
        H_IFF  : lambda A, B : A ^ B,
        # Double NOT:
        H_NOT  : lambda A : A,

        # Indexing:
        H_IDX  : lambda A, B : ~(A.__idx__(B))
    };

    XOR_TABLE = {
        H_XOR : lambda A, B : (~A & B) | (A & ~B),
    }

    NEED_PAR = {
                    H_ADD, H_SUB , H_MUL, H_DIV,
                    H_AND, H_OR  , H_XOR,
                    H_IMP, H_RIMP, H_IFF,
                }

    SIDE = {
        # For Hashing Effects when comparing expressions
        # None stands for commutativity
        # True means that the side is right.
        # Any other symbol explains how to invert expression

        # AND, OR, XOR:
        H_AND  : None,
        H_OR   : None,
        H_XOR  : None,
        # Implications:
        H_IMP  : True,
        H_RIMP : T_IMP,
        H_IFF  : None,
        # NOT:
        H_NOT  : None,

        # Indexing:
        H_IDX  : True,
    }

    def __init__(expr, token, *tail):
        BaseExpr.__init__(expr, token, *tail)

    def __str__(expr):
        tail = [expr.par(e) for e in expr.tail]
        return Expr.FORMATS[expr.head].format(expr.token, *tail)

    def __solve__(expr):
        expr = expr.rmv_xor()
        expr = expr.rmv_imp()
        expr = expr.rmv_not()
        expr = expr.rmv_and()
        expr = expr.rmv_or()
        return expr

    def __gnd__(expr):
        return expr.RULES[expr.head](*[e.__gnd__() for e in expr.tail])

    def __getitem__(expr, index):
        if type(index) is not dict:
            raise TypeError(ERROR_MSGS['Expr.__getitem__'][0])
        else:
            return Expr.back_apply(expr, Expr.s_index, index)

    def __hash__(expr):
        side = Expr.SIDE[expr.head]

        if side is None:
            head_hash = hash(expr.head)
            tail_hash = hash(sum(hash(e) for e in expr.tail))

        elif side is True:
            head_hash = hash(expr.head)
            tail_hash = hash(expr.tail)

        else:
            head_hash = hash(side)
            tail_hash = hash(expr.tail)

        return hash((head_hash, tail_hash))

    # Solving Techniques
    @staticmethod
    def s_index(expr, index):
        '''
        '''
        if expr.head == H_IDX:
            x, i = expr.tail
            if i in index:
                return Expr('[]', x, index[i])
            else:
                return expr
        else:
            return expr

    @staticmethod
    def s_rmv_and(expr):
        '''
        '''
        if expr.head == H_AND:
            A, B = expr.tail

            if Expr.equal(A, B):
                return A

            elif Expr.equal(A, (~B).rmv_not()):
                return Number.FALSE

            elif Expr.equal(A, Number.TRUE):
                return B

            elif Expr.equal(B, Number.TRUE):
                return A

            elif Expr.equal(A, Number.FALSE):
                return Number.FALSE

            elif Expr.equal(B, Number.FALSE):
                return Number.FALSE

        return expr

    @staticmethod
    def s_rmv_or(expr):
        '''
        '''
        if expr.head == H_OR:
            A, B = expr.tail

            if Expr.equal(A, B):
                return A

            elif Expr.equal(A, (~B).rmv_not()):
                return Number.TRUE

            elif Expr.equal(A, Number.TRUE):
                return Number.TRUE

            elif Expr.equal(B, Number.TRUE):
                return Number.TRUE

            elif Expr.equal(A, Number.FALSE):
                return B

            elif Expr.equal(B, Number.FALSE):
                return A

        return expr


    @staticmethod
    def s_to_cnf(expr):
        ''' Translates to conjunctive normal form (c.n.f.)
            (a11 | ... | a1n) & ... & (am1 | ... | amn)
        '''
        raise NotImplementedError("Missing steps in this method.")

    @staticmethod
    def s_to_dnf(expr):
        ''' Translates to disjunctive normal form (d.n.f.)
            (a11 & ... & a1n) | ... | (am1 & ... & amn)
        '''
        raise NotImplementedError("Missing steps in this method.")

    @staticmethod
    def s_to_inf(expr):
        ''' Translates to implicative normal form (i.n.f.)
            a1 & ... & am -> b1 | ... | bn
        '''
        raise NotImplementedError("Missing steps in this method.")

    @staticmethod
    def s_rmv_xor(expr):
        ''' Removes XOR.
            A ^ B : [~A & B] | [A & ~B]
        '''
        if expr.head == H_XOR:
            return Expr.XOR_TABLE[expr.head](*expr.tail)
        else:
            return expr

    @staticmethod
    def s_rmv_not(expr):
        ''' Solves negations, applying DeMorgan rule and removing double
            negations (warning: requires t-norm idempotency)
                ~[~A]    :  A
                ~[A | B] : ~A & ~B
                ~[A & B] : ~A | ~B
                ~[A-> B] : ~B-> ~A
                ~[A <-B] : ~B <-~A
                ~[A ^ B] :  A<->B
                ~[A<->B] :  A ^ B
        '''
        if expr.head == H_NOT:
            expr, = expr.tail
            if expr.expr:
                return Expr.NOT_TABLE[expr.head](*expr.tail)
            else:
                return ~expr
        else:
            return expr

    @staticmethod
    def s_rmv_imp(expr):
        ''' Removes Implications (->, <- and <->).
            Translation occours as:
                A -> B  : ~A | B
                A <- B  : A | ~B
                A <-> B : (~A & ~B) | (A & B)
        '''
        if expr.head in Expr.IMP_TABLE:
            return Expr.IMP_TABLE[expr.head](*expr.tail)
        else:
            return expr

    def rmv_imp(expr):
        return Expr.apply(expr, Expr.s_rmv_imp)

    def rmv_not(expr):
        return Expr.apply(expr, Expr.s_rmv_not)

    def rmv_xor(expr):
        return Expr.apply(expr, Expr.s_rmv_xor)

    def rmv_and(expr):
        return Expr.apply(expr, Expr.s_rmv_and)

    def rmv_or(expr):
        return Expr.apply(expr, Expr.s_rmv_or)

    @staticmethod
    def s_lms(expr):
        ''' Maps formula into arithmetic form.
        '''
        if expr.head in Expr.LMS_TABLE:
            return Expr.LMS_TABLE[expr.head](*expr.tail)
        else:
            return expr

    @property
    def lms(expr):
        if not expr.pseudo_logic:
            msg = "This expression is not pseudo-boolean thus logic correspondence is not guaranteed."
            warnings.warn(msg)

        expr = expr.rmv_xor()
        expr = expr.rmv_imp()
        expr = expr.rmv_not()

        return Expr.apply(expr, Expr.s_lms)

    @staticmethod
    def equal(A, B):
        ''' Method for comparing two expressions.
        '''
        return hash(A) == hash(B);

    @staticmethod
    def __decode__(T):
        if type(T) is tuple:
            head, *tail = T
            
            return Expr(head, *(Expr.from_tuple(t) for t in tail))
        else:
            return T
    
    @staticmethod
    def _encode_(p):
        if type(p) is Expr:
            return p.head, tuple(Expr.to_tuple(q) for q in p.tail)
        else:
            return p

    def __encode__(expr):
        return Expr._encode_(expr)

    @staticmethod
    def apply(expr, func, *args, **kwargs):
        if expr.expr:
            expr = func(expr, *args, **kwargs)
        else:
            return expr

        if expr.expr:
            tail = [Expr.apply(e, func, *args, **kwargs) for e in expr.tail]
            expr = Expr(expr.token, *tail)
            return expr
        else:
            return expr

    @staticmethod
    def back_apply(expr, func, *args, **kwargs):
        if expr.expr:
            tail = [Expr.back_apply(e, func, *args, **kwargs) for e in expr.tail]
            expr = Expr(expr.token, *tail)
            return func(expr, *args, **kwargs)
        else:
            return expr

    @property
    def cnf(expr):
        if expr.logic:
            return Expr.s_to_cnf(expr)
        else:
            error_msg = 'Non-logic expression has no C.N.F'
            raise SatError(error_msg)

    @property
    def dnf(expr):
        if expr.logic:
            return Expr.s_to_dnf(expr)
        else:
            error_msg = 'Non-logic expression has no D.N.F'
            raise SatError(error_msg)

    @property
    def inf(expr):
        if expr.logic:
            return Expr.s_to_inf(expr)
        else:
            error_msg = 'Non-logic expression has no I.N.F'
            raise SatError(error_msg)

    def par(expr, e):
        if (e.expr) and (e.head in Expr.NEED_PAR) and (expr.group != e.group):
            return f"({e})"
        return f"{e}"

    @property
    def gnd(expr):
        expr = solve(expr)
        return expr.__gnd__()

    @property
    def group(expr):
        return Expr.GROUPS[expr.head]

    @property
    def logic(expr):
        if expr.head not in Expr.LOGIC:
            return False
        else:
            return all(e.logic for e in expr.tail)

    @property
    def pseudo_logic(expr):
        if (not expr.logic) and (expr.head not in Expr.PSEUDO_LOGIC):
            return False
        else:
            return all(e.pseudo_logic for e in expr.tail)

    @property
    def vars(expr):
        return set.union(*(e.vars for e in expr.tail))

class Var(BaseSatType, str):

    __ref__ = {} # works as 'intern'

    def __new__(cls, name):
        if name not in cls.__ref__:
            obj = str.__new__(cls, name)
            Var.__init__(obj, name)
            cls.__ref__[name] = obj
        return cls.__ref__[name]

    def __init__(self, name):
        BaseSatType.__init__(self)

    def __hash__(self):
        return str.__hash__(self)

    def __repr__(self):
        return f"Var('{self}')"

    def __idx__(x, i):
        return Var(f"{x}_{i}")

    @property
    def tail(self):
        return None

    @property
    def vars(self):
        return {self}

    @property
    def expr(self):
        return False

    @property
    def var(self):
        return True
