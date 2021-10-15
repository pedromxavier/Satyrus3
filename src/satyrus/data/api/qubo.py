import json

from satyrus import SatAPI, Posiform


class qubo(SatAPI):
    """"""

    ext: str = "qubo.json"

    def solve(self, energy: Posiform, indent=None, **params: dict) -> str:
        """"""
        x, Q, c = energy.qubo()

        self.check_params(indent=indent)

        return json.dumps({"x": x, "Q": [list(q) for q in Q], "c": c}, indent=indent)

    def check_params(self, **params):
        """"""
        if "indent" in params:
            if params["indent"] is None:
                return
            elif not isinstance(params["indent"], int) or (params["indent"] < 0):
                self.error("Parameter 'indent' must be a non-negative integer")