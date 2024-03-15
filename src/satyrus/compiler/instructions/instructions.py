from .sys_config import sys_config
from .def_array import def_array
from .def_constant import def_constant
from .def_constraint import def_constraint
from .run_init import run_init
from .run_script import run_script
from ...symbols import SYS_CONFIG, DEF_ARRAY, DEF_CONSTANT, DEF_CONSTRAINT, RUN_SCRIPT, RUN_INIT

INSTRUCTIONS = {
    RUN_INIT: run_init,
    SYS_CONFIG: sys_config,
    DEF_ARRAY: def_array,
    DEF_CONSTANT: def_constant,
    DEF_CONSTRAINT: def_constraint,
    RUN_SCRIPT: run_script
}

__all__ = ["INSTRUCTIONS"]