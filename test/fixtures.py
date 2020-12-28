import pytest
import random

## Test expr
from satyrus.sat.types.symbols import T_LOGICAL
from satyrus.sat.types import Expr

def _logical_token():
    return

def _logical_expr(expr=None, depth=1):
    if expr is None:
        return 

    if depth <= 0:
        return Expr(token)