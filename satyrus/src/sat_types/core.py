from .expr import Expr

class SatType(object):

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