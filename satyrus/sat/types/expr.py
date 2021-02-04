## Standard Library
from itertools import combinations
from functools import reduce
from collections import defaultdict

## Local
from ...satlib import join, compose, stderr
from .error import SatValueError
from .main import Expr, Number, Var, Array, SatType, MetaSatType

## Tokens
from .symbols.tokens import T_ADD, T_NEG, T_MUL, T_DIV, T_MOD
from .symbols.tokens import T_AND, T_XOR, T_NOT, T_OR
from .symbols.tokens import T_IMP, T_IFF, T_RIMP
from .symbols.tokens import T_EQ, T_NE, T_LE, T_GE, T_LT, T_GT
from .symbols.tokens import T_IDX
from .symbols.tokens import T_LOGICAL, T_ARITHMETIC, T_EXTRA

## Special Format
def F_ADD(cls: type, head: str, tail: list):
    def glue(i: int, e: Expr):
        if i:
            if (isinstance(e, Expr) and e.head == T_NEG) or (type(e) is Number and e < 0):
                return f" {T_NEG} "
            else:
                return f" {T_ADD} "
        else:
            return ""

    def func(i: int, e: Expr):
        if i:
            if isinstance(e, Expr):
                if e.head == T_NEG:
                    x = e.tail[0]
                    if isinstance(x, Expr) and cls._parenthesise(head, x.head):
                        return f"({x})"
                    else:
                        return str(x)
                else:
                    if isinstance(e, Expr) and cls._parenthesise(head, e.head):
                        return f"({e})"
                    else:
                        return str(e)
            else:
                return str(e)
        else:
            if isinstance(e, Expr) and cls._parenthesise(head, e.head):
                return f"({e})"
            else:
                return str(e)

    return join(glue, tail, func, enum=True)

class SatExpr(Expr, metaclass=MetaSatType):

    FLAT = {
        ## Logical
        T_AND, T_OR,

        ## Arithmetic
        T_ADD, T_MUL,

        ## Indexing
        T_IDX
    }

    SORTABLE = {
        T_AND, T_OR, T_ADD, T_MUL, T_IFF
    }

    HASH_SUM = lambda h: (lambda *X : hash((h, hash(sum(map(hash, X))))))
    HASH_DIR = lambda h: (lambda *X : hash((h, hash(tuple(map(hash, X))))))
    HASH_REV = lambda h: (lambda *X : hash((h, hash(tuple(map(hash, reversed(X)))))))
    HASH_IDP = lambda h: (lambda x : (ord(h) - hash(x)))

    HASH = {
        ## Logical
        T_OR  : HASH_SUM(T_OR),
        T_AND : HASH_SUM(T_AND),
        T_NOT : HASH_IDP(T_NOT),
        T_XOR : HASH_DIR(T_XOR),
        T_IMP : HASH_DIR(T_IMP),
        T_RIMP: HASH_REV(T_IMP),
        T_IFF : HASH_SUM(T_IFF),

        ## Arithmetic
        T_ADD: HASH_SUM(T_ADD),
        T_NEG: HASH_IDP(T_NEG),
        T_MUL: HASH_SUM(T_MUL),
        T_DIV: HASH_DIR(T_DIV),
        T_MOD: HASH_DIR(T_MOD),
        
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

    GROUPS = { ## precedence groups
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

        T_NEG : 4.5,

        T_MUL : 6,
    }

    FORMAT_PATTERNS = {
        ## Logical
        T_XOR : "{1} {0} {2}",
        T_NOT : "{0}{1}",

        T_IMP : "{1} {0} {2}",
        T_RIMP: "{1} {0} {2}",
        T_IFF : "{1} {0} {2}",

        ## Arithmetic
        T_NEG : "{0}{1}",
        T_DIV : "{1} {0} {2}",
        T_MOD : "{1} {0} {2}",

        ## Comparison
        T_EQ : "{1} {0} {2}",
        T_LE : "{1} {0} {2}",
        T_GE : "{1} {0} {2}",
        T_LT : "{1} {0} {2}",
        T_GT : "{1} {0} {2}",
        T_NE : "{1} {0} {2}"
    }

    FORMAT_SPECIAL = {
        T_ADD : F_ADD
    }

    FORMAT_FUNCTIONS = {
        ## Arithmetic
        T_MUL : (lambda head, *tail: (join(f' {head} ', tail))),

        ## Logical
        T_AND : (lambda head, *tail: (join(f' {head} ', tail))),
        T_OR  : (lambda head, *tail: (join(f' {head} ', tail))),

        ## Indexing
        T_IDX : (lambda head, *tail: f"{tail[0]}{join('', [f'[{x}]' for x in tail[1:]])}")
    }

    TABLE = {}

    TABLE['IMP'] = {
        T_IMP  : (lambda A, B : A._NOT_()._OR_(B)),
        T_RIMP : (lambda A, B : A._OR_(B._NOT_())),
        T_IFF  : (lambda A, B : (A._NOT_()._AND_(B._NOT_())._OR_(A._AND_(B)))),
    }

    TABLE['XOR'] = {
        T_XOR : (lambda A, B : (~A & B) | (A & ~B)),
    }

    @classmethod
    def _remove_implications(cls, expr):
        if type(expr) is cls and expr.head in cls.TABLE['IMP']:
            return cls.TABLE['IMP'][expr.head](*expr.tail)
        elif type(expr) is cls and expr.head in cls.TABLE['XOR']:
            return cls.TABLE['XOR'][expr.head](*expr.tail)
        else:
            return expr

    @classmethod
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

    @classmethod
    def _distribute_and_over_or(cls, expr):
        if type(expr) is cls and expr.head == T_OR:
            conjs = [(p.tail if (type(p) is cls and p.head == T_AND) else (p,)) for p in expr.tail]
            return cls(T_AND, *(cls(T_OR, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
        else:
            return expr

    @classmethod
    def _distribute_or_over_and(cls, expr):
        if type(expr) is cls and expr.head == T_AND:
            conjs = [(p.tail if (type(p) is cls and p.head == T_OR) else (p,)) for p in expr.tail]
            return cls(T_OR, *(cls(T_AND, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
        else:
            return expr

    @classmethod
    def cnf(cls: type, expr: Expr):
        expr = cls.apply(expr, compose(cls._move_not_inwards, cls._remove_implications))
        return cls.back_apply(expr, cls._distribute_and_over_or)

    @classmethod
    def dnf(cls: type, expr: Expr):
        expr = cls.apply(expr, compose(cls._move_not_inwards, cls._remove_implications))
        return cls.back_apply(expr, cls._distribute_or_over_and)

    @classmethod
    def _move_neg_inwards(cls: type, expr: Expr):
        """
        """
        if type(expr) is cls and (expr.head == T_NEG):
            expr = expr.tail[0]
            if type(expr) is cls:
                if expr.head in cls.TABLE['NEG']:
                    return cls.TABLE['NEG'][expr.head](*expr.tail)
                else:
                    return cls(T_NEG, expr)
            else:
                return cls(T_NEG, expr)
        else:
            return expr

    @classmethod
    def _remove_subtractions(cls: type, expr: Expr):
        """
        """
        if type(expr) is cls and expr.head == T_NEG and len(expr.tail) == 2:
            return cls(T_ADD, expr.tail[0], cls(T_NEG, expr.tail[1]))
        else:
            return expr

    @classmethod
    def _distribute_add_over_mul(cls: type, expr: Expr):
        """
        """
        if type(expr) is cls and expr.head == T_MUL:
            conjs = [(p.tail if (type(p) is cls and p.head == T_ADD) else (p,)) for p in expr.tail]
            return cls(T_ADD, *(cls(T_MUL, *z) for z in reduce(lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()])))
        else:
            return expr

    @classmethod
    def anf(cls: type, expr: Expr):
        """
        """
        expr = cls.apply(expr, compose(cls._move_neg_inwards, cls._remove_subtractions))
        return cls.back_apply(expr, cls._distribute_add_over_mul)

    @classmethod
    def _logical(cls: type, item: object):
        return (type(item) is not cls) or (item.head in T_LOGICAL) or (item.head in T_EXTRA)

    @classmethod
    def logical(cls: type, expr: Expr):
        return cls.tell(expr, all, cls._logical)

    @classmethod
    def _arithmetic(cls: type, item: object):
        return (type(item) is not cls) or (item.head in T_ARITHMETIC) or (item.head in T_EXTRA)

    @classmethod
    def arithmetic(cls: type, expr: Expr):
        return cls.tell(expr, all, cls._arithmetic)

## Expression  Tables
SatExpr.TABLE['NOT'] = {
    # AND, OR, XOR:
    T_AND  : (lambda *X : SatExpr(T_OR, *[x._NOT_() for x in X])),
    T_OR   : (lambda *X : SatExpr(T_AND, *[x._NOT_() for x in X])),
    T_XOR  : (lambda A, B : A.__iff__(B)),
    # Implications:
    T_IMP  : (lambda A, B : A & ~B),
    T_RIMP : (lambda A, B : ~A & B),
    T_IFF  : (lambda A, B : A ^ B),
    # Double NOT:
    T_NOT  : (lambda A : A)
}

SatExpr.TABLE['NEG'] = {
    # AND, OR, XOR:
    T_ADD  : (lambda *X : SatExpr(T_ADD, *[x._NEG_() for x in X])),
    T_MUL  : (lambda x, *Y : SatExpr(T_MUL, x._NEG_(), *Y)),
    T_NEG  : (lambda x : x),
    # Implications:
    T_DIV  : (lambda x, y : x._NEG_()._DIV_(y)),
}

@SatExpr.sorting
def sorting(p: SatType):
    if type(p) is Number:
        return (0, float(p))
    elif type(p) is Var:
        return (1, str(p))
    elif type(p) is Array:
        return (2, str(p.var))
    elif type(p) is SatExpr:
        return (3, hash(p))
    else:
        raise TypeError(f'Invalid type for comparison {type(p)}')

@SatExpr.rule(T_AND)
def R_AND(cls: type, *tail: tuple):
    expr_table = {}
    cons_table = []

    for p in tail:
        if type(p) is Number:
            if p == Number.T:
                continue
            elif p == Number.F:
                return Number.F
            else:
                cons_table.append(p)
        else:
            expr_table[hash(p)] = p

    cons = reduce(lambda x, y: x._AND_(y), cons_table, Number('1'))

    if cons == Number.F:
        return Number.F
    elif cons == Number.T:
        if len(expr_table) == 0:
            return Number.T
        elif len(expr_table) == 1:
            return expr_table.pop()
        else:
            return cls(T_AND, *expr_table.values())
    else:
        if len(expr_table) == 0:
            return cons
        else:
            return cls(T_AND, cons, *expr_table.values())


@SatExpr.rule(T_OR)
def R_OR(cls: type, *tail: tuple):
    expr_table = {}
    cons_table = []

    for p in tail:
        if type(p) is Number:
            if p == Number.F:
                continue
            elif p == Number.T:
                return Number.T
            else:
                cons_table.append(p)
        else:
            expr_table[hash(p)] = p

    cons = reduce(lambda x, y: x._OR_(y), cons_table, Number('0'))

    if cons == Number.T:
        return Number.T
    elif cons == Number.F:
        if len(expr_table) == 0:
            return Number.F
        elif len(expr_table) == 1:
            return expr_table.pop()
        else:
            return cls(T_OR, *expr_table.values())
    else:
        if len(expr_table) == 0:
            return cons
        else:
            return cls(T_OR, cons, *expr_table.values())

@SatExpr.rule(T_NOT)
def R_NOT(cls: type, x: SatType):
    return x._NOT_()

@SatExpr.rule(T_XOR)
def R_XOR(cls: type, x: SatType, y: SatType):
    return x._XOR_(y)

@SatExpr.rule(T_IMP)
def R_IMP(cls: type, x: SatType, y: SatType):
    return x._IMP_(y)

@SatExpr.rule(T_RIMP)
def R_RIMP(cls: type, x: SatType, y: SatType):
    return x._RIMP_(y)

@SatExpr.rule(T_IFF)
def R_IFF(cls: type, x: SatType, y: SatType):
    return x._IFF_(y)    

## ADD
@SatExpr.rule(T_ADD)
def R_ADD(cls: type, *tail: tuple):
    hash_table = {}
    expr_table = {}
    cons_table = []

    for p in tail:
        if type(p) is Number:
            cons_table.append(p)
        elif hash(p) in hash_table:
            expr_table[hash(p)] += Number('1.0')
        else:
            hash_table[hash(p)] = p
            expr_table[hash(p)] = Number('1.0')
    
    cons = reduce(lambda x, y: x._ADD_(y), cons_table, Number('0.0'))

    tail = [(hash_table[h] if (c == Number('1.0')) else cls(T_MUL, c, hash_table[h])) for h, c in expr_table.items()]

    if cons != Number('0.0'):
        if len(tail) == 0:
            return cons
        else:
            return cls(T_ADD, cons, *tail)
    else:
        if len(tail) == 0:
            return Number('0.0')
        elif len(tail) == 1:
            return tail[0]
        else:
            return cls(T_ADD, *tail)

@SatExpr.rule(T_MUL)
def R_MUL(cls: type, *tail: tuple):
    cons_table = []
    expr_table = []

    for p in tail:
        if type(p) is Number:
            cons_table.append(p)
        else:
            expr_table.append(p)
    
    cons = reduce(lambda x, y: x._MUL_(y), cons_table, Number('1.0'))

    if cons != Number('1.0'):
        if len(expr_table) == 0:
            return cons
        else:
            return cls(T_MUL, cons, *expr_table)
    else:
        if len(expr_table) == 0:
            return Number('1.0')
        elif len(expr_table) == 1:
            return expr_table[0]
        else:
            return cls(T_MUL, *expr_table)

@SatExpr.rule(T_MUL)
def R_MUL_EXPAND(cls: type, *tail: tuple):
    fulltail = []

    if not any([(type(p) is cls) and (p.head == T_ADD) for p in tail]):
        return cls(T_MUL, *tail)

    for p in tail:
        if (type(p) is cls) and (p.head == T_ADD):
            if fulltail:
                fulltail = [[*x, y] for x in fulltail for y in p.tail]
            else:
                fulltail = [[y] for y in p.tail]
        else:
            if fulltail:
                fulltail = [[*x, p] for x in fulltail]
            else:
                fulltail = [[p]]
    
    fulltail = [q[0] if (len(q) == 1) else cls(T_MUL, *q) for q in fulltail]

    if len(fulltail) == 0:
        return Number('1.0')
    elif len(fulltail) == 1:
        return fulltail[0]
    else:
        return cls(T_ADD, *fulltail)

@SatExpr.rule(T_NEG)
def R_NEG(cls: type, x: SatType):
    return x._NEG_()

@SatExpr.rule(T_DIV)
def R_DIV(cls: type, x: SatType, y: SatType):
    return x._DIV_(y)

@SatExpr.rule(T_MOD)
def R_MOD(cls: type, x: SatType, y: SatType):
    return x._MOD_(y)

@SatExpr.rule(T_IDX)
def R_IDX(cls: type, x: SatType, i: tuple):
    raise NotImplementedError








