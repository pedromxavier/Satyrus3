""" All tokens are defined here.
    > sys.intern avoids double storage of a single string on memory. This also
      allows O(1) comparison using ´x is y´ syntax instead of O(n) ´x == y´.
"""
from sys import intern

## Logical
T_AND = intern('&')
T_OR = intern('|')
T_XOR = intern('^')
T_NOT = intern('~')

T_IFF = intern('<->')
T_IMP = intern('->')  
T_RIMP = intern('<-')  

## Quantifiers
T_FORALL = intern('@')     # These only appear at statements,
T_EXISTS = intern('$')     # not at expressions, thus no head
T_EXISTS_ONE = intern('!$')    # is needed.

## Arithmetic
T_ADD = intern('+')
T_SUB = intern('-')
T_MUL = intern('*')
T_DIV = intern('/')

## Indexing
T_IDX = intern('[]')

## Comparison
T_GT = intern('>')
T_LT = intern('<')
T_GE = intern('>=')
T_LE = intern('<=')
T_NE = intern('!=')
T_EQ = intern('==')

## Statements
T_ASSIGN = intern('=')
T_SHARP = intern('#')
T_DOTS = intern(':')