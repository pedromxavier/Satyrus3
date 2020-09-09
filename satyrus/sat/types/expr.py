## Standard Library
from functools import reduce

## Local
from ...satlib import join, compose
from .main import Expr
from .number import Number

## :: Rule Definition ::
## :: Logical ::
from .symbols.tokens import T_AND, T_OR, T_XOR, T_NOT, T_IFF, T_IMP, T_RIMP

@Expr.rule(T_AND)
def AND(*args):
    return reduce(lambda x, y : x.__and__(y), args)

@Expr.rule(T_OR)
def OR(*args):
    return reduce(lambda x, y : x.__or__(y), args)

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
        return reduce(lambda x, y : x.__add__(y), args)
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
    return reduce(lambda x, y : x.__mul__(y), args)

@Expr.rule(T_DIV)
def DIV(x, y):
    return x.__truediv__(y)

@Expr.rule(T_MOD)
def MOD(x, y):
    return x.__mod__(y)

Expr.ASSOCIATIVE.update({
    ## Logical
    T_AND, T_OR,

    ## Arithmetic
    T_ADD, T_MUL,
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
    T_AND  : (lambda A, B : ~A | ~B),
    T_OR   : (lambda A, B : ~A & ~B),
    T_XOR  : (lambda A, B : A.__iff__(B)),
    # Implications:
    T_IMP  : (lambda A, B : (~B).__imp__(~A)),
    T_RIMP : (lambda A, B : (~B).__rimp__(~A)),
    T_IFF  : (lambda A, B : A ^ B),
    # Double NOT:
    T_NOT  : (lambda A : A),
    # Indexing:
    T_IDX  : (lambda A, B : ~(A.__idx__(B))),
    }

Expr.TABLE['XOR'] = {
    T_XOR : (lambda A, B : (~A & B) | (A & ~B)),
    }

def AND_HASH(head, *tail):
    if len(tail) >= 2:
        return reduce(lambda x, y: hash((head, hash(x) + hash(y))), tail)
    else:
        return hash((head, hash(tail[0])))

def SUB_HASH(head, x, y=None):
    if y is not None:
        return hash((T_ADD, hash(x) + hash((T_SUB, y))))
    else:
        return hash((head, hash(x)))

Expr.HASH.update({
    ## Logical
    T_AND  : (lambda head, *tail: reduce(lambda x, y: hash((head, hash(x) + hash(y))), tail)),
    T_OR   : (lambda head, *tail: reduce(lambda x, y: hash((head, hash(x) + hash(y))), tail)),
    T_XOR  : (lambda head, x, y: hash((head, hash(x) + hash(y)))),
    
    T_IMP  : (lambda head, x, y: hash((T_IMP, hash(x), hash(y)))),
    T_RIMP : (lambda head, x, y: hash((T_IMP, hash(y), hash(x)))),
    T_IFF  : (lambda head, x, y: hash((head, hash(x) + hash(y)))),

    ## Arithmetic
    T_ADD : AND_HASH,
    T_SUB : SUB_HASH,

    T_MUL : (lambda head, *tail: reduce(lambda x, y: hash((head, hash(x) + hash(y))), tail)),
    })

def remove_implications(expr):
    if expr.head in expr.TABLE['IMP']:
        return expr.TABLE['IMP'][expr.head](*expr.tail)
    else:
        return expr

def move_not_inwards(expr):
    if expr.head == T_NOT:
        expr = expr.tail[0]
        if type(expr) is Expr:
            if expr.head in expr.TABLE['NOT']:
                return expr.TABLE['NOT'][expr.head](*expr.tail)
            else:
                return expr
        else:
            return Expr(T_NOT, expr)
    else:
        return expr

def distribute_and_over_or(expr):
    """
        (A & B) | C => (A | C) & (B | C)
        (A & B) | (C & D) => (A | C) & (A | D) & (B | C) & (B | D)
    """
    if expr.head == T_OR:
        conjs = [(p.tail if (type(p) is Expr and p.head == T_AND) else (p,)) for p in expr.tail]
        return Expr(T_AND, *(Expr(T_OR, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.property
def cnf(expr):
    expr = Expr.apply(expr, compose(move_not_inwards, remove_implications))
    expr = expr.associate
    expr = expr.back_apply(expr, distribute_and_over_or)
    return expr

@Expr.property
def lms(expr):
    if expr.head == T_AND:
        array = []
        for p in expr.tail:
            if type(p) is Expr:
                if p.head == T_OR:
                    array.append(list(p.tail))
                else:
                    print(expr)
                    raise ValueError
            else:
                array.append([p])
    else:
        print(expr)
        raise ValueError