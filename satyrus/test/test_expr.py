## Third-Party
import pytest

## Local
from ..sat.types import Var, Array, Number
from ..sat.types.expr import Expr


## Fixtures
@pytest.fixture
def arrays():
    return [
        Array(Var('X'), (Number('4'),)),
        Array(Var('Y'), (Number('4'), Number('4'))),
    ]

@pytest.fixture
def expressions(arrays):
    return [
        ~Expr('->', Var('a'), Var('b')), ## ~(a -> b)
        ~Expr('->', Expr('~', Var('a')), Var('b')), ## ~(~a -> b)
        ~Expr('<-', Var('a'), Expr('~', Var('b'))), ## ~(a <- ~b)
    ] + [
        Expr('->', Expr('~', Expr('[]', arrays[0], Var('k'))), Expr('~', Expr('[]', arrays[1], Var('i'), Var('k'))))
    ]

@pytest.fixture
def cnf_expressions(arrays):
    return [
        Expr('&', Var('a'), Expr('~', Var('b'))), ## a & ~b
        Expr('&', Var('a'), Var('b')), ## ~a & ~b
        Expr('&', Var('a'), Var('b')), ## ~a | ~b
    ] + [
        Expr('|', 
            Expr('[]', arrays[0], Var('k')),
            Expr('~', Expr('[]', arrays[1], Var('i'), Var('k')))
            )
    ]

## Tests
# def test_comparison(expressions):
#     assert Expr.cmp()

def test_cnf(expressions: list, cnf_expressions: list):
    for expr, cnf_expr in zip(expressions, cnf_expressions):
        assert Expr.cmp(Expr.cnf(expr), cnf_expr) #pylint: disable=no-member

    
        
