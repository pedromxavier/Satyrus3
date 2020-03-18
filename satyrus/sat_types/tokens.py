""" All tokens are defined here.
    > sys.intern avoids double storage of a single string on memory. This also
      allows O(1) comparison using ´x is y´ syntax instead of O(n) ´x == y´.
"""
from sys import intern

T_AND = intern('&'); H_AND = (T_AND, 2)
T_OR  = intern('|'); H_OR  = (T_OR , 2)
T_XOR = intern('^'); H_XOR = (T_XOR, 2)
T_NOT = intern('~'); H_NOT = (T_NOT, 1)

T_IMP  = intern('->');  H_IMP  = (T_IMP, 2)
T_RIMP = intern('<-');  H_RIMP = (T_RIMP,2)
T_IFF  = intern('<->'); H_IFF  = (T_IFF, 2)

T_FORALL     = intern('@')     # These only appear at statements,
T_EXISTS     = intern('$')     # not at expressions, thus no head
T_EXISTS_ONE = intern('!$')    # is needed.

T_ADD = intern('+'); H_ADD = (T_ADD, 2); H_POS = (T_ADD, 1)
T_SUB = intern('-'); H_SUB = (T_SUB, 2); H_NEG = (T_SUB, 1)
T_MUL = intern('*'); H_MUL = (T_MUL, 2)
T_DIV = intern('/'); H_DIV = (T_DIV, 2)

T_IDX = intern('[]'); H_IDX = (T_IDX, 2)

T_GT = intern('>');   H_GT = (T_GT, 2)
T_LT = intern('<');   H_LT = (T_LT, 2)
T_GE = intern('>=');  H_GE = (T_GE, 2)
T_LE = intern('<=');  H_LE = (T_LE, 2)
T_NE = intern('!=');  H_NE = (T_NE, 2)
T_EQ = intern('==');  H_EQ = (T_EQ, 2)


## These are for statements
T_SHARP = intern('#'); H_CONFIG = (T_SHARP, 2)

T_DOTS = intern(':'); H_CONSTRAINT = (T_DOTS, 5)

## Assignment
T_ASSIGN = intern('='); H_CONST = (T_ASSIGN, 2); H_ARRAY = (T_ASSIGN, 3)
