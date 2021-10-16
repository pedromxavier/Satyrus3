""" All tokens are defined here.
    > sys.intern avoids double storage of a single string on memory. This also
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

## Quantifiers
T_FORALL = intern("@")
T_EXISTS = intern("$")
T_UNIQUE = intern("$!")

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


## Arithmetic
T_ADD = intern("+")
T_NEG = intern("-")
T_SUB = intern("-")
T_MUL = intern("*")
T_DIV = intern("/")
T_MOD = intern("%")
T_POW = intern("**")

T_ARITHMETIC = {T_ADD, T_NEG, T_MUL, T_DIV, T_MOD, T_POW}

## Indexing
T_IDX = intern("[]")

T_EXTRA = {T_IDX}

## Comparison
T_GT = intern(">")
T_LT = intern("<")
T_GE = intern(">=")
T_LE = intern("<=")
T_NE = intern("!=")
T_EQ = intern("==")

T_DICT = {
    "AND": T_AND,
    "RAND": T_AND,
    "OR": T_OR,
    "ROR": T_OR,
    "XOR": T_XOR,
    "RXOR": T_XOR,
    "NOT": T_NOT,
    "IFF": T_IFF,
    "IMP": T_IMP,
    "RIMP": T_RIMP,
    "ADD": T_ADD,
    "RADD": T_ADD,
    "POS": T_ADD,
    "SUB": T_NEG,
    "RSUB": T_NEG,
    "NEG": T_NEG,
    "MUL": T_MUL,
    "RMUL": T_MUL,
    "DIV": T_DIV,
    "RDIV": T_DIV,
    "TRUEDIV": T_DIV,
    "RTRUEDIV": T_DIV,
    "MOD": T_MOD,
    "RMOD": T_MOD,
    "GT": T_GT,
    "LT": T_LT,
    "GE": T_GE,
    "LE": T_LE,
    "NE": T_NE,
    "EQ": T_EQ,
    "IDX": T_IDX,
}

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
MAPPING = intern("mapping")
INDEXER = intern("indexer")

## Constraint Types
CONS_INT = intern("int")
CONS_OPT = intern("opt")
