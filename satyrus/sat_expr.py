from sat_types.expr import Expr
from sat_types.number import Number
from functools import reduce

## :: Rule Definition ::

## :: Logical ::
from sat_types.symbols.heads import H_AND, H_OR, H_XOR, H_NOT, H_IFF, H_IMP, H_RIMP

@Expr.rule(H_AND)
def AND(*args):
    return reduce(lambda x, y : x.__and__(y), args)

@Expr.rule(H_OR)
def OR(*args):
    return reduce(lambda x, y : x.__or__(y), args)

@Expr.rule(H_XOR)
def XOR(x, y):
    return x.__xor__(y)

@Expr.rule(H_NOT)
def NOT(x):
    return x.__not__()

@Expr.rule(H_IMP)
def IMP(x, y):
    return x.__imp__(y)

@Expr.rule(H_RIMP)
def RIMP(x, y):
    return x.__rimp__(y)

@Expr.rule(H_IFF)
def IFF(x, y):
    return x.__iff__(y)

## :: Indexing ::
from sat_types.symbols.heads import H_IDX

@Expr.rule(H_IDX)
def IDX(x, i):
    return x.__idx__(i)

## :: Aritmetic ::
from sat_types.symbols.heads import H_ADD, H_SUB, H_MUL, H_DIV, H_POS, H_NEG

@Expr.rule(H_ADD)
def ADD(*args):
    return reduce(lambda x, y : x.__add__(y), args)

@Expr.rule(H_SUB)
def r_SUB(x, y):
    return x.__sub__(y)

@Expr.rule(H_MUL)
def r_MUL(*args):
    return reduce(lambda x, y : x.__mul__(y), args)

@Expr.rule(H_DIV)
def r_DIV(x, y):
    return x.__truediv__(y)

@Expr.rule(H_POS)
def r_POS(x):
    return x.__pos__()

@Expr.rule(H_NEG)
def r_NEG(x):
    return x.__neg__()

Expr.FORMATS.update({
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
    })

Expr.GROUPS.update({
    H_ADD : 1, H_ADD : 1, H_SUB : 1,
    H_MUL : 2, H_DIV : 2,
    H_AND : 3,
    H_OR  : 4, H_XOR : 4,
    H_ADD : 5, H_SUB : 5,
    H_NOT : 6,
    H_IMP : 7, H_RIMP: 7, H_IFF : 7,
    H_IDX : 8,
    })

Expr.TABLE['LOGIC'] = {
    H_AND,
    H_OR ,
    H_XOR,
    H_NOT,
    H_IMP, H_RIMP, H_IFF,
    H_IDX,
    }

Expr.TABLE['PSEUDO_LOGIC'] = {
    H_MUL, H_ADD, H_SUB, H_POS, H_NEG,
    }

Expr.TABLE['IMP_TABLE'] = {
    H_IMP  : lambda A, B : ~A | B,
    H_RIMP : lambda A, B : A | ~B,
    H_IFF  : lambda A, B : (~A & ~B) | (A & B),
    }

Expr.TABLE['LMS_TABLE'] = {
    H_AND : lambda x, y : x * y,
    H_OR  : lambda x, y : x + y - x * y,
    H_NOT : lambda x : Number.TRUE - x, # 1 - x
    }

Expr.TABLE['NOT'] = {
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
    }

Expr.TABLE['XOR'] = {
    H_XOR : lambda A, B : (~A & B) | (A & ~B),
    }

Expr.NEED_PAR.update({
    H_ADD, H_SUB , H_MUL, H_DIV,
    H_AND, H_OR  , H_XOR,
    H_IMP, H_RIMP, H_IFF,
    })

Expr.HASH_SIDE.update({
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
    H_RIMP : H_IMP,
    H_IFF  : None,
    # NOT:
    H_NOT  : None,

    # Indexing:
    H_IDX  : True,
    })

@Expr.solve_func({H_IDX})
def s_index(expr, index):
    x, i = expr.tail
    if i in index:
        return Expr('[]', x, index[i])
    else:
        return expr

@Expr.solve_func({H_AND})
def s_rmv_and(expr):
    '''
    '''
    A, B = expr.tail

    if Expr.cmp(A, B):
        return A

    elif Expr.cmp(A, (~B).rmv_not()):
        return Number.FALSE

    elif Expr.cmp(A, Number.TRUE):
        return B

    elif Expr.cmp(B, Number.TRUE):
        return A

    elif Expr.cmp(A, Number.FALSE):
        return Number.FALSE

    elif Expr.cmp(B, Number.FALSE):
        return Number.FALSE

    else:
        return expr


@Expr.solve_func({H_OR})
def s_rmv_or(expr):
    '''
    '''
    A, B = expr.tail

    if Expr.cmp(A, B):
        return A

    elif Expr.cmp(A, (~B).rmv_not()):
        return Number.TRUE

    elif Expr.cmp(A, Number.TRUE):
        return Number.TRUE

    elif Expr.cmp(B, Number.TRUE):
        return Number.TRUE

    elif Expr.cmp(A, Number.FALSE):
        return B

    elif Expr.cmp(B, Number.FALSE):
        return A
    
    else:
        return expr

@Expr.solve_func({H_XOR})
def s_rmv_xor(expr):
    ''' Removes XOR.
        A ^ B : [~A & B] | [A & ~B]
    '''
    return Expr.TABLE['XOR'][expr.head](*expr.tail)
    
@Expr.solve_func({H_NOT})
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
    if expr.expr:
        return Expr.TABLE['NOT'][expr.head](*expr.tail)
    else:
        return ~expr
    
@Expr.solve_func({H_IFF, H_IMP, H_RIMP})
def s_rmv_imp(expr):
    ''' Removes Implications (->, <- and <->).
        Translation occours as:
            A -> B  : ~A | B
            A <- B  : A | ~B
            A <-> B : (~A & ~B) | (A & B)
    '''
    return Expr.TABLE['IMP'][expr.head](*expr.tail)
    
@property
def group(expr):
    return Expr.GROUPS[expr.head]