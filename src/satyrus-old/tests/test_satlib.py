# Future Imports
from __future__ import annotations

# Standard Library
import json

# Third-Party
import numpy as np
import pytest

# Local
from ..satlib import Posiform


class TestPosiform:
    @pytest.fixture
    def fix_init(self) -> list[tuple[Posiform | float, Exception | None]]:
        return [
            (0.0, None),
            (1.0, None),
            ({None: 0.0}, None),
            ({None: 2j}, TypeError),
            ({(1, 2): 1}, TypeError),
            ("string", TypeError),
        ]

    @pytest.fixture
    def fix_str(self) -> list[tuple[Posiform, str]]:
        return [
            (Posiform(), "0.0"),
            (Posiform({("x", "y"): 1.0, ("x", "z"): 2.0, None: 1.0}), "x * y + 2.0 * x * z + 1.0"),
            (Posiform({("x", "y"): -1.0, ("x", "z"): -2.0, None: -1.0}), "- x * y - 2.0 * x * z - 1.0"),
        ]

    @pytest.fixture
    def fix_repr(self) -> list[tuple[Posiform, str]]:
        return [(Posiform(), r"Posiform({})"), (Posiform({frozenset({"x", "y"}): 2.0, None: -3.0}), "Posiform({('x', 'y'): 2.0, None: -3.0})")]

    @pytest.fixture
    def fix_bool(self) -> list[tuple[Posiform]]:
        return [(Posiform({("x", "y"): 1.0, ("x", "z"): 2.0}), True), (Posiform(0.0), False)]

    @pytest.fixture
    def fix_add(self) -> list[tuple[Posiform]]:
        return [
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): 2.0}), None),
            (Posiform({("x", "y"): 1.0}), 3.0, Posiform({("x", "y"): 1.0, None: 3.0}), None),
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): -1.0}), Posiform({}), None),
            (Posiform({}), Posiform({("x", "y"): -1.0}), Posiform({("x", "y"): -1.0}), None),
            (Posiform({("x", "y"): 1.0, None: 1.0}), 3.0, Posiform({("x", "y"): 1.0, None: 4.0}), None),
            (Posiform({("x", "y"): 1.0, None: 1.0}), 3j, None, TypeError),
            (Posiform({("x", "y"): 1.0, None: 1.0}), {"x": 3.0}, None, TypeError),
        ]

    @pytest.fixture
    def fix_sub(self) -> list[Posiform]:
        return [
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): 1.0}), Posiform({}), None),
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "z"): 1.0}), Posiform({("x", "y"): 1.0, ("x", "z"): -1.0}), None),
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): 0.5}), Posiform({("x", "y"): 0.5}), None),
            (Posiform({("x", "y"): 1.0}), 1.0, Posiform({("x", "y"): 1.0, None: -1.0}), None),
            (Posiform({("x", "y"): 1.0}), 3.0, Posiform({("x", "y"): 1.0, None: -3.0}), None),
            (3.0, Posiform(1.0), Posiform(2.0), None),
            (Posiform({("x", "y"): 1.0, None: 1.0}), 3j, None, TypeError),
            (Posiform({("x", "y"): 1.0, None: 1.0}), {"x": 3.0}, None, TypeError),
        ]

    @pytest.fixture
    def fix_neg(self) -> list[Posiform]:
        return [
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): -1.0})),
            (Posiform({("x", "y"): 1.0, None: 3.0}), Posiform({("x", "y"): -1.0, None: -3.0})),
            (Posiform(3.0), Posiform(-3.0)),
        ]

    @pytest.fixture
    def fix_mul(self) -> list[Posiform]:
        return [
            (Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): 1.0}), Posiform({("x", "y"): 1.0}), None),
            (Posiform({("x", "y"): 1.0}), Posiform({("y", "z"): 1.0}), Posiform({("x", "y", "z"): 1.0}), None),
            (Posiform({("x", "y"): 1.0}), 3.0, Posiform({("x", "y"): 3.0}), None),
            (Posiform({("x", "y"): 1.0, None: 3.0}), 3.0, Posiform({("x", "y"): 3.0, None: 9.0}), None),
            (Posiform({("x", "y"): 1.0, None: 3.0}), Posiform({("x", "y"): 1.0, None: 3.0}), Posiform({("x", "y"): 7.0, None: 9.0}), None),
            (Posiform({("x", "y"): 1.0, None: 1.0}), 3j, None, TypeError),
            (Posiform({("x", "y"): 1.0, None: 1.0}), {"x": 3.0}, None, TypeError),
            (Posiform({("x", "y"): 1.0, None: 1.0}), 0.0, Posiform({}), None),
            (Posiform({("x", "y"): 1.0, ("y", "z"): 1.0}), Posiform({("x", "z"): -1.0, ("y", "w"): -2.0}), Posiform({("x", "y", "z"): -2.0, ("x", "y", "w"): -2.0, ("z", "y", "w"): -2.0}), None),
            (Posiform({("x", "y"): 1.0, ("x",): -1.0}), Posiform({("y",): -1.0}), Posiform({}), None),
        ]

    @pytest.fixture
    def fix_div(self) -> list[Posiform]:
        return [
            (Posiform({("x", "y"): 3.0}), 0.0, None, ZeroDivisionError),
            (Posiform({("x", "y"): 3.0}), "string", None, TypeError),
            (Posiform({("x", "y"): 3.0}), 3.0, Posiform({("x", "y"): 1.0}), None),
            (Posiform({("x", "y"): 2.0, None: -2.0}), 2.0, Posiform({("x", "y"): 1.0, None: -1.0}), None),
        ]

    @pytest.fixture
    def fix_call(self) -> list[tuple[Posiform, dict, Posiform]]:
        return [
            (Posiform({("x", "y"): 1.0, ("z", "w"): -1.0}), {"x": 2.0, "w": 3.0}, Posiform({("y",): 2.0, ("z",): -3.0}), None),
            (Posiform({("x", "y"): 1.0, ("z", "w"): -1.0}), 5.0, None, TypeError),
            (Posiform({("x", "y"): 1.0, ("z", "w"): -1.0}), {5: 1.0}, None, TypeError),
            (Posiform({("x", "y"): 1.0, ("z", "w"): -1.0}), {"x": 1j}, None, TypeError),
            (Posiform({("x", "y"): 1.0, ("z", "w"): -1.0}), {"x": "u", "w": 3.0}, Posiform({("u", "y",): 1.0, ("z",): -3.0}), None),
            (Posiform({("x", "y"): 1.0, None: -1.0}), {"x": 2.0, "w": 3.0}, Posiform({("y",): 2.0, None: -1.0}), None),
            (Posiform({("x",): 1.0, None: -1.0}), {"x": 2.0}, Posiform({None: 1.0}), None),
            (Posiform({("x",): 1.0, None: -1.0}), {"y": 2.0}, Posiform({("x",): 1.0, None: -1.0}), None),
            (Posiform({("x",): 1.0, ("y",): 1.0, None: -1.0}), {"x": 2.0, "y": 3.0}, Posiform({None: 4.0}), None),
            (Posiform({("x", "w"): 1.0, ("y", "w"): 1.0, None: -1.0}), {"x": 2.0, "y": 3.0}, Posiform({("w",): 5.0, None: -1.0}), None),
        ]

    @pytest.fixture
    def fix_qubo(self) -> list:
        return [(Posiform({("x", "y", "z"): 1.0}), {"$1": 0, "x": 1, "y": 2, "z": 3}, np.array([[-1, 1, 1, 1], [1, -1, 1, 1], [1, 1, -1, 1], [1, 1, 1, -1]], dtype=float), 1.0)]

    @pytest.fixture
    def fix_json(self) -> list:
        return [
            (r'[{"term": ["x", "y"], "cons": 1.0}]', Posiform({("x", "y"): 1.0}), r'[{"term": ["x", "y"], "cons": 1.0}]', None),
            (r'[{"term": ["x", "y"], "cons": 1.0}, {"term": ["x", "y"], "cons": 3.0}]', Posiform({("x", "y"): 4.0}), r'[{"term": ["x", "y"], "cons": 4.0}]', None),
            (r'[[{"term": ["x", "y"], "cons": 3.0}]]', None, r'[[{"term": ["x", "y"], "cons": 3.0}]]', json.decoder.JSONDecodeError),
            (r'[{"term": ["x", "y"], "tons": 3.0}]', None, r'[{"term": ["x", "y"], "tons": 3.0}]', json.decoder.JSONDecodeError),
            (r'[{"term": 2.0, "cons": 3.0}]', None, r'[{"term": 2.0, "cons": 3.0}]', json.decoder.JSONDecodeError),
            (r'[{"term": ["x", 3.0], "cons": 3.0}]', None, r'[{"term": ["x", 3.0], "cons": 3.0}]', json.decoder.JSONDecodeError),
            (r'[{"term": ["x", "y"], "cons": "3.0"}]', None, r'[{"term": ["x", "y"], "cons": "3.0"}]', json.decoder.JSONDecodeError),
            (r'{"term": ["x", "y"], "cons": "3.0"}', None, r'{"term": ["x", "y"], "cons": "3.0"}', json.decoder.JSONDecodeError),
        ]

    @pytest.fixture
    def fix_json_indent(self) -> list:
        return [
            (r'[{"term": ["x", "y"], "cons": 1.0}]', Posiform({("x", "y"): 1.0}), '[\n{\n"term": [\n"x",\n"y"\n],\n"cons": 1.0\n}\n]', None),
            (r'[{"term": ["x", "y"], "cons": 1.0}, {"term": ["x", "y"], "cons": 3.0}]', Posiform({("x", "y"): 4.0}), '[\n{\n"term": [\n"x",\n"y"\n],\n"cons": 4.0\n}\n]', None),
            (r'[[{"term": ["x", "y"], "cons": 3.0}]]', None, r'[[{"term": ["x", "y"], "cons": 3.0}]]', json.decoder.JSONDecodeError),
            (r'[{"term": ["x", "y"], "tons": 3.0}]', None, r'[{"term": ["x", "y"], "tons": 3.0}]', json.decoder.JSONDecodeError),
            (r'[{"term": 2.0, "cons": 3.0}]', None, r'[{"term": 2.0, "cons": 3.0}]', json.decoder.JSONDecodeError),
            (r'[{"term": ["x", 3.0], "cons": 3.0}]', None, r'[{"term": ["x", 3.0], "cons": 3.0}]', json.decoder.JSONDecodeError),
            (r'[{"term": ["x", "y"], "cons": "3.0"}]', None, r'[{"term": ["x", "y"], "cons": "3.0"}]', json.decoder.JSONDecodeError),
            (r'{"term": ["x", "y"], "cons": "3.0"}', None, r'{"term": ["x", "y"], "cons": "3.0"}', json.decoder.JSONDecodeError),
        ]

    @pytest.fixture
    def fix_mini_json(self) -> list:
        return [
            (r'{"x y": 1.0}', Posiform({("x", "y"): 1.0}), r'{"x y": 1.0}', None),
            (r'{"x y": 1.0, "x z": 3.0}', Posiform({("x", "y"): 1.0, ("x", "z"): 3.0}), r'{"x y": 1.0, "x z": 3.0}', None),
            (r'[{"x y": 3.0}]', None, None, json.decoder.JSONDecodeError),
            (r'{"x": [1.0]}', None, None, json.decoder.JSONDecodeError),
            (r'{"x y": 3.0, "y x": -2.0}', Posiform({("x", "y"): 1.0}), r'{"x y": 1.0}', None),
            (r'{"x y": 3.0, "": -2.0}', Posiform({("x", "y"): 3.0, None: -2.0}), r'{"x y": 3.0, "": -2.0}', None),
        ]

    def test_json(self, fix_json):
        for s, t, r, exc in fix_json:
            if exc is None:
                assert Posiform.fromJSON(s) == t
                assert r == t.toJSON()
            else:
                with pytest.raises(exc):
                    assert Posiform.fromJSON(s) == t
                    assert r == t.toJSON()

    def test_mini_json(self, fix_mini_json):
        for s, t, r, exc in fix_mini_json:
            if exc is None:
                assert Posiform.fromMiniJSON(s) == t
                assert r == t.toMiniJSON()
            else:
                with pytest.raises(exc):
                    assert Posiform.fromMiniJSON(s) == t
                    assert r == t.toMiniJSON()
    
    def test_json_indent(self, fix_json_indent):
        for s, t, r, exc in fix_json_indent:
            if exc is None:
                assert Posiform.fromJSON(s) == t
                assert r == t.toJSON(indent=0)
            else:
                with pytest.raises(exc):
                    assert Posiform.fromJSON(s) == t
                    assert r == t.toJSON(indent=0)

    def test_call(self, fix_call):
        for p, x, q, exc in fix_call:
            if exc is None:
                assert p(x) == q
            else:
                with pytest.raises(exc):
                    assert p(x) == q

    # -*- Tests -*-
    def test_init(self, fix_init):
        for a, exc in fix_init:
            if exc is None:
                assert isinstance(Posiform(a), Posiform)
            else:
                with pytest.raises(exc):
                    assert isinstance(Posiform(a), Posiform)

    def test_bool(self, fix_bool):
        for a, b in fix_bool:
            assert bool(a) == b

    def test_str(self, fix_str):
        for a, b in fix_str:
            assert str(a) == b

    def test_repr(self, fix_repr):
        for a, b in fix_repr:
            assert repr(a) == b

    def test_add(self, fix_add):
        for a, b, c, exc in fix_add:
            if exc is None:
                assert (a + b) == c
            else:
                with pytest.raises(exc):
                    assert (a + b) == c

    def test_sub(self, fix_sub):
        for a, b, c, exc in fix_sub:
            if exc is None:
                assert (a - b) == c
            else:
                with pytest.raises(exc):
                    assert (a - b) == c

    def test_neg(self, fix_neg):
        for a, b in fix_neg:
            assert (-a) == b

    def test_mul(self, fix_mul):
        for a, b, c, exc in fix_mul:
            if exc is None:
                assert (a * b) == c
            else:
                with pytest.raises(exc):
                    assert (a * b) == c

    def test_div(self, fix_div):
        for a, b, c, exc in fix_div:
            if exc is None:
                assert (a / b) == c
            else:
                with pytest.raises(exc):
                    assert (a / b) == c

    def test_qubo(self, fix_qubo):
        for p, t_x, t_Q, t_c in fix_qubo:
            x, Q, c = p.qubo()
            assert x == t_x
            assert np.all(Q == t_Q)
            assert c == t_c
