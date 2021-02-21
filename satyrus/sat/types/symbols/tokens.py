""" All tokens are defined here.
    > sys.intern avoids double storage of a single string on memory. This also
      allows O(1) comparison using ´x is y´ syntax instead of O(k) ´x == y´.
"""
from sys import intern

## Ancillary variable token
T_AUX = intern('§')

## Logical
T_AND = intern('&')
T_OR = intern('|')
T_XOR = intern('^')
T_NXR = intern('!')
T_NOT = intern('~')

T_IFF = intern('<->')
T_IMP = intern('->')  
T_RIMP = intern('<-')

## Quantifiers
T_FORALL = intern('@')      
T_EXISTS = intern('$')      
T_EXISTS_ONE = intern('$!') 

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
  T_EXISTS_ONE,
}


## Arithmetic
T_ADD = intern('+')
T_NEG = intern('-')
T_MUL = intern('*')
T_DIV = intern('/')
T_MOD = intern('%')

T_ARITHMETIC = {
  T_ADD,
  T_NEG,
  T_MUL,
  T_DIV,
  T_MOD
}

## Indexing
T_IDX = intern('[]')

T_EXTRA = {
  T_IDX
}

## Comparison
T_GT = intern('>')
T_LT = intern('<')
T_GE = intern('>=')
T_LE = intern('<=')
T_NE = intern('!=')
T_EQ = intern('==')

T_DICT = {
  'AND' : T_AND, 'RAND' : T_AND,
  'OR' : T_OR, 'ROR' : T_OR,
  'XOR' : T_XOR, 'RXOR' : T_XOR,
  'NOT' : T_NOT,

  'IFF' : T_IFF,
  'IMP' : T_IMP,
  'RIMP' : T_RIMP,

  'ADD' : T_ADD, 'RADD' : T_ADD, 'POS' : T_ADD,
  'SUB' : T_NEG, 'RSUB' : T_NEG, 'NEG' : T_NEG,
  'MUL' : T_MUL, 'RMUL' : T_MUL,
  'DIV' : T_DIV, 'RDIV' : T_DIV, 'TRUEDIV' : T_DIV, 'RTRUEDIV' : T_DIV,
  'MOD' : T_MOD, 'RMOD' : T_MOD,

  'GT' : T_GT,
  'LT' : T_LT,
  'GE' : T_GE,
  'LE' : T_LE,
  'NE' : T_NE,
  'EQ' : T_EQ,

  'IDX' : T_IDX,
}