""" All tokens are defined here.
    
    sys.intern avoids double storage of a single string on memory. This also
    allows O(1) comparison using ´x is y´ syntax instead of O(k) ´x == y´.
"""
from sys import intern

## Ancillary variable token
T_AUX = intern("$")

## Extra Indexing variable token
T_ACC = intern(":")

## Logical
T_AND = intern("&")
T_OR = intern("|")
T_XOR = intern("^")
T_NXR = intern("!")
T_NOT = intern("~")

T_IFF = intern("<->")
T_IMP = intern("->")
T_RIMP = intern("<-")

## Quantifiers & Loops
T_LOOP = intern("LOOP")
T_FORALL = intern("FORALL")
T_EXISTS = intern("EXISTS")
T_UNIQUE = intern("UNIQUE")

T_LOGICAL = {
    T_AND,
    T_OR,
    T_XOR,
    T_NOT,
    T_IFF,
    T_IMP,
    T_RIMP,
    ## Quantifiers
    T_FORALL,
    T_EXISTS,
    T_UNIQUE,
}

# Arithmetic
T_ADD = intern("+")
T_NEG = intern("-")
T_SUB = intern("-")
T_MUL = intern("*")
T_DIV = intern("/")
T_MOD = intern("%")
T_POW = intern("**")

T_ARITHMETIC = {T_ADD, T_NEG, T_MUL, T_DIV, T_MOD, T_POW}

# Indexing
T_IDX = intern("[]")

T_EXTRA = {T_IDX, T_LOOP}

## Comparison
T_GT = intern(">")
T_LT = intern("<")
T_GE = intern(">=")
T_LE = intern("<=")
T_NE = intern("!=")
T_EQ = intern("==")

## Statements
RUN_INIT = intern("RUN_INIT")
CMD_INIT = (RUN_INIT,)
SYS_CONFIG = intern("SYS_CONFIG")
DEF_CONSTANT = intern("DEF_CONSTANT")
DEF_ARRAY = intern("DEF_ARRAY")
DEF_CONSTRAINT = intern("DEF_CONSTRAINT")
CMD_PYTHON = intern("CMD_PYTHON")
RUN_SCRIPT = intern("RUN_SCRIPT")
CMD_SCRIPT = (RUN_SCRIPT,)

## Sys config options
## To be used in `compiler.env` dict as keys.
DIR = intern("dir")
OUT = intern("out")
OPT = intern("opt")
PREC = intern("prec")
LOAD = intern("load")
EXIT = intern("exit")
ALPHA = intern("alpha")
EPSILON = intern("epsilon")

## Constraint Types
CONS_INT = intern("int")
CONS_OPT = intern("opt")