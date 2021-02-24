#pylint: disable=undefined-variable
class myapi1(SatAPI):

    def solve(self, posiform):
        print("Solving with myapi1")
        return (None, 'solution1')

class myapi2(SatAPI):

    def solve(self, posiform):
        print("Solving with myapi2")
        return (None, 'solution2')