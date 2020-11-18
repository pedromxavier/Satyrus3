## Standard Library
from functools import reduce
from collections import defaultdict

## Local
from ...satlib import join, compose
from .main import Expr, Number, Var

## :: Rule Definition ::
## :: Logical ::
from .symbols.tokens import T_AND, T_OR, T_XOR, T_NOT, T_IFF, T_IMP, T_RIMP

@Expr.rule(T_AND)
def AND(*args):
    return reduce(lambda x, y : x.__and__(y), args, Number.T) ## Empty product

@Expr.rule(T_OR)
def OR(*args):
    return reduce(lambda x, y : x.__or__(y), args, Number.F) ## Empty Sum

@Expr.rule(T_XOR)
def XOR(x, y):
    return x.__xor__(y)

@Expr.rule(T_NOT)
def NOT(x):
    return x.__not__()

@Expr.rule(T_IMP)
def IMP(x, y):
    return x.__imp__(y)

@Expr.rule(T_RIMP)
def RIMP(x, y):
    return x.__rimp__(y)

@Expr.rule(T_IFF)
def IFF(x, y):
    return x.__iff__(y)

## :: Indexing ::
from .symbols.tokens import T_IDX

@Expr.rule(T_IDX)
def IDX(x, i):
    return x.__idx__(i)

## :: Aritmetic ::
from .symbols.tokens import T_ADD, T_SUB, T_MUL, T_DIV, T_MOD

@Expr.rule(T_ADD)
def ADD(*args):
    if len(args) >= 2:
        number = []
        others = []
        for arg in args:
            if type(arg) is Number:
                number.append(arg)
            else:
                others.append(arg)
        else:
            if number:
                x = reduce(lambda x, y : x.__add__(y), number)
            else:
                x = None
            if others:
                y = Expr(T_ADD, *others)
            else:
                y = None

            if y is None:
                return x
            if x is None:
                return y
            else:
                return Expr.associate(x + y)
    else:
        args[0].__pos__()

@Expr.rule(T_SUB)
def SUB(x, y=None):
    if y is not None:
        return x.__sub__(y)
    else:
        return x.__neg__()

@Expr.rule(T_MUL)
def MUL(*args):
    number = []
    others = []
    for arg in args:
        if type(arg) is Number:
            number.append(arg)
        else:
            others.append(arg)
    else:
        if number:
            x = reduce(lambda x, y : x.__mul__(y), number)
        else:
            x = None
        if others:
            y = Expr(T_MUL, *others)
        else:
            y = None

        if x is None:
            return y
        if y is None:
            return x
        else:
            return Expr.associate(x * y)

@Expr.rule(T_DIV)
def DIV(x, y):
    return x.__truediv__(y)

@Expr.rule(T_MOD)
def MOD(x, y):
    return x.__mod__(y)

## :: Comparison ::
from .symbols.tokens import T_GE, T_GT, T_EQ, T_LT, T_LE, T_NE

@Expr.rule(T_GT)
def GT(x, y):
    return x.__gt__(y)

@Expr.rule(T_GE)
def GE(x, y):
    return x.__ge__(y)

@Expr.rule(T_LT)
def LT(x, y):
    return x.__lt__(y)

@Expr.rule(T_LE)
def LE(x, y):
    return x.__le__(y)

@Expr.rule(T_NE)
def NE(x, y):
    return (~ x.__ge__(y))

Expr.ASSOCIATIVE.update({
    ## Logical
    T_AND, T_OR,

    ## Arithmetic
    T_ADD, T_MUL,
})

Expr.NULL.update({
    ## Logical
    T_AND : Number.F,
    T_OR : Number.T,

    ## Arithmetic
    T_ADD : None,
    T_MUL : Number('0'),
})

Expr.NEUTRAL.update({
    ## Logical
    T_AND : Number.T,
    T_OR : Number.F,

    ## Arithmetic
    T_ADD : Number('0'),
    T_MUL : Number('1'),
})

Expr.GROUPS.update({ ## precedence groups
    ## Logical
    ## 1
    T_IMP : 1,
    T_RIMP : 1,
    T_IFF : 1,

    ## 2
    T_OR : 2,

    ## 3
    T_AND : 3,

    ## 4
    T_NOT : 4,

    T_ADD : 5,

    T_SUB : 5,

    T_MUL : 6,
})

Expr.FORMAT_PATTERNS.update({
    
    ## Logical
    T_XOR : "{1} {0} {2}",
    T_NOT : "{0}{1}",

    T_IMP : "{1} {0} {2}",
    T_RIMP: "{1} {0} {2}",
    T_IFF : "{1} {0} {2}",

    ## Arithmetical
    T_DIV : "{1} {0} {2}",
    T_MOD : "{1} {0} {2}",

    ## Indexing
    T_IDX: "{1}[{2}]",
    })

Expr.FORMAT_FUNCS.update({
    T_ADD : (lambda head, *tail: (join(f' {head} ', tail) if (len(tail) > 1) else f'{head}{tail[0]}')),
    T_SUB : (lambda head, *tail: (join(f' {head} ', tail) if (len(tail) > 1) else f'{head}{tail[0]}')),
    T_MUL : (lambda head, *tail: (join(f' {head} ', tail))),

    T_AND : (lambda head, *tail: (join(f' {head} ', tail))),
    T_OR  : (lambda head, *tail: (join(f' {head} ', tail))),
})

## Expression  Tables
Expr.TABLE['IMP'] = {
    T_IMP  : (lambda A, B : ~A | B),
    T_RIMP : (lambda A, B : A | ~B),
    T_IFF  : (lambda A, B : (~A & ~B) | (A & B)),
    }

Expr.TABLE['LMS'] = {
    T_AND : (lambda x, y : x * y),
    T_OR  : (lambda x, y : x + y - x * y),
    T_NOT : (lambda x : Number('1') - x),
    }

Expr.TABLE['NOT'] = {
    # AND, OR, XOR:
    T_AND  : (lambda *X : Expr(T_OR, *[Expr(T_NOT, x) for x in X])),
    T_OR   : (lambda *X : Expr(T_AND, *[Expr(T_NOT, x) for x in X])),
    T_XOR  : (lambda A, B : A.__iff__(B)),
    # Implications:
    T_IMP  : (lambda A, B : (~B).__imp__(~A)),
    T_RIMP : (lambda A, B : (~B).__rimp__(~A)),
    T_IFF  : (lambda A, B : A ^ B),
    # Double NOT:
    T_NOT  : (lambda A : A)
    }

Expr.TABLE['NEG'] = {
    # AND, OR, XOR:
    T_ADD  : (lambda *X : Expr(T_ADD, *[Expr(T_SUB, x) for x in X])),
    T_MUL  : (lambda *x, Y : Expr(T_MUL, Expr(T_SUB, x), *Y)),
    T_SUB  : (lambda A, B=None : A.__add__(B) if (B is not None) else A),
    # Implications:
    T_DIV  : (lambda A, B : Expr(T_SUB, A) / (B)),
    }

Expr.TABLE['XOR'] = {
    T_XOR : (lambda A, B : (~A & B) | (A & ~B)),
    }

@Expr.classmethod
def remove_implications(cls, expr):
    if type(expr) is cls and expr.head in cls.TABLE['IMP']:
        return cls.TABLE['IMP'][expr.head](*expr.tail)
    else:
        return expr

@Expr.classmethod
def move_not_inwards(cls, expr):
    if type(expr) is cls and expr.head == T_NOT:
        expr = expr.tail[0]
        if type(expr) is Expr:
            if expr.head in cls.TABLE['NOT']:
                return cls.TABLE['NOT'][expr.head](*expr.tail)
            else:
                return expr
        else:
            return cls(T_NOT, expr)
    else:
        return expr

@Expr.classmethod
def distribute_and_over_or(cls, expr):
    if type(expr) is cls and expr.head == T_OR:
        conjs = [(p.tail if (type(p) is cls and p.head == T_AND) else (p,)) for p in expr.tail]
        return cls(T_AND, *(cls(T_OR, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.classmethod
def distribute_or_over_and(cls, expr):
    if type(expr) is cls and expr.head == T_AND:
        conjs = [(p.tail if (type(p) is cls and p.head == T_OR) else (p,)) for p in expr.tail]
        return cls(T_OR, *(cls(T_AND, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.classmethod
def cnf(cls, expr):
    expr = cls.associate(cls.apply(expr, compose(cls.move_not_inwards, cls.remove_implications)))
    return cls.associate(cls.back_apply(expr, cls.distribute_and_over_or))

@Expr.classmethod
def dnf(cls, expr):
    expr = cls.associate(cls.apply(expr, compose(cls.move_not_inwards, cls.remove_implications)))
    return cls.associate(cls.back_apply(expr, cls.distribute_or_over_and))

@Expr.classmethod
def lms(cls, expr):
    """ Expr is assumed to be in the c.n.f.
    """
    table = {
        T_AND : (lambda tail: cls(T_MUL, *tail)),
        T_OR : (lambda tail: cls(T_ADD, *tail)),
        T_NOT : (lambda tail: cls(T_SUB, Number('1'), *tail))
    }
    return Expr.apply(expr, lambda expr: table[expr.head](expr.tail) if (type(expr) is cls and expr.head in table) else expr)

@Expr.classmethod
def move_neg_inwards(cls, expr):
    if type(expr) is cls and expr.head == T_SUB:
        expr = expr.tail[0]
        if type(expr) is cls:
            if expr.head in cls.TABLE['NEG']:
                return cls.TABLE['NEG'][expr.head](*expr.tail)
            else:
                return expr
        else:
            return cls(T_SUB, expr)
    else:
        return expr

@Expr.classmethod
def remove_subtractions(cls, expr):
    if type(expr) is cls and expr.head == T_SUB and len(expr.tail) == 2:
        return cls(T_ADD, expr.tail[0], cls(T_SUB, expr.tail[1]))
    else:
        return expr

@Expr.classmethod
def distribute_add_over_mul(cls, expr):
    """
    """
    if type(expr) is cls and expr.head == T_MUL:
        conjs = [(p.tail if (type(p) is cls and p.head == T_ADD) else (p,)) for p in expr.tail]
        return cls(T_ADD, *(cls(T_MUL, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.classmethod
def anf(cls, expr):
    expr = cls.associate(cls.apply(expr, compose(cls.move_neg_inwards, cls.remove_subtractions)))
    return cls.associate(cls.back_apply(expr, cls.distribute_add_over_mul))

@Expr.classmethod
def calc_prod(cls, expr) -> (frozenset, Number):
    c = Number('1.0')
    s = set()
    for e in expr.tail:
        if type(e) is cls:
            if e.head == T_SUB:
                c *= Number('-1')
                s.add(e.tail[0])
            else:
                raise ValueError('CALC_PRODx00')
        elif type(e) is Var:
            s.add(e)
        elif type(e) is Number:
            c *= e
        else:
            raise ValueError('CALC_PRODx10')
    else:
        return (frozenset(s), c)

@Expr.classmethod
def sum_table(cls, expr):
    if type(expr) is cls:
        if expr.head == T_ADD:
            table = defaultdict(lambda: Number('0'))
            for e in expr.tail:
                if type(e) is cls:
                    if e.head == T_MUL:
                        k, v = cls.calc_prod(e)
                    elif e.head == T_SUB:
                        k, v = (frozenset([e.tail[0]]), Number('-1'))
                    else:
                        raise ValueError('SUM_TABLE')
                else:
                    k, v = (None, Number('1'))
                table[k] += v
                continue
            else:
                return table

        elif expr.head == T_MUL:
            return dict([cls.calc_prod(expr)])
        elif expr.head == T_SUB:
            return {frozenset([expr.tail[0]]) : Number('-1')}
        else:
            raise ValueError('SUM_TABLEx00')
    elif type(expr) is Var:
        return {frozenset([expr]) : Number('-1')}
    elif type(expr) is Number:
        return {None: expr}
    else:
        raise ValueError('SUM_TABLEx10')