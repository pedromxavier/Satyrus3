"""
"""

# -*- Satyrus -*-
from satyrus import SatAPI, Posiform

# Third-Party
import gurobipy as gp
from cstream import devnull

class gurobi(SatAPI):
    """"""

    def solve(self, energy: Posiform, **params: dict) -> tuple[dict, float]:
        """"""
        
        # Retrieve QUBO
        x, Q, c = energy.qubo()

        try:
            # pylint: disable=no-member
            
            # Create a new model
            model = gp.Model("MIP")

            X = model.addMVar(len(x), vtype=gp.GRB.BINARY, name="")

            model.setMObjective(Q, None, 0.0, X, X, None, sense=gp.GRB.MINIMIZE)

            with devnull:
                model.optimize()

            y = list(model.getVars())

            s = {k: int(y[i].x) for k, i in x.items()}
            e = model.objVal
        except gp.GurobiError as exc:
            self.error(f"(Gurobi code {exc.errno}) {exc}")
        else:
            return (s, e + c)
