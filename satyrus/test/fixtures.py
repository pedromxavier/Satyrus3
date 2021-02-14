## Third-Party
import pytest

## Local
from ..sat.types import Var, Array, Number, Constraint
from ..sat.types import Expr
from ..sat.types.indexer import SatIndexer, Default
from ..sat.compiler import SatCompiler
from ..sat.parser import SatParser
from ..sat.parser.legacy import SatLegacyParser

## Compiler
@pytest.fixture
def parsers():
    return [SatParser(), SatLegacyParser()]

@pytest.fixture
def compilers(instructions, parsers):
    return [SatCompiler(instructions, parser) for parser in parsers]



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

@pytest.fixture
def indexers():
    return [
        Default()
    ]