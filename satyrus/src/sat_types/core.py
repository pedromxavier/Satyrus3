from .expr import Expr

class SatType(object):

    def __eq__(self, b):
        return Expr(T_EQ, self, b)

    def __le__(self, b):
        return Expr(T_LE, self, b)

    def __lt__(self, b):
        return Expr(T_LT, self, b)

    def __ge__(self, b):
        return Expr(T_GE, self, b)

    def __gt__(self, b):
        return Expr(T_GT, self, b)

    def __neg__(self):
        return Expr(T_SUB, self)

    def __pos__(self):
        return Expr(T_ADD, self)

    def __mul__(self, b):
        return Expr(T_MUL, self, b)

    def __rmul__(self, b):
        return Expr(T_MUL, b, self)

    def __add__(self, b):
        return Expr(T_ADD, self, b)

    def __radd__(self, b):
        return Expr(T_ADD, b, self)

    def __sub__(self, b):
        return Expr(T_SUB, self, b)

    def __rsub__(self, b):
        return Expr(T_SUB, b, self)

    def __truediv__(self, b):
        return Expr(T_DIV, self, b)

    def __rtruediv__(self, b):
        return Expr(T_DIV, b, self)

    # Logic
    def __and__(self, b):
        return Expr(T_AND, self, b)

    def __rand__(self, b):
        return Expr(T_AND, b, self)

    def __or__(self, b):
        return Expr(T_OR, self, b)

    def __ror__(self, b):
        return Expr(T_OR, b, self)

    def __xor__(self, b):
        return Expr(T_XOR, self, b)

    def __rxor__(self, b):
        return Expr(T_XOR, b, self)

    def __imp__(self, b):
        return Expr(T_IMP, self, b)

    def __rimp__(self, b):
        return Expr(T_RIMP, self, b)

    def __iff__(self, b):
        return Expr(T_IFF, self, b)

    def __not__(self):
        return Expr(T_NOT, self)

    def __idx__(self, b):
        return Expr(T_IDX, self, b)

    def __invert__(self):
        return self.__not__()

    @property
    def logic(self):
        return True

    @property
    def pseudo_logic(self):
        return True

    @property
    def token(self):
        return None

    @property
    def arity(self):
        return 0

    @property
    def head(self):
        return (self.token, self.arity)

    @property
    def expr(self):
        return False

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return 1

    @property
    def vars(self):
        return set()

    @property
    def var(self):
        return False