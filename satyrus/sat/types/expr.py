## Standard Library
from functools import reduce
from collections import defaultdict

## Local
from ...satlib import join, compose, stderr
from .error import SatValueError
from .main import Expr, Number, Var, Array

@Expr.classmethod
def _simplify(cls: type, args: tuple, token: str, op: callable, e: Number):
    number = []
    others = []
    for arg in args:
        if type(arg) is Number:
            number.append(arg)
        else:
            others.append(arg)
    else:
        if number:
            x = reduce(op, number, e)
        else:
            x = None

        if others:
            y = Expr(token, *others)
        else:
            y = None

        if x is None and y is None:
            return e
        elif x is None:
            return y
        elif y is None:
            return x
        else:
            return Expr.associate(op(x, y))

## :: Rule Definition ::
## :: Logical ::
from .symbols.tokens import T_AND, T_OR, T_XOR, T_NOT, T_IFF, T_IMP, T_RIMP

Expr.LOGICAL = {
    T_AND, T_OR, T_XOR, T_NOT, T_IFF, T_IMP, T_RIMP
}

@Expr.rule(T_AND)
def AND(*args):
    #pylint: disable=no-member
    return Expr._simplify(args, T_AND, lambda x, y: x.__and__(y), Number.T)

@Expr.rule(T_OR)
def OR(*args):
    #pylint: disable=no-member
    return Expr._simplify(args, T_OR, lambda x, y: x.__or__(y), Number.F)

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

Expr.EXTRA = {
    T_IDX
}

@Expr.rule(T_IDX)
def IDX(x: Array, *i: tuple):
    return x.__idx__(i)
    
## :: Aritmetic ::
from .symbols.tokens import T_ADD, T_SUB, T_MUL, T_DIV, T_MOD

Expr.ARITHMETIC = {
    T_ADD, T_SUB, T_MUL, T_DIV, T_MOD
}

@Expr.rule(T_ADD)
def ADD(*args):
    #pylint: disable=no-member
    return Expr._simplify(args, T_ADD, lambda x, y: x.__add__(y), Number('0'))

@Expr.rule(T_SUB)
def SUB(x, y=None):
    if y is not None:
        return x.__sub__(y)
    else:
        return x.__neg__()

@Expr.rule(T_MUL)
def MUL(*args):
    #pylint: disable=no-member
    return Expr._simplify(args, T_MUL, lambda x, y: x.__mul__(y), Number('1'))

@Expr.rule(T_DIV)
def DIV(x, y):
    if y == Number('0'):
        raise SatValueError("Division by zero.", target=y)
    else:
        return x.__truediv__(y)

@Expr.rule(T_MOD)
def MOD(x, y):
    return x.__mod__(y)

## :: Comparison ::
from .symbols.tokens import T_GE, T_GT, T_EQ, T_LT, T_LE, T_NE

Expr.COMPARISON = {
    T_GE, T_GT, T_EQ, T_LT, T_LE, T_NE
}

@Expr.rule(T_GT)
def GT(x, y):
    return x.__gt__(y)

@Expr.rule(T_GE)
def GE(x, y):
    return x.__ge__(y)

@Expr.rule(T_EQ)
def EQ(x, y):
    return x.__eq__(y)

@Expr.rule(T_LT)
def LT(x, y):
    return x.__lt__(y)

@Expr.rule(T_LE)
def LE(x, y):
    return x.__le__(y)

@Expr.rule(T_NE)
def NE(x, y):
    return (x.__eq__(y)).__invert__()

Expr.ASSOCIATIVE.update({
    ## Logical
    T_AND, T_OR,

    ## Arithmetic
    T_ADD, T_MUL,

    ## Indexing
    T_IDX
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

    ## Comparison
    T_EQ : "{1} {0} {2}",
    T_LE : "{1} {0} {2}",
    T_GE : "{1} {0} {2}",
    T_LT : "{1} {0} {2}",
    T_GT : "{1} {0} {2}",
    T_NE : "{1} {0} {2}",

    })

Expr.FORMAT_FUNCS.update({
    ## Arithmetic
    T_ADD : (lambda head, *tail: (join(f' {head} ', tail) if (len(tail) > 1) else f'{head}{tail[0]}')),
    T_SUB : (lambda head, *tail: (join(f' {head} ', tail) if (len(tail) > 1) else f'{head}{tail[0]}')),
    T_MUL : (lambda head, *tail: (join(f' {head} ', tail))),

    ## Logical
    T_AND : (lambda head, *tail: (join(f' {head} ', tail))),
    T_OR  : (lambda head, *tail: (join(f' {head} ', tail))),

    ## Indexing
    T_IDX : (lambda head, *tail: f"{tail[0]}{join('', [f'[{x}]' for x in tail[1:]])}")
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
    T_IMP  : (lambda A, B : A & ~B),
    T_RIMP : (lambda A, B : ~A & B),
    T_IFF  : (lambda A, B : A ^ B),
    # Double NOT:
    T_NOT  : (lambda A : A)
    }

Expr.TABLE['NEG'] = {
    # AND, OR, XOR:
    T_ADD  : (lambda *X : Expr(T_ADD, *[Expr(T_SUB, x) for x in X])),
    T_MUL  : (lambda *x, Y : Expr(T_MUL, Expr(T_SUB, x), *Y)),
    T_SUB  : (lambda A, B=None : B.__sub__(A) if (B is not None) else A),
    # Implications:
    T_DIV  : (lambda A, B : Expr(T_SUB, A) / (B)),
    }

Expr.TABLE['XOR'] = {
    T_XOR : (lambda A, B : (~A & B) | (A & ~B)),
    }

@Expr.classmethod
def _remove_implications(cls, expr):
    if type(expr) is cls and expr.head in cls.TABLE['IMP']:
        return cls.TABLE['IMP'][expr.head](*expr.tail)
    elif type(expr) is cls and expr.head in cls.TABLE['XOR']:
        return cls.TABLE['XOR'][expr.head](*expr.tail)
    else:
        return expr

@Expr.classmethod
def _move_not_inwards(cls, expr):
    if type(expr) is cls and expr.head == T_NOT:
        expr = expr.tail[0]
        if type(expr) is Expr:
            if expr.head in cls.TABLE['NOT']:
                return cls.TABLE['NOT'][expr.head](*expr.tail)
            else:
                return cls(T_NOT, expr)
        else:
            return cls(T_NOT, expr)
    else:
        return expr

@Expr.classmethod
def _distribute_and_over_or(cls, expr):
    if type(expr) is cls and expr.head == T_OR:
        conjs = [(p.tail if (type(p) is cls and p.head == T_AND) else (p,)) for p in expr.tail]
        return cls(T_AND, *(cls(T_OR, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.classmethod
def _distribute_or_over_and(cls, expr):
    if type(expr) is cls and expr.head == T_AND:
        conjs = [(p.tail if (type(p) is cls and p.head == T_OR) else (p,)) for p in expr.tail]
        return cls(T_OR, *(cls(T_AND, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.classmethod
def cnf(cls: type, expr: Expr):
    expr = cls.associate(cls.apply(expr, compose(cls._move_not_inwards, cls._remove_implications)))
    return cls.associate(cls.back_apply(expr, cls._distribute_and_over_or))

@Expr.classmethod
def dnf(cls: type, expr: Expr):
    expr = cls.associate(cls.apply(expr, compose(cls._move_not_inwards, cls._remove_implications)))
    return cls.associate(cls.back_apply(expr, cls._distribute_or_over_and))

@Expr.classmethod
def _move_neg_inwards(cls: type, expr: Expr):
    """
    """
    #pylint: disable=unreachable
    raise NotImplementedError
    if type(expr) is cls and (expr.head == T_SUB):
        expr = expr.tail[0]
        if type(expr) is cls:
            if expr.head in cls.TABLE['NEG']:
                return cls.TABLE['NEG'][expr.head](*expr.tail)
            else:
                return cls(T_SUB, expr)
        else:
            return cls(T_SUB, expr)
    else:
        return expr

@Expr.classmethod
def _remove_subtractions(cls: type, expr: Expr):
    """
    """
    #pylint: disable=unreachable
    raise NotImplementedError
    if type(expr) is cls and expr.head == T_SUB and len(expr.tail) == 2:
        return cls(T_ADD, expr.tail[0], cls(T_SUB, expr.tail[1]))
    else:
        return expr

@Expr.classmethod
def _distribute_add_over_mul(cls: type, expr: Expr):
    """
    """
    #pylint: disable=unreachable
    raise NotImplementedError
    if type(expr) is cls and expr.head == T_MUL:
        conjs = [(p.tail if (type(p) is cls and p.head == T_ADD) else (p,)) for p in expr.tail]
        return cls(T_ADD, *(cls(T_MUL, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
    else:
        return expr

@Expr.classmethod
def anf(cls: type, expr: Expr):
    """
    """
    #pylint: disable=unreachable
    raise NotImplementedError
    expr = cls.associate(cls.apply(expr, compose(cls._move_neg_inwards, cls._remove_subtractions)))
    return cls.associate(cls.back_apply(expr, cls._distribute_add_over_mul))

@Expr.classmethod
def _logical(cls: type, item: object):
    return (type(item) is not cls) or (item.head in cls.LOGICAL) or (item.head in cls.EXTRA)

@Expr.classmethod
def logical(cls: type, expr: Expr):
    return cls.tell(expr, all, cls._logical)

@Expr.classmethod
def _arithmetic(cls: type, item: object):
    return (type(item) is not cls) or (item.head in cls.ARITHMETIC) or (item.head in cls.EXTRA)

@Expr.classmethod
def arithmetic(cls: type, expr: Expr):
    return cls.tell(expr, all, cls._arithmetic)

Expr._HASH = {
    ## Logical
    T_OR: None,
    T_AND: None,
    T_NOT: T_NOT,
    T_XOR: T_XOR,
    T_IMP: T_IMP,
    T_RIMP: T_IMP,
    T_IFF: None,

    ## Arithmetic
    T_ADD: None,
    T_SUB: T_SUB,
    T_MUL: None,
    T_DIV: T_DIV,
    T_MOD: T_MOD,
    
    ## Comparisons
    T_EQ: None,
    T_NE: None,
    T_GE: T_GE,
    T_LE: T_GE,
    T_GT: T_GT,
    T_LT: T_GT,

    ## Indexing
    T_IDX: T_IDX,
}

@Expr.classmethod
def _hash(cls: type, expr: Expr):
    if type(expr) is cls:
        hash_key = cls._HASH[expr.head]
        if hash_key is None:
            return hash((expr.head, hash(sum(cls._hash(p) for p in expr.tail))))
        elif hash_key == expr.head:
            return hash((hash_key, hash(tuple(cls._hash(p) for p in expr.tail))))
        else:
            return hash((hash_key, hash(tuple(cls._hash(p) for p in reversed(expr.tail)))))
    else:
        return hash(expr)

@Expr.classmethod
def cmp(cls: type, p: Expr, q: Expr) -> bool:
    return bool(cls._hash(p) == cls._hash(q))