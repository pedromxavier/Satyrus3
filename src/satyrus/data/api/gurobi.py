import gurobipy as gp
from satyrus import SatAPI, Posiform
from cstream import devnull

class gurobi(SatAPI):
    """"""

    def solve(self, energy: Posiform, **params: dict) -> tuple[dict, float]:
        """"""
        
        # Retrieve QUBO
        x, Q, c = energy.qubo()

        # Create a new model
        model = gp.Model("MIP")

        X = model.addMVar(len(x), vtype=gp.GRB.BINARY, name="")

        model.setMObjective(Q, None, 0.0, X, X, None, sense=gp.GRB.MINIMIZE)

        try:
            with devnull:
                model.optimize()

            y = list(model.getVars())

            s = {k: int(y[i].x) for k, i in x.items()}
            e = model.objVal

            return (s, e + c)
        except gp.GurobiError as error:
            self.error(f"(Gurobi code {error.errno}) {error}")
