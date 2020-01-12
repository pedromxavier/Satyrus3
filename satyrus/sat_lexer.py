from sat_types import *;

from ply import lex;

tokens = [
    'NAME',
    'NUMBER',

    'FORALL',
    'EXISTS',
    'EXISTS_ONE',

    'NOT',
    'AND',
    'OR',
    'XOR',

    'IMP',
    'RIMP',
    'IFF',

    'SHARP',

    'TYPE',

    'ENDL',

    'COMMA',

    'ASSIGN',

    'EQ', # equal
    'GT', # greater than
    'LT', # less than

    'GE', # greater or equal
    'LE', # less or equal

    'NE', # not equal

    'MUL',
    'DIV',
    'ADD',
    'SUB',

    'DOTS',

    'LBRA', 'RBRA',
    'LPAR', 'RPAR',
    'LCUR', 'RCUR',

    'STRING',
]

t_DOTS = r'\:'

t_LBRA = r'\['
t_RBRA = r'\]'

t_LPAR = r'\('
t_RPAR = r'\)'

t_LCUR = r'\{'
t_RCUR = r'\}'

t_FORALL = r'\@'
t_EXISTS = r'\$'
t_EXISTS_ONE = r'\!\$'

t_NOT = r'\~'

t_AND = r'\&'

t_OR = r'\|'

t_XOR = r'\^'

t_IMP = r'\-\>'

t_RIMP = r'\<\-'

t_IFF = r'\<\-\>'

t_COMMA = r'\,'

t_DIV = r'\/'

t_MUL = r'\*'

t_ADD = r'\+'

t_SUB = r'\-'

t_ENDL = r'\;'

t_ASSIGN = r'\='

t_EQ = r'\=\='
t_GT = r'\>'
t_LT = r'\<'

t_GE = r'\>\='
t_LE = r'\<\='

t_NE = r'\!\='

t_SHARP = r'\#'

def t_STRING(t):
    r'\".*\"'
    t.value = str(t.value[1:-1])
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_NAME(t):
    r"[a-zA-Z_][a-zA-Z0-9_']*"
    t.value = Var(t.value)
    return t

def t_NUMBER(t):
    r'[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?'
    t.value = Number(t.value)
    return t

def t_error(t):
    return t_error.error(t)

t_error.error = lambda t: None;

t_ignore = " \t"

t_ignore_COMMENT = r'%.*'

t_ignore_MULTICOMMENT = r'\%\{[\s\S]*?\}\%'

lexer = lex.lex()
lexer.t_error = t_error;
