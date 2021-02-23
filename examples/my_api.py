#pylint: disable=undefined-variable
class myapi_1(SatAPI):

    def solve(self, posiform):
        print("Solving with myapi_1")
        return (None, 'solution_1')

class myapi_2(SatAPI):

    def solve(self, posiform):
        print("Solving with myapi_2")
        return (None, 'solution_2')