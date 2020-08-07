
## Number
def import_number_module():
    global Number

    try:
        from satyrus.types import Number as _Number
        assert True
    except ImportError:
        Number = None
        assert False
    finally:
        Number = _Number


