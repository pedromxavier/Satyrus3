import sys

try:
    from numpy import zeros
except ImportError:

    def zeros(shape, dtype: type = float):
        if len(shape) == 0:
            return []
        if len(shape) == 1:
            return [dtype(0) for _ in range(*shape)]
        else:
            n, *shape = shape
            return [zeros(shape, dtype=dtype) for _ in range(n)]


T_AUX = "§"


class Posiform(dict):
    """"""

    def __init__(self, d: dict = None):
        dict.__init__(
            self,
            {}
            if d is None
            else {
                (k if k is None else tuple(map(str, k))): float(v)
                for k, v in d.items()
                if (float(v) != 0.0)
            },
        )
        self.__aux = 0

    def __iter__(self):
        return iter(dict.items(self))

    def copy(self):
        return Posiform(dict.copy(self))

    def __add__(self, other):
        if type(other) is type(self) or type(other) is dict:
            posiform = self.copy()
            for k, v in other.items():
                if k in posiform:
                    u = float(posiform[k] + v)
                    if u != 0.0:
                        posiform[k] = u
                    else:
                        del posiform[k]
                elif v != 0.0:
                    posiform[k] = float(v)
            return posiform
        else:
            try:
                v = float(other)
            except:
                return NotImplemented
            else:
                posiform = self.copy()
                if None in posiform:
                    posiform[None] += v
                else:
                    posiform[None] = v
                return posiform

    def __iadd__(self, other):
        if type(other) is type(self) or type(other) is dict:
            for k, v in other.items():
                if k in self:
                    u = float(self[k] + v)
                    if u != 0.0:
                        self[k] = u
                    else:
                        del self[k]
                elif v != 0.0:
                    self[k] = float(v)
            return self
        else:
            try:
                v = float(other)
            except:
                return NotImplemented
            else:
                if None in self:
                    self[None] += v
                else:
                    self[None] = v
                return self

    def __mul__(self, other):
        if type(other) is type(self) or type(other) is dict:
            raise NotImplementedError()
        else:
            try:
                cons = float(other)
            except:
                return NotImplemented
            else:
                posiform = self.copy()
                for k, _ in posiform:
                    posiform[k] *= cons
                return posiform

    @property
    def aux(self):
        self.__aux += 1
        return f"{T_AUX}{self.__aux}"

    def reduce_degree(self, term: {tuple, None}, cons: float):
        """
        Parameters
        ----------
        term : {tuple(str), None}
            Tuple with the string variable names (or None for constant term).
        cons : float
            Multiplicative constant.

        Returns
        -------
        Posiform
        """
        if term is None or len(term) <= 2:
            return self.cls({tuple(sorted(term)): cons})
        elif len(term) >= 3:
            ## Reduction by minimum selection
            a = cons
            w = self.aux
            x, y, *z = sorted(term)

            if self.minimum_selection():  ## minimum selection
                if a < 0:
                    ## if a < 0: a (x y z) => a w (x + y + z - 2)
                    return self.cls({(x, w): a, (y, w): a, (*z, w): a, (w,): -2.0 * a})
                else:
                    ## if a > 0: a (x y z) => a (x w + y w + z w + x y + x z + y z - x - y - z - w + 1)
                    return self.cls(
                        {
                            (x, w): a,
                            (y, w): a,
                            (x, y): a,
                            (x,): -a,
                            (y,): -a,
                            (w,): -a,
                            None: a,
                        }
                    ) + (
                        self.reduce_degree((x, *z), a)
                        + self.reduce_degree((y, *z), a)
                        + self.reduce_degree((*z, w), a)
                        + self.reduce_degree((*z,), -a)
                    )
            elif self.substitution():
                alpha = 2.0  ## TODO: How can I compute alpha? (besides alpha > 1)
                return self.reduce_degree((*z, w), 1.0) + alpha * self.P(x, y, w)
            else:
                raise NotImplementedError("Not an option.")
        else:
            raise NotImplementedError(
                "Reducing any amount of terms (greater than 3) is not implemented yet."
            )  #

    def minimum_selection(self, *args) -> bool:
        return True

    def substitution(self, *args) -> bool:
        return True

    @property
    def cls(self):
        return self.__class__

    @classmethod
    def P(cls: type, x: str, y: str, w: str):
        """"""
        return cls({(x, y): 1.0, (x, w): -2.0, (y, w): -2.0, (w,): 3.0})

    def qubo(self):
        """
        Returns
        -------
        dict[str] -> int
            Mapping between variables and respective indexes.
        np.ndarray
            Symmetric Matrix representing QUBO instance.
        float
            Ground state energy.
        """
        ## Reset ancillary variable counter
        self.__aux = 0

        reduced_posiform = Posiform()

        c: float = 0.0

        for term, cons in self:
            if term is not None:
                reduced_posiform += self.reduce_degree(term, cons)
            else:
                c += float(cons)

        variables: set = set()

        for term, _ in reduced_posiform:
            variables.update(term)

        n = len(variables)
        x = {v: i for i, v in enumerate(sorted(variables))}
        Q = zeros((n, n), dtype=float)

        for term, cons in reduced_posiform:
            I = tuple(map(x.get, term))
            if len(I) == 1:
                (i,) = I
                Q[i][i] += float(cons)
            elif len(I) >= 3:
                raise ValueError("Degree reduction failed.")
            else:
                i, j = I
                Q[i][j] += float(cons)
                Q[j][i] += float(cons)

        return x, Q, c