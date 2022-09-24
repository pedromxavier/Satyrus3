def type_error(msg: str = ""):
    raise TypeError(msg)

def value_error(msg: str = ""):
    raise ValueError(msg)

class PBF(dict):
    """"""

    @staticmethod
    def parse_data(data: dict) -> dict:
        if data is None:
            return {}
        elif isinstance(data, dict):
            return data
        else:
            type_error(f"Invalid type: {type(data)}")

    @staticmethod
    def parse_key(key: object) -> frozenset:
        if key is None:
            return frozenset()
        elif isinstance(key, str):
            return frozenset([key])
        elif isinstance(key, (frozenset, set, list, tuple)):
            return frozenset(
                [
                    x if isinstance(x, str) else type_error("Varibles must be strings")
                    for x in key
                ]
            )
        else:
            type_error("Invalid key type")

    def parse_point(self, __point: object):
        if isinstance(__point, dict):
            point = set()
            for var in self.__vars__:
                if var in __point and __point[var]:
                    point.add(var)
            return frozenset(point)
        elif isinstance(__point, (tuple, list, set, frozenset)):
            return frozenset(__point)
        else:
            type_error("Can't parse point")

    def deepcopy(self):
        """Deep PBF copy."""
        return PBF({k: v for k, v in self})

    def isscalar(self):
        """ """
        return len(self) == 0 or (len(self) == 1 and None in self)

    def __incref(self, key: frozenset):
        if key in self:
            return

        for var in key:
            if var in self.__vars__:
                self.__vars__[var] += 1
            else:
                self.__vars__[var] = 1

    def __decref(self, key: frozenset):
        if key not in self:
            return 

        for var in key:
            if var in self.__vars__:
                self.__vars__[var] -= 1
            else:
                value_error("Invalid decref")

            if self.__vars__[var] == 0:
                del self.__vars__[var]

    def __init__(self, data: dict = None):
        dict.__init__(self, self.parse_data(data))
        self.__vars__ = {}

    def __contains__(self, key) -> bool:
        return dict.__contains__(self, self.parse_key(key))

    def __getitem__(self, key: frozenset) -> float:
        if key in self:
            return dict.__getitem__(self, self.parse_key(key))
        else:
            return 0.0

    def __setitem__(self, __key: frozenset, value: float) -> None:
        key = self.parse_key(__key)

        if value == 0.0:
            self.__delitem__(key)
        else:
            self.__incref(key)
            dict.__setitem__(self, key, float(value))
            

    def __delitem__(self, __key: frozenset) -> None:
        key = self.parse_key(__key)
        self.__decref(key)
        dict.__delitem__(self, key)
        

    def __iter__(self):
        return iter(dict.items(self))

    def __bool__(self) -> bool:
        return len(self) > 0

    def __float__(self) -> float:
        if self.isscalar():
            return self[None]
        else:
            type_error("Can't cast 'PBF' to 'float' due to non-constant terms")

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

    def __call__(self, __point: object):
        """"""
        n = self.parse_point(__point)

        f = PBF()
        for w, c in self:
            if w <= n:
                f[w - n] += c
        return f

f = PBF()
f[None] = 3.0
f["x"] = 1.2
f[("x", "y")] = -5.0
