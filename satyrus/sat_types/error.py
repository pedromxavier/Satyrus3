from ..sat_core import stderr

class SatError(Exception):
    TITLE = 'Error'
    def __init__(self, msg=None, target=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.target = target

    def launch(self):
        if self.target is not None:
            stderr << f"""Error at line {self.target.lineno}:
            {self.target.source.lines[self.target.lineno]}
            {' ' * self.target.chrpos}^
            {self.TITLE}: {self.msg}"""
        else:
            raise self