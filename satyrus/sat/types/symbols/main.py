from sys import intern

## Statements
RUN_INIT = intern('RUN_INIT')
SYS_CONFIG = intern('SYS_CONFIG')
DEF_CONSTANT  = intern('DEF_CONSTANT')
DEF_ARRAY = intern('DEF_ARRAY')
DEF_CONSTRAINT = intern('DEF_CONSTRAINT')
RUN_SCRIPT = intern('RUN_SCRIPT')

## Sys config options
PREC = intern('prec')
DIR = intern('dir')
LOAD = intern('load')
OUT = intern('out')
EPSILON = intern('epsilon')
ALPHA = intern('alpha')
EXIT = intern('exit')

## Constraint Types
CONS_INT = intern('int')
CONS_OPT = intern('opt')