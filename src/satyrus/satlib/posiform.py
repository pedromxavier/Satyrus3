""""""
# Future
from __future__ import annotations

# Standard Library
import json
import numbers

# Third-Party
import numpy as np


class Posiform(dict):
    """\
    This object is intended to represent a sum of products under a psudo-boolean domain.

    Assumptions
    -----------
    1. Every variable is boolean (i.e. $x \in \{0, 1\}$)
    2. Posiform is a mutable type.
    """

    def __init__(self, buffer: dict | float = None):
        """\
        Parameters
        ----------
        buffer : dict
            Dictionary containing pairs (variables, constant).
        """
        if buffer is not None:
            if isinstance(buffer, dict):
                __buffer = {}
                for k, v in buffer.items():
                    if not isinstance(v, numbers.Number) or isinstance(v, complex):
                        raise TypeError("Posiform buffer values must be real numbers")
                    elif float(v) == 0.0:
                        continue

                    if k is None:
                        __buffer[k] = float(v)
                    else:
                        if not isinstance(k, (list, tuple, set, frozenset)) or not all(isinstance(s, str) for s in k):
                            raise TypeError("Posiform buffer keys must be 'None' or be of type 'list', 'tuple' or 'set' and contain only 'strings'.")
                        else:
                            __buffer[frozenset(map(str, k))] = float(v)
            elif isinstance(buffer, numbers.Number):
                if buffer == 0.0:
                    __buffer = {}
                else:
                    __buffer = {None: float(buffer)}
            else:
                raise TypeError("Posiform buffer must be of type 'dict' or 'None'.")
        else:
            __buffer = {}
        dict.__init__(self, __buffer)
        self.__aux = 0

    def __str__(self) -> str:
        if self:
            terms = []
            for k,v in self:
                if k is None:
                    if v >= 0.0:
                        terms.extend(["+", str(v)])
                    else:
                        terms.extend(["-", str(abs(v))])
                else:
                    if v == 1.0:
                        terms.extend(["+", " * ".join(k)])
                    elif v == -1.0:
                        terms.extend(["-", " * ".join(k)])
                    elif v >= 0.0:
                        terms.extend(["+", " * ".join([str(v), *k])])
                    else:
                        terms.extend(["-", " * ".join([str(abs(v)), *k])])
            else:
                return " ".join(terms[1:] if terms[0] == "+" else terms)
        else:
            return "0.0"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict.__repr__(self)})"

    def __iter__(self):
        return iter(dict.items(self))

    def copy(self) -> Posiform:
        """Deep Posiform copy."""
        return Posiform({k: v for k, v in self})

    def __add__(self, other) -> Posiform:
        posiform = self.copy()
        posiform = posiform.__iadd__(other)
        return posiform

    def __iadd__(self, other) -> Posiform:
        if isinstance(other, dict):
            try:
                other = self.cls(other)
            except TypeError as type_error:
                raise TypeError("Unable to cast operand to Posiform type.") from type_error
        if isinstance(other, type(self)):
            for k, v in other:
                if k in self:
                    w = self[k] + v
                    if w == 0.0:
                        del self[k]
                    else:
                        self[k] = w
                else:
                    self[k] = v
            return self
        elif isinstance(other, numbers.Number) and not isinstance(other, complex):
            if None in self:
                self[None] += float(other)
            else:
                self[None] = float(other)
            return self
        else:
            return NotImplemented

    def __neg__(self) -> Posiform:
        posiform = self.cls()
        for k, v in self:
            posiform[k] = -v
        return posiform

    def __rsub__(self, other) -> Posiform:
        return self.__sub__(other).__neg__()

    def __sub__(self, other) -> Posiform:
        posiform = self.copy()
        posiform = posiform.__isub__(other)
        return posiform

    def __isub__(self, other) -> Posiform:
        if isinstance(other, dict):
            try:
                other = self.cls(other)
            except TypeError as type_error:
                raise TypeError("Unable to cast operand to Posiform type.") from type_error
        if isinstance(other, type(self)):
            for k, v in other.items():
                if k in self:
                    w = self[k] - v
                    if w == 0.0:
                        del self[k]
                    else:
                        self[k] = w
                else:
                    self[k] = - v
            return self
        elif isinstance(other, numbers.Number) and not isinstance(other, complex):
            if None in self:
                self[None] -= float(other)
            else:
                self[None] = -float(other)
            return self
        else:
            return NotImplemented

    def __truediv__(self, other) -> Posiform:
        posiform = self.copy()
        posiform /= other
        return posiform

    def __itruediv__(self, other) -> Posiform:
        if isinstance(other, numbers.Number):
            c = float(other)
            if c != 0.0:
                for k, v in self:
                    self[k] = v / c
            else:
                raise ZeroDivisionError("division by zero")
        else:
            return NotImplemented

    def __mul__(self, other) -> Posiform:
        posiform = self.copy()
        posiform *= other
        return posiform

    def __imul__(self, other):
        if isinstance(other, dict):
            try:
                other = self.cls(other)
            except TypeError as type_error:
                raise TypeError("Unable to cast operand to Posiform type") from type_error
        if isinstance(other, type(self)):
            posiform = Posiform()
            for kx, vx in self:
                for ky, vy in other:
                    if kx is None:
                        k = ky
                    elif ky is None:
                        k = kx
                    else:
                        k = frozenset({*kx, *ky})

                    v = vx * vy

                    if k in posiform:
                        w = posiform[k] + v
                        if w == 0.0:
                            del posiform[k]
                        else:
                            posiform[k] = w
                    else:
                        posiform[k] = v
            return posiform
        elif isinstance(other, numbers.Number) and not isinstance(other, complex):
            w = float(other)
            if w == 0.0:
                self.clear()
            else:
                for k, v in self:
                    self[k] = w * v
            return self
        else:
            return NotImplemented

    __radd__ = __add__
    __rmul__ = __mul__

    @property
    def aux(self) -> str:
        self.__aux += 1
        return f"${self.__aux}"

    def reduce_degree(self) -> Posiform:
        """"""
        ## Reset ancillary variable counter
        self.__aux = 0

        posiform = Posiform()
        for X, a in self:
            posiform += self.__reduce_term(X, a)
        return posiform

    def __reduce_term(self, X: frozenset, a: float) -> Posiform:
        """
        Parameters
        ----------
        X : frozenset[str], tuple[str], list[str], set[str]
            Tuple with the string variable names (or None for constant term).
        a : float
            Multiplicative constant.

        Returns
        -------
        Posiform
        """
        if X is None or len(X) <= 2:
            return self.cls({X: a})
        else:
            ## Reduction by minimum selection
            w = self.aux
            x, y, *z = X

            if self.__minimum_selection():  ## minimum selection
                if a < 0:
                    ## if a < 0: a (x y z) => a w (x + y + z - 2)
                    return self.cls({(x, w): a, (y, w): a, (*z, w): a, (w,): -2.0 * a})
                else:
                    ## if a > 0: a (x y z) => a (x w + y w + z w + x y + x z + y z - x - y - z - w + 1)
                    return (
                        self.cls(
                            {
                                (x, w): a,
                                (y, w): a,
                                (x, y): a,
                                (x,): -a,
                                (y,): -a,
                                (w,): -a,
                                None: a,
                            }
                        )
                        + (self.__reduce_term((x, *z), a) + self.__reduce_term((y, *z), a) + self.__reduce_term((*z, w), a) + self.__reduce_term((*z,), -a))
                    )
            elif self.__substitution():
                alpha = 2.0  ## TODO: How can I compute alpha? (besides alpha > 1)
                return self.__reduce_term((*z, w), 1.0) + alpha * self.__P(x, y, w)
            else:
                raise NotImplementedError("Not an option.")

    @classmethod
    def __P(cls: type, x: str, y: str, w: str):
        """"""
        return cls({(x, y): 1.0, (x, w): -2.0, (y, w): -2.0, (w,): 3.0})

    def __minimum_selection(self, *args) -> bool:
        return True

    def __substitution(self, *args) -> bool:
        return True

    @property
    def variables(self):
        return sorted(set(x for k in self.keys() if k is not None for x in k))

    @property
    def cls(self):
        return self.__class__

    def toJSON(self) -> str:
        return json.dumps([{"term": list(k) if k is not None else None, "cons": v} for k, v in self], indent=4)

    @classmethod
    def fromJSON(cls, data: str) -> Posiform:
        return cls({(tuple(item["term"]) if item["term"] is not None else None): item["cons"] for item in json.loads(data)})

    def qubo(self) -> tuple[dict[str, int], np.ndarray[float], float]:
        """
        Returns
        -------
        dict[str, int]
            Mapping between variables and respective indexes.
        np.ndarray
            Symmetric Matrix representing QUBO instance.
        float
            Ground state energy.
        """
        reduced = self.reduce_degree()
        variables = reduced.variables

        n = len(variables)

        x = {v: i for i, v in enumerate(variables)}
        Q = np.zeros((n, n), dtype=float)
        c = 0.0

        for k, a in reduced:
            if k is None:
                c = a
            else:
                I = tuple(map(x.get, k))
                if len(I) == 1:
                    i = I[0]
                    Q[i, i] += a
                elif len(I) == 2:
                    i, j = I
                    Q[i, j] += a
                    Q[j, i] += a
                else:
                    raise ValueError("Degree reduction failed.")
        return x, Q, c


__all__ = ["Posiform"]
