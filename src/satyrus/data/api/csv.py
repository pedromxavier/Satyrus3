from satyrus import SatAPI, Posiform

class csv(SatAPI):
    """"""

    ext: str = "csv"

    def solve(self, posiform: Posiform, **params: dict) -> str:
        """"""
        lines = []

        for term, cons in posiform:
            if term is None:
                lines.append(f"{cons:.5f}")
            else:
                lines.append(",".join([f"{cons:.5f}", *term]))

        return "\n".join(lines)