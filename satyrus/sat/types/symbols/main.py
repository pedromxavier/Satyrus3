from sys import intern

## Statements
RUN_INIT = intern('RUN_INIT')
SYS_CONFIG = intern('SYS_CONFIG')
DEF_CONSTANT  = intern('DEF_CONSTANT')
DEF_ARRAY = intern('DEF_ARRAY')
DEF_CONSTRAINT = intern('DEF_CONSTRAINT')
CMD_PYTHON = intern('CMD_PYTHON')
RUN_SCRIPT = intern('RUN_SCRIPT')

## Sys config options
## To be used in `compiler.env` dict as keys.
DIR = intern('dir')
OUT = intern('out')
OPT = intern('opt')
PREC = intern('prec')
LOAD = intern('load')
EXIT = intern('exit')
ALPHA = intern('alpha')
EPSILON = intern('epsilon')
MAPPING = intern('mapping')
INDEXER = intern('indexer')

## Constraint Types
CONS_INT = intern('int')
CONS_OPT = intern('opt')