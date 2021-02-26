#pylint: disable=undefined-variable
class MyPartialAPI(SatAPI):

    def _solve(self, posiform: Posiform) -> {(dict, float), object}:
        return "My Solution"

class MyCompleteAPI(SatAPI):
    
    def _solve(self, posiform: Posiform) -> {(dict[str: int], float), object}:
        x = {'x': 0, 'y': 1, 'z': 0}
        e = 2.0
        return (x, e)