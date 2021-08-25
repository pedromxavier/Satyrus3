# Standard Library
from typing import Callable
import itertools as it

# Local
from .base import SatType
from ..satlib import Source, join
from ..symbols import (
    T_IDX,
    T_AND,
    T_OR,
    T_ADD,
    T_MUL,
    T_IFF,
    T_IMP,
    T_RIMP,
    T_NOT,
    T_NEG,
    T_XOR,
    T_DIV,
    T_MOD,
    T_EQ,
    T_NE,
    T_GE,
    T_LE,
    T_GT,
    T_LT,
)

## pylint:disable=no-self-argument
class Expr(SatType, tuple):
    """
    This is one of the core elements of the system. This is used to represent ASTs.
    """

    FLAT = set()
    HASH = {}
    RULES = {}
    GROUPS = {}
    FORMAT_SPECIAL = {}
    FORMAT_PATTERNS = {}
    FORMAT_FUNCTIONS = {}

    # -*- Object Creation -*-
    def __new__(
        cls,
        head: str,
        *tail: tuple,
        sort: bool = True,
        flat: bool = True,
        source: Source = None,
        lexpos: int = None,
    ):
        """An Expr instance is a (head, tail) pair representing an expression. Here is applied, according to `sort` and `flat` parameters, child sorting and n-ary expression flatening.

        Parameters
        ----------
        head : str
            Operation identifier
        tail : tuple
            Operand sequence
        """
        if sort and flat:
            return tuple.__new__(cls, (head, *cls.sort(head, cls.flat(head, tail))))
        elif sort:
            return tuple.__new__(cls, (head, *cls.sort(head, tail)))
        elif flat:
            return tuple.__new__(cls, (head, *cls.flat(head, tail)))
        else:
            return tuple.__new__(cls, (head, *tail))

    def __init__(
        self,
        head: str,
        *tail: tuple,
        sort: bool = True,
        flat: bool = True,
        source: Source = None,
        lexpos: int = None,
    ):
        SatType.__init__(self, source=source, lexpos=lexpos)
        self._flat_ = flat
        self._sort_ = sort
        self._hash_ = None

    @property
    def head(self) -> str:
        return self[0]

    @property
    def tail(self) -> list:
        return self[1:]

    # -*- Interal Expression Management -*-
    DO_SORT = {T_AND, T_OR, T_ADD, T_MUL, T_IFF}

    @classmethod
    def sort(cls, head: str, tail: list) -> list:
        """Returns sorted tail according to key function defined by `cls.SORT: object -> object`."""
        if head in cls.DO_SORT:
            return sorted(
                [
                    (
                        p
                        if (type(p) is not cls)
                        else (p if p._sort_ else cls(p.head, *p.tail))
                    )
                    for p in tail
                ],
                key=cls.SORT,
            )
        else:
            return tail

    DO_FLAT = {T_AND, T_OR, T_ADD, T_MUL, T_IDX}

    @classmethod
    def flat(cls, head: str, tail: list) -> list:
        if head in cls.DO_FLAT:
            flattail = []
            for p in tail:
                if p.is_expr and (p.head == head):
                    if p._flat_:
                        tail = p.tail
                    else:
                        tail = cls.flat(p.head, p.tail)
                    flattail.extend(tail)
                else:
                    flattail.append(p)
            return flattail
        else:
            return tail

    @classmethod
    def sorting(cls, sort: callable):
        cls.SORT = sort

    # -*- Parenthesis -*-
    PARENTHESIS = {  ## precedence groups
        ## 1
        T_IMP: 1,
        T_RIMP: 1,
        T_IFF: 1,
        ## 2
        T_OR: 2,
        ## 3
        T_AND: 3,
        ## 4
        T_NOT: 4,
        T_ADD: 5,
        T_NEG: 4.5,
        T_MUL: 6,
    }

    @classmethod
    def parenthesise(cls, root: object, child: object) -> bool:
        if root.is_expr and child.is_expr:
            return cls._parenthesise(root.head, child.head)
        else:
            return False

    @classmethod
    def _parenthesise(cls, head_x: str, head_y: str):
        if head_x not in cls.PARENTHESIS:
            return False
        elif head_y not in cls.PARENTHESIS:
            return False
        elif cls.PARENTHESIS[head_x] > cls.PARENTHESIS[head_y]:
            return True
        else:
            return False

    def __str__(self):
        tail = [(f"({p})" if self.parenthesise(self, p) else str(p)) for p in self.tail]
        if self.head in self.FORMAT_PATTERNS:
            return self.FORMAT_PATTERNS[self.head].format(self.head, *tail)
        elif self.head in self.FORMAT_FUNCTIONS:
            return self.FORMAT_FUNCTIONS[self.head](self.head, *tail)
        elif self.head in self.FORMAT_SPECIAL:
            return self.FORMAT_SPECIAL[self.head](type(self), self.head, self.tail)
        else:
            return join(" ", [self.head, *tail])

    def __repr__(self):
        return f"Expr({join(', ', self, repr)})"

    # -*- Hash Computing -*-
    HASH_COM = lambda h: (lambda *X: hash((h, hash(sum(map(hash, X))))))
    HASH_NCM = lambda h: (lambda *X: hash((h, hash(tuple(map(hash, X))))))
    HASH_REV = lambda h: (lambda *X: hash((h, hash(tuple(map(hash, reversed(X)))))))
    HASH_IDP = lambda h: (lambda x: (ord(h) - hash(x)))

    HASH = {
        ## Logical
        T_OR: HASH_COM(T_OR),
        T_AND: HASH_COM(T_AND),
        T_NOT: HASH_IDP(T_NOT),
        T_XOR: HASH_NCM(T_XOR),
        T_IMP: HASH_NCM(T_IMP),
        T_RIMP: HASH_REV(T_IMP),
        T_IFF: HASH_COM(T_IFF),
        ## Arithmetic
        T_ADD: HASH_COM(T_ADD),
        T_NEG: HASH_IDP(T_NEG),
        T_MUL: HASH_COM(T_MUL),
        T_DIV: HASH_NCM(T_DIV),
        T_MOD: HASH_NCM(T_MOD),
        ## Comparisons
        T_EQ: HASH_COM(T_EQ),
        T_NE: HASH_COM(T_NE),
        T_GE: HASH_NCM(T_GE),
        T_LE: HASH_NCM(T_GE),
        T_GT: HASH_NCM(T_GT),
        T_LT: HASH_NCM(T_GT),
        ## Indexing
        T_IDX: HASH_NCM(T_IDX),
    }

    def __hash__(self):
        if self._hash_ is None:
            self._hash_ = self.HASH[self.head](*self.tail)
        return self._hash_

    # -*- Computation Rules -*-
    @classmethod
    def rule(cls, token: str):
        def decor(callback: callable):
            if token in cls.RULES:
                cls.RULES[token].append(callback)
            else:
                cls.RULES[token] = [callback]

        return decor

    @classmethod
    def apply_rule(cls, expr: SatType) -> SatType:
        """"""
        if expr.is_expr:
            if expr.head in cls.RULES:
                e = expr
                for rule in cls.RULES[expr.head]:
                    if e.is_expr and (expr.head == e.head):
                        e = rule(cls, *e.tail)
                    else:
                        return cls.apply_rule(e)
                else:
                    return e
            else:
                return expr
        else:
            return expr

    @classmethod
    def calculate(cls, expr: SatType) -> SatType:
        """\
        Applies rules as described in `cls.RULES` for each expression, in a backward fashion i.e. from leaves to root, then, applies forward. As result, may yield Var, Number or Expr.
        
        Parameters
        ----------
        expr : SatType
            Expression to calculate.

        Returns
        -------
        SatType
        """
        return cls.apply(cls.back_apply(expr, cls.apply_rule), cls.apply_rule)

    @classmethod
    def transverse(cls, e: SatType, f: Callable, *args, **kwargs) -> None:
        """
        Transverses expression tree calling `func` on leaves.

        Parameters
        ----------
        e : SatType
            Expression to be transversed.
        f : Callable
            Function `f(e: SatType, *args, **kwargs)`.
        *args : tuple (optional)
            `f`'s positional arguments
        **kwargs : dict (optional)
            `f`'s key-word arguments
        """
        if e.is_expr:
            for x in e.tail:
                cls.transverse(x, f, *args, **kwargs)
        else:
            f(e, *args, **kwargs)

    @classmethod
    def seek(cls, e: SatType, f, *a, **kw) -> list:
        """\
        Seeks, depth-first, for tree leaves who satisfy `func`.

        Parameters
        ----------
        e : SatType
            Expression to be seeked.
        f : Callable
            Function `f(e: SatType, *args, **kwargs) -> bool`.
        *a : tuple (optional)
            `f`'s positional arguments
        **kw : dict (optional)
            `f`'s key-word arguments
        """
        if e.is_expr:
            return [y for x in e.tail for y in cls.seek(x, f, *a, **kw)]
        else:
            if f(e, *a, **kw):
                return [e]
            else:
                return []

    @classmethod
    def tell(cls, e: SatType, c: Callable, f: Callable, *a: tuple, **kw: dict) -> bool:
        """Returns either `True` or `False` if `choice` subtrees
        satisfies `func`.
        """
        if e.is_expr:
            h = (f(e, *a, **kw),)
            t = (cls.tell(x, c, f, *a, **kw) for x in e.tail)
            return c(it.chain(h, t))
        else:
            return f(e, *a, **kw)

    @classmethod
    def apply(cls, e: SatType, f: Callable, *a: tuple, **kw: dict):
        """\
            Forward-applies function `f` to `e`.

        >>> def func(expr, *args, **kwargs):
        ...    new_expr = ...
        ...    return new_expr
        """

        e = f(e, *a, **kw)

        if e.is_expr:
            t = (cls.apply(x, f, *a, **kw) for x in e.tail)
            return cls(e.head, *t)
        else:
            return e

    @classmethod
    def back_apply(cls, e: SatType, f: Callable, *a: tuple, **kw: dict):
        """Backward-applies function `func` to `expr`."""
        if e.is_expr:
            t = (cls.back_apply(x, f, *a, **kw) for x in e.tail)
            return f(cls(e.head, *t, *a, **kw))
        else:
            return f(e, *a, **kw)

    @classmethod
    def sub(cls, e: SatType, x: SatType, y: SatType) -> SatType:
        """\
        Substitutes 'x' for 'y' in 'e'.

        Parameters
        ----------
        e : SatType
            Expression to be seeked.
        f : Callable
            Function `f(e: SatType, *args, **kwargs) -> bool`.
        *a : tuple (optional)
            `f`'s positional arguments
        **kw : dict (optional)
            `f`'s key-word arguments
        """
        return cls.apply(e, lambda z: ((y if (z == x) else z) if z.is_var else z))

    # -*- Subtype Checking -*-
    @property
    def is_expr(self) -> bool:
        return True

    @property
    def is_number(self) -> bool:
        return False

    @property
    def is_array(self) -> bool:
        return False

    @property
    def is_var(self) -> bool:
        return False

    # -*- Operator Definition -*-
    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)

    def __ne__(self, other) -> bool:
        return hash(self) != hash(other)

    def _IDX_(self, i: tuple):
        raise SatTypeError(f"Can not index object of type `{type(self)}`.", target=self)

    ## Some aliases
    def __invert__(self):
        return self._NOT_()

    def __and__(self, other):
        return self._AND_(other)

    def __or__(self, other):
        return self._OR_(other)

    def __xor__(self, other):
        return self._XOR_(other)

    def __neg__(self):
        return self._NEG_()

    def __add__(self, other):
        return self._ADD_(other)

    def __mul__(self, other):
        return self._MUL_(other)

    def _IDX_(e, i: tuple):
        return Expr(T_IDX, e, *i)

    FORMAT_PATTERNS = {
        ## Logical
        T_XOR: "{1} {0} {2}",
        T_NOT: "{0}{1}",
        T_IMP: "{1} {0} {2}",
        T_RIMP: "{1} {0} {2}",
        T_IFF: "{1} {0} {2}",
        ## Arithmetic
        T_NEG: "{0}{1}",
        T_DIV: "{1} {0} {2}",
        T_MOD: "{1} {0} {2}",
        ## Comparison
        T_EQ: "{1} {0} {2}",
        T_LE: "{1} {0} {2}",
        T_GE: "{1} {0} {2}",
        T_LT: "{1} {0} {2}",
        T_GT: "{1} {0} {2}",
        T_NE: "{1} {0} {2}",
    }

    FORMAT_SPECIAL = {T_ADD: F_ADD}

    FORMAT_FUNCTIONS = {
        ## Arithmetic
        T_MUL: (lambda head, *tail: (join(f" {head} ", tail))),
        ## Logical
        T_AND: (lambda head, *tail: (join(f" {head} ", tail))),
        T_OR: (lambda head, *tail: (join(f" {head} ", tail))),
        ## Indexing
        T_IDX: (
            lambda head, *tail: f"{tail[0]}{join('', [f'[{x}]' for x in tail[1:]])}"
        ),
    }

    TABLE = {}

    TABLE["IMP"] = {
        T_IMP: (lambda A, B: A._NOT_()._OR_(B)),
        T_RIMP: (lambda A, B: A._OR_(B._NOT_())),
        T_IFF: (lambda A, B: (A._NOT_()._AND_(B._NOT_())._OR_(A._AND_(B)))),
    }

    TABLE["XOR"] = {
        T_XOR: (lambda A, B: (~A & B) | (A & ~B)),
    }

    TABLE[T_NEG] = {
        # AND, OR, XOR:
        T_ADD: (lambda cls, *X: cls(T_ADD, *(x._NEG_() for x in X))),
        T_MUL: (lambda cls, x, *Y: cls(T_MUL, x._NEG_(), *Y)),
        T_NEG: (lambda cls, x: x),
        # Implications:
        T_DIV: (lambda cls, x, y: x._NEG_()._DIV_(y)),
    }

    @classmethod
    def _remove_implications(cls, expr):
        if type(expr) is cls and expr.head in cls.TABLE["IMP"]:
            return cls.TABLE["IMP"][expr.head](*expr.tail)
        elif type(expr) is cls and expr.head in cls.TABLE["XOR"]:
            return cls.TABLE["XOR"][expr.head](*expr.tail)
        else:
            return expr

    @classmethod
    def _move_not_inwards(cls, expr):
        if type(expr) is cls and expr.head == T_NOT:
            expr = expr.tail[0]
            if type(expr) is Expr:
                if expr.head in cls.TABLE["NOT"]:
                    return cls.TABLE["NOT"][expr.head](*expr.tail)
                else:
                    return cls(T_NOT, expr)
            else:
                return cls(T_NOT, expr)
        else:
            return expr

    @classmethod
    def _distribute_and_over_or(cls, expr):
        if type(expr) is cls and expr.head == T_OR:
            conjs = [
                (p.tail if (type(p) is cls and p.head == T_AND) else (p,))
                for p in expr.tail
            ]
            return cls(
                T_AND,
                *(
                    cls(T_OR, *z)
                    for z in reduce(
                        lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()]
                    )
                ),
            )
        else:
            return expr

    @classmethod
    def _distribute_or_over_and(cls, expr):
        if type(expr) is cls and expr.head == T_AND:
            conjs = [
                (p.tail if (type(p) is cls and p.head == T_OR) else (p,))
                for p in expr.tail
            ]
            return cls(
                T_OR,
                *(
                    cls(T_AND, *z)
                    for z in reduce(
                        lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()]
                    )
                ),
            )
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
        """"""
        if type(expr) is cls and (expr.head == T_NEG):
            expr = expr.tail[0]
            if type(expr) is cls:
                if expr.head in cls.TABLE[T_NEG]:
                    return cls.TABLE[T_NEG][expr.head](cls, *expr.tail)
                else:
                    return cls(T_NEG, expr)
            else:
                return cls(T_NEG, expr)
        else:
            return expr

    @classmethod
    def _remove_subtractions(cls: type, expr: Expr):
        """"""
        if type(expr) is cls and expr.head == T_NEG and len(expr.tail) == 2:
            return cls(T_ADD, expr.tail[0], cls(T_NEG, expr.tail[1]))
        else:
            return expr

    @classmethod
    def _distribute_add_over_mul(cls: type, expr: Expr):
        """"""
        if type(expr) is cls and expr.head == T_MUL:
            conjs = [
                (p.tail if (type(p) is cls and p.head == T_ADD) else (p,))
                for p in expr.tail
            ]
            return cls(
                T_ADD,
                *(
                    cls(T_MUL, *z)
                    for z in reduce(
                        lambda X, Y: [(*x, y) for x in X for y in Y], conjs, [()]
                    )
                ),
            )
        else:
            return expr

    @classmethod
    def anf(cls: type, expr: Expr):
        """"""
        expr = cls.apply(expr, compose(cls._move_neg_inwards, cls._remove_subtractions))
        return cls.back_apply(expr, cls._distribute_add_over_mul)

    @classmethod
    def _logical(cls: type, item: SatType):
        return (
            (type(item) is not cls)
            or (item.head in T_LOGICAL)
            or (item.head in T_EXTRA)
        )

    @property
    def logical(self) -> bool:
        return self.tell(self, all, self._logical)

    @classmethod
    def _arithmetic(cls: type, item: SatType):
        return (
            (type(item) is not cls)
            or (item.head in T_ARITHMETIC)
            or (item.head in T_EXTRA)
        )

    @property
    def arithmetic(self) -> bool:
        return self.tell(self, all, self._arithmetic)

    @classmethod
    def posiform(cls, item: SatType, boolean: bool = False) -> Posiform:
        """Turns SatType into posiform dictionary i.e. matching between terms and their respective weights.

        Note
        ----
        ``SatExpr.posiform(item: SatType, boolean: bool)`` supposes that
            1. ``item`` is already in its stable representation as a sum of products.
            2. If ``item`` is an expression, its terms are sorted (constants ahead).

        Parameters
        ----------
        item : SatType
            expression, constant or variable to be posiformed.
        boolean : bool
            allows for simplification on repeated variables within terms.

        Returns
        -------
        dict
            dictionary containing the terms as keys and the multiplying constant as respective value.
        """
        return Posiform(
            {k: v for k, v in cls._posiform(item, boolean).items() if v != Number("0")}
        )

    @classmethod
    def _posiform(cls, item: SatType, boolean: bool) -> dict:
        """"""
        if type(item) is cls:
            ## {Expr | None: Number}
            if item.head == T_ADD:
                table = {}
                for child in item.tail:
                    for p, x in cls._posiform(child, boolean).items():
                        if p in table:
                            table[p] += x
                        else:
                            table[p] = x
                else:
                    return table

            elif item.head == T_MUL:
                table = {}
                for child in item.tail:
                    if table:
                        next_table = {}
                        for p, x in table.items():
                            for q, y in cls._posiform(child, boolean).items():
                                if type(p) is tuple:  ## Variable term
                                    if boolean:
                                        key = tuple(sorted({*p, *q}))
                                    else:
                                        key = tuple({*p, *q})
                                elif p is None:  ## Constant
                                    key = q
                                else:
                                    raise TypeError(
                                        f"Invalid type `{type(p)}` as posiform multiplicative term."
                                    )

                                val = x * y

                                if key in next_table:
                                    next_table[key] += val
                                else:
                                    next_table[key] = val
                        else:
                            table = next_table
                    else:
                        table = cls._posiform(child, boolean)
                else:
                    return table

            elif item.head == T_NEG:
                return {
                    term: cons._NEG_()
                    for term, cons in cls._posiform(item[1], boolean).items()
                }
            else:
                raise TypeError(
                    f"Posiform candidates must be copositions of addition, negation and multiplication only."
                )

        elif type(item) is Number:
            return {None: item}
        elif type(item) is Var:
            return {(item,): Number("1")}
        else:
            raise TypeError(f"Invalid type `{type(item)}` for posiform.")


## Expression  Tables
SatExpr.TABLE["NOT"] = {
    # AND, OR, XOR:
    T_AND: (lambda *X: SatExpr(T_OR, *(x._NOT_() for x in X))),
    T_OR: (lambda *X: SatExpr(T_AND, *(x._NOT_() for x in X))),
    T_XOR: (lambda A, B: A.__iff__(B)),
    # Implications:
    T_IMP: (lambda A, B: A & ~B),
    T_RIMP: (lambda A, B: ~A & B),
    T_IFF: (lambda A, B: A ^ B),
    # Double NOT:
    T_NOT: (lambda A: A),
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
        raise TypeError(f"Invalid type for comparison {type(p)} in `{p}`.")


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

    cons = reduce(lambda x, y: x._AND_(y), cons_table, Number("1"))

    if cons == Number.F:
        return Number.F
    elif cons == Number.T:
        if len(expr_table) == 0:
            return Number.T
        elif len(expr_table) == 1:
            return expr_table.pop(next(iter(expr_table.keys())))
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

    cons = reduce(lambda x, y: x._OR_(y), cons_table, Number("0"))

    if cons == Number.T:
        return Number.T
    elif cons == Number.F:
        if len(expr_table) == 0:
            return Number.F
        elif len(expr_table) == 1:
            return expr_table.pop(next(iter(expr_table.keys())))
        else:
            return cls(T_OR, *expr_table.values())
    else:
        if len(expr_table) == 0:
            return cons
        else:
            return cls(T_OR, cons, *expr_table.values())


@SatExpr.rule(T_NOT)
def R_NOT(cls: type, x: SatType):
    if type(x) is cls:
        if x.head == T_NOT:
            return x[1]
        elif x.head == T_AND:
            return cls(T_OR, *(p._NOT_() for p in x.tail))
        elif x.head == T_OR:
            return cls(T_AND, *(p._NOT_() for p in x.tail))
        else:
            return x._NOT_()
    else:
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
        elif (type(p) is cls) and (p.head == T_MUL) and (type(p[1]) is Number):
            c, *t = p[1:]
            if len(t) == 1:
                q = t[0]
            else:
                q = cls(T_MUL, *t)

            if hash(q) in hash_table:
                expr_table[hash(q)] += c
            else:
                hash_table[hash(q)] = q
                expr_table[hash(q)] = c
        elif hash(p) in hash_table:
            expr_table[hash(p)] += Number("1")
        else:
            hash_table[hash(p)] = p
            expr_table[hash(p)] = Number("1")

    cons = reduce(lambda x, y: x._ADD_(y), cons_table, Number("0"))

    tail = [
        (hash_table[h] if (c == Number("1")) else cls(T_MUL, c, hash_table[h]))
        for h, c in expr_table.items()
    ]

    if cons != Number("0"):
        if len(tail) == 0:
            return cons
        else:
            return cls(T_ADD, cons, *tail)
    else:
        if len(tail) == 0:
            return Number("0")
        elif len(tail) == 1:
            return tail[0]
        else:
            return cls(T_ADD, *tail)


@SatExpr.rule(T_MUL)
def R_MUL(cls: type, *tail: tuple):
    cons_table = []
    expr_table = []

    even = True

    for p in tail:
        if type(p) is Number:
            if p < 0:
                even = not even
                cons_table.append(abs(p))
            else:
                cons_table.append(p)
        elif type(p) is cls and p.head == T_NEG:
            even = not even
            expr_table.append(p[1])
        else:
            expr_table.append(p)

    cons = reduce(lambda x, y: x._MUL_(y), cons_table, Number("1"))

    if cons != Number("1"):
        if len(expr_table) == 0:
            return cons if even else -cons
        else:
            return (
                cls(T_MUL, cons, *expr_table)
                if even
                else cls(T_MUL, -cons, *expr_table)
            )
    else:
        if len(expr_table) == 0:
            return Number("1") if even else Number("-1")
        elif len(expr_table) == 1:
            return expr_table[0] if even else cls(T_NEG, expr_table[0])
        else:
            return (
                cls(T_MUL, *expr_table)
                if even
                else cls(T_MUL, cls(T_NEG, expr_table[0]), *expr_table[1:])
            )


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
        return Number("1")
    elif len(fulltail) == 1:
        return fulltail[0]
    else:
        return cls(T_ADD, *fulltail)


@SatExpr.rule(T_NEG)
def R_NEG(cls: type, x: SatType):
    if type(x) is cls and x.head in cls.TABLE[T_NEG]:
        return cls.TABLE[T_NEG][x.head](cls, *x.tail)
    else:
        return x._NEG_()


@SatExpr.rule(T_DIV)
def R_DIV(cls: type, x: SatType, y: SatType):
    return x._DIV_(y)


@SatExpr.rule(T_MOD)
def R_MOD(cls: type, x: SatType, y: SatType):
    return x._MOD_(y)


@SatExpr.rule(T_IDX)
def R_IDX(cls: type, x: SatType, *i: tuple):
    return x._IDX_(i)


## Comparisons
@SatExpr.rule(T_EQ)
def R_EQ(cls: type, x: SatType, y: SatType):
    return x._EQ_(y)


@SatExpr.rule(T_NE)
def R_NE(cls: type, x: SatType, y: SatType):
    return x._NE_(y)


@SatExpr.rule(T_LE)
def R_LE(cls: type, x: SatType, y: SatType):
    return x._LE_(y)


@SatExpr.rule(T_GE)
def R_GE(cls: type, x: SatType, y: SatType):
    return x._GE_(y)


@SatExpr.rule(T_LT)
def R_LT(cls: type, x: SatType, y: SatType):
    return x._LT_(y)


@SatExpr.rule(T_GT)
def R_GT(cls: type, x: SatType, y: SatType):
    return x._GT_(y)