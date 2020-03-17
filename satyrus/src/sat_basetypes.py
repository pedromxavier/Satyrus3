class BaseSatType(object):

    def __eq__(a, b):
        return Expr('==', a, b, format="{1} {0} {2}")

    def __le__(a, b):
        return Expr('<=', a, b, format="{1} {0} {2}")

    def __lt__(a, b):
        return Expr('<', a, b, format="{1} {0} {2}")

    def __ge__(a, b):
        return Expr('>=', a, b, format="{1} {0} {2}")

    def __gt__(a, b):
        return Expr('>', a, b, format="{1} {0} {2}")

    def __neg__(a):
        return Expr('-', a, format="{0}{1}")

    def __pos__(a):
        return Expr('+', a, format="{0}{1}")

    def __mul__(a, b):
        return Expr('*', a, b, format="{1} {0} {2}")

    def __rmul__(a, b):
        return Expr('*', b, a, format="{1} {0} {2}")

    def __add__(a, b):
        return Expr('+', a, b, format="{1} {0} {2}")

    def __radd__(a, b):
        return Expr('+', b, a, format="{1} {0} {2}")

    def __sub__(a, b):
        return Expr('-', a, b, format="{1} {0} {2}")

    def __rsub__(a, b):
        return Expr('-', b, a, format="{1} {0} {2}")

    def __truediv__(a, b):
        return Expr('/', a, b, format="{1} {0} {2}")

    def __rtruediv__(a, b):
        return Expr('/', b, a, format="{1} {0} {2}")

    # Logic
    def __and__(a, b):
        return Expr('&', a, b, format="{1} {0} {2}")

    def __rand__(a, b):
        return Expr('&', b, a, format="{1} {0} {2}")

    def __or__(a, b):
        return Expr('|', a, b, format="{1} {0} {2}")

    def __ror__(a, b):
        return Expr('|', b, a, format="{1} {0} {2}")

    def __xor__(a, b):
        return Expr('^', a, b, format="{1} {0} {2}")

    def __rxor__(a, b):
        return Expr('^', b, a, format="{1} {0} {2}")

    def __imp__(a, b):
        return Expr('->', a, b, format="{1} {0} {2}")

    def __rimp__(a, b):
        return Expr('<-', a, b, format="{1} {0} {2}")

    def __iff__(a, b):
        return Expr('<->', a, b, format="{1} {0} {2}")

    def __not__(a):
        return a.__invert__()

    def __invert__(a):
        return Expr('~', a, format="{0}{1}")
