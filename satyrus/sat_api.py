""" :: SATyrus Python API ::

    sco = {
        'int' : [...],
        'opt' : [...],
        ...
    }

    sat = Satyrus(sco)
    sat.expr()
""" 

class Satyrus:

    def __init__(self, sco):
        self.sco = sco
