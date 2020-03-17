"""
SATyrus Python API
"""
from sat_types import Loop

class Sat:
    @staticmethod
    def forall(var, start, stop, step=1, conditions=None):
        conditions = conditions if conditions is not None else []
        return Loop('@', var, start, stop, step, conditions) 

    @staticmethod
    def exists(var, start, stop, step=1, conditions=None):
        conditions = conditions if conditions is not None else []
        return Loop('$', var, start, stop, step, conditions)	

    @staticmethod
    def exists_one(var, start, stop, step=1, conditions=None):
        conditions = conditions if conditions is not None else []
        return Loop('$!', var, start, stop, step, conditions)

    @staticmethod
    def execute(sco):
        return sco


        
