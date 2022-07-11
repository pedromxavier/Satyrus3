""""""
# Future
from __future__ import annotations

# Standard Library
import json
import numbers

# Third-Party
import numpy as np


class Posiform(dict):
    r"""
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
                    if not isinstance(v, numbers.Real):
                        raise TypeError("Posiform buffer values must be real numbers")
                    elif float(v) == 0.0:
                        continue

                    if k is None:
                        __buffer[k] = float(v)
                    else:
                        if not isinstance(k, (tuple, set, frozenset)) or not all(isinstance(s, str) for s in k):
                            raise TypeError("Posiform buffer keys must be 'None' or be of type 'tuple' or 'set' and contain only 'strings'.")
                        else:
                            __buffer[frozenset(map(str, k))] = float(v)
            elif isinstance(buffer, numbers.Real):
                if buffer == 0.0:
                    __buffer = {}
                else:
                    __buffer = {None: float(buffer)}
            else:
                raise TypeError(f"Posiform buffer must be of type 'dict', 'float', 'int' or 'None', not '{type(buffer)}'")
        else:
            __buffer = {}
        dict.__init__(self, __buffer)
        self.__aux = 0

    def __bool__(self) -> bool:
        return len(self) > 0

    def __str__(self) -> str:
        if self:
            terms = []
            for k, v in self:
                if k is None:
                    if v >= 0.0:
                        terms.extend(["+", str(v)])
                    else:
                        terms.extend(["-", str(abs(v))])
                else:
                    if v == 1.0:
                        terms.extend(["+", " * ".join(sorted(k))])
                    elif v == -1.0:
                        terms.extend(["-", " * ".join(sorted(k))])
                    elif v >= 0.0:
                        terms.extend(["+", " * ".join([str(v), *sorted(k)])])
                    else:
                        terms.extend(["-", " * ".join([str(abs(v)), *sorted(k)])])
            return " ".join(terms[1:] if terms[0] == "+" else terms)
        else:
            return "0.0"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict.__repr__({k if k is None else tuple(sorted(k)) : v for k, v in self})})"

    def __iter__(self):
        return iter(dict.items(self))

    def copy(self) -> Posiform:
        """Deep Posiform copy."""
        return Posiform({k: v for k, v in self})

    def __float__(self) -> float:
        if len(self) == 0:
            return 0.0
        elif len(self) == 1 and None in self:
            return self[None]
        else:
            raise TypeError("Can't cast 'Posiform' to 'float' due to non-constant terms")
            

    def __call__(self, point: dict) -> Posiform:
        """"""

        if isinstance(point, dict):

            posiform = Posiform()

            term: frozenset | None
            cons: float

            for term, cons in self:
                if term is None:
                    if None in posiform:
                        posiform[None] += cons
                    else:
                        posiform[term] = cons
                    continue
                
                for x in point:
                    if not isinstance(x, str):
                        raise TypeError(f"Variables must be of type 'str', not '{type(x)}'")

                    c = point[x]

                    if isinstance(c, str):
                        if x in term:
                            term -= {x}
                            term |= {c}
                    elif isinstance(c, numbers.Real):
                        if x in term:
                            term -= {x}
                            cons *= c
                    else:
                        raise TypeError(f"Evaluation point coordinates must be either real numbers ('int', 'float') or variables ('str'), not '{type(c)}'")

                if not term:
                    if None in posiform:
                        posiform[None] += cons
                    else:
                        posiform[None] = cons
                elif term in posiform:
                    posiform[term] += cons
                else:
                    posiform[term] = cons

            return posiform
        else:
            raise TypeError(f"Can't evaluate Posiform at non-mapping {point} of type {type(point)}")

    def __add__(self, other) -> Posiform:
        posiform = self.copy()
        posiform = posiform.__iadd__(other)
        return posiform

    def __iadd__(self, other) -> Posiform:
        if isinstance(other, dict):
            try:
                other = self.__class__(other)
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
        posiform = self.__class__()
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
                other = self.__class__(other)
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
                    self[k] = -v
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
        posiform = posiform.__itruediv__(other)
        return posiform

    def __itruediv__(self, other) -> Posiform:
        if isinstance(other, numbers.Number):
            c = float(other)
            if c != 0.0:
                for k, v in self:
                    self[k] = v / c
                return self
            else:
                raise ZeroDivisionError("division by zero")
        else:
            return NotImplemented

    def __pow__(self, other) -> Posiform:
        posiform = self.copy()
        posiform = posiform.__ipow__(other)
        return posiform

    def __ipow__(self, other) -> Posiform:
        if isinstance(other, dict):
            try:
                other = self.__class__(other)
            except TypeError as type_error:
                raise TypeError("Unable to cast operand to 'Posiform' type") from type_error
        if isinstance(other, type(self)) or isinstance(other, numbers.Real):
            try:
                other = float(other)
            except TypeError as type_error:
                raise TypeError("Unable to cast operand to 'float' type") from type_error

            if not other.is_integer() or other < 0:
                raise TypeError("Can't raise 'Posiform' to non-integer power")
            else:
                other = int(other)

            posiform = Posiform(1.0)
            while other > 0:
                posiform *= self
                other -= 1
            return posiform
        else:
            return NotImplemented

    def __mul__(self, other) -> Posiform:
        posiform = self.copy()
        posiform = posiform.__imul__(other)
        return posiform

    def __imul__(self, other):
        if isinstance(other, dict):
            try:
                other = self.__class__(other)
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
        elif isinstance(other, numbers.Real):
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

    __RED_NO = 0 # No Reduction
    __RED_MS = 1 # Minimum Selection
    __RED_SU = 2 # Substitution

    def __reduce_strategy(self, term: frozenset, __cons: float) -> int:
        """"""
        if term is None or len(term) <= 2:
            return self.__RED_NO
        else:
            return self.__RED_MS

    def __reduce_term(self, term: frozenset, cons: float) -> Posiform:
        """
        Parameters
        ----------
        term : frozenset[str], tuple[str], list[str], set[str]
            Tuple with the string variable names (or None for constant term).
        cons : float
            Multiplicative constant.

        Returns
        -------
        Posiform
        """
        strategy = self.__reduce_strategy(term, cons) 

        if strategy == self.__RED_NO:
            return self.__class__({term: cons})
        elif strategy == self.__RED_MS:
            return self.__minimum_selection(term, cons)
        elif strategy == self.__RED_SU:
            return self.__substitution(term, cons)
        else:
            raise NotImplementedError("No more strategies were implemented")

    def __substitution(self, X: frozenset, a: float) -> Posiform:
        """"""
        w = self.aux
        x, y, *z = X
        # TODO: How can I compute alpha? (besides alpha > 1)
        alpha = 2.0
        return a * (self.__reduce_term((*z, w), 1.0) + alpha * self.__P(x, y, w))

    def __minimum_selection(self, X: frozenset, a: float) -> Posiform:
        """"""
        w = self.aux
        x, y, *z = X
        if a < 0:
            ## if a < 0: a (x y z) => a w (x + y + z - 2)
            return self.__class__({(x, w): a, (y, w): a, (w,): -2.0 * a}) + self.__reduce_term((*z, w), a)
        else:
            ## if a > 0: a (x y z) => a (x w + y w + z w + x y + x z + y z - x - y - z - w + 1)
            return (
                self.__class__(
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

    @classmethod
    def __P(cls: type, x: str, y: str, w: str):
        """"""
        return cls({(x, y): 1.0, (x, w): -2.0, (y, w): -2.0, (w,): 3.0})

    @property
    def variables(self) -> list:
        return sorted(set(x for k in self.keys() if k is not None for x in k))

    @property
    def degree(self) -> int:
        return max(map(lambda k: 0 if k is None else len(k), self))

    def toMiniJSON(self) -> str:
        return json.dumps({("" if k is None else " ".join(sorted(k))): v for k, v in self})

    @classmethod
    def fromMiniJSON(cls, data: str) -> Posiform:
        """"""
        json_data = json.loads(data)

        buffer = {}

        if not isinstance(json_data, dict):
            raise json.decoder.JSONDecodeError("Data must be of Object type (Python dict)", data, 0)
        
        for term, cons in json_data.items():
            if not isinstance(cons, (int, float)):
                raise json.decoder.JSONDecodeError("Constants must be of Number type (Python int, float)", data, 0)
            else:
                if term != "":
                    key = frozenset(term.split(" "))
                else:
                    key = None
                val = float(cons)

                if key in buffer:
                    buffer[key] += val
                else:
                    buffer[key] = val
        return cls(buffer)

    def toJSON(self, indent: int = None) -> str:
        if indent is None:
            return json.dumps([{"term": sorted(k) if k is not None else None, "cons": v} for k, v in self])
        else:
            return json.dumps([{"term": sorted(k) if k is not None else None, "cons": v} for k, v in self], indent=indent)

    @classmethod
    def fromJSON(cls, data: str) -> Posiform:
        """"""
        json_data = json.loads(data)

        buffer = {}

        if not isinstance(json_data, list):
            raise json.decoder.JSONDecodeError("Data must be of Array type (Python list)", data, 0)
        
        for item in json_data:
            if not isinstance(item, dict):
                raise json.decoder.JSONDecodeError("Items must be of Object type (Python dict)", data, 0)
            elif "term" not in item or "cons" not in item:
                raise json.decoder.JSONDecodeError("Items must contain both 'term' and 'cons' keys", data, 0)
            elif not isinstance(item["term"], list) and item["term"] is not None:
                raise json.decoder.JSONDecodeError("Items 'term' value must be of Array type (Python list)", data, 0)
            elif item["term"] is not None and not all(isinstance(var, str) for var in item["term"]):
                raise json.decoder.JSONDecodeError("Items 'term' value must contain only entries of type String (Python str)", data, 0)
            elif not isinstance(item["cons"], (int, float)):
                raise json.decoder.JSONDecodeError("Items 'cons' value must be of Number type (Python float)", data, 0)
            else:
                key = tuple(item["term"]) if item["term"] is not None else None
                val = float(item["cons"])
                if key in buffer:
                    buffer[key] += val
                else:
                    buffer[key] = val
        return cls(buffer)

    def qubo(self) -> tuple[dict[str, int], np.ndarray, float]:
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
                    Q[i, j] += a / 2.0
                    Q[j, i] += a / 2.0
                else:
                    raise RuntimeError("Degree reduction failed.")
        return x, Q, c

    def ising(self) -> tuple[dict[str, int], np.ndarray, float]:
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
        J = np.zeros((n, n), dtype=float)
        c = 0.0

        for k, a in reduced:
            if k is None:
                c = a
            else:   
                I = tuple(map(x.get, k))
                if len(I) <= 2:
                    J[I] += a
                else:
                    raise RuntimeError("Degree reduction failed.")
        return x, J, c


__all__ = ["Posiform"]
