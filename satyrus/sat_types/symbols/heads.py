from .tokens import T_AND, T_OR, T_XOR, T_NOT, T_IFF, T_IMP, T_RIMP
# Logical
H_AND = (T_AND, None)
H_OR  = (T_OR , None)
H_XOR = (T_XOR, 2)
H_NOT = (T_NOT, 1)
H_IFF = (T_IFF, 2)
H_IMP = (T_IMP, 2)
H_RIMP = (T_RIMP,2)

from .tokens import T_ADD, T_SUB, T_MUL, T_DIV
# Aritmetic
H_ADD = (T_ADD, None)
H_POS = (T_ADD, 1)
H_SUB = (T_SUB, 2)
H_NEG = (T_SUB, 1)
H_MUL = (T_MUL, None)
H_DIV = (T_DIV, 2)

from .tokens import T_GT, T_LT, T_GE, T_LE, T_NE, T_EQ
# Comparisons
H_GT = (T_GT, 2)
H_LT = (T_LT, 2)
H_GE = (T_GE, 2)
H_LE = (T_LE, 2)
H_NE = (T_NE, 2)
H_EQ = (T_EQ, 2)

from .tokens import T_IDX
# Indexing
H_IDX = (T_IDX, 2)