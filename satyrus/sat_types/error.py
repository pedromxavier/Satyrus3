from ..sat_core import stderr

class SatError(Exception):
    TITLE = 'Error'
    def __init__(self, msg=None, target=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.target = target

    def launch(self):
        stderr << f"Error at line {self.target.lineno}:"
        stderr << self.target.source.lines[self.target.lineno]
        stderr << f"{' ' * self.target.chrpos}^"
        stderr << f"{self.TITLE}: {self.msg}"