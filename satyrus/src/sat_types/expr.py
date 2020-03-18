class Expr(object):
    """
    """
    def __init__(self, head, *tail):
        self.head = head
        self.tail = tail



    

## --------------------------------------- ##

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