import sys

class qubo(object):

    T_AUX = sys.intern("§")

    def __init__(self):
        self.__aux: int = 0

    @property
    def aux(self) -> str:
        self.__aux += 1
        return f"{self.T_AUX}{self.__aux}"

    def reduce_degree(self, term: tuple, cons: float) -> dict:
        """
        :param term:
        :type term: tuple
        :param cons:
        :type cons: Number
        :returns:
        :rtype: dict
        """
        if len(term) <= 2:
            return {term: cons}
        elif len(term) == 3:
            ## Reduction by minimum selection
            if a < 0:
                a = cons
                w = self.aux
                x, y, z = term
                return {(x, w): a, (y, w): a, (z, w): a, (w,): -2.0 * a}
            else:
                return {
                    (x, w): a, (y, w): a, (z, w): a,
                    (x, y): a, (y, z): a, (x, z): a,
                    (x,): -a, (y,): -a, (z,): -a, (w,): -a,
                    None : a
                    }

            ## Reduction by substitution ?
        else:
            raise NotImplementedError("Reducing any amount of terms (greater than 3) is not implemented yet.") # 

    def solve(self, posiform: dict) -> (dict, list, float):
        """
        :param posiform:
        :type posiform: dict
        :returns: 
        :rtype: (dict, np.ndarray, float)
        """
        import numpy as np

        reduced_posiform: dict = {}

        for term, cons in posiform.items():
            if term is not None:
                reduced_posiform.update(self.reduce_degree(term, cons))
            else:
                c = float(cons)

        reduced_posiform: dict = {k: v for k, v in reduced_posiform.items() if v != 0.0}

        variables: set = set()
        for term in reduced_posiform:
            variables.update(term)
        
        n = len(variables)
        x = {v: i for i, v in enumerate(sorted(variables))}
        Q = np.zeros((n, n), dtype=float)

        for term, cons in reduced_posiform.items():
            I = tuple(map(x.get, term))
            if len(I) == 1:
                i, = I
                Q[i, i] += float(cons)
            elif len(I) >= 3:
                raise ValueError('Degree reduction failed.')
            else:
                i, j = I
                Q[i, j] += float(cons)
                Q[j, i] += float(cons)
        return x, Q, c