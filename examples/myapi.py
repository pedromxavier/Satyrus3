# Future Imports
from __future__ import annotations

from satyrus import SatAPI, Posiform

class MyPartialAPI(SatAPI):

    def solve(self, posiform: Posiform) -> str:
        return "My Solution"

class MyCompleteAPI(SatAPI):
    
    def solve(self, posiform: Posiform) -> tuple[dict, float]:
        x = {'x': 0, 'y': 1, 'z': 0}
        e = 2.0
        return (x, e)