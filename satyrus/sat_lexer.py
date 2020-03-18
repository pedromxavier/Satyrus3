"""
"""
from ply import lex

from sat_types import Number, Var
from sat_core.stream import stdout, stderr

def regex(pattern):
    def decor(callback):
        callback.__doc__ = pattern
        return callback
    return decor

# Set of token names.   This is always required
tokens = {
    'NAME', 'NUMBER',

    'FORALL', 'EXISTS', 'EXISTS_ONE',

    'NOT', 'AND', 'OR', 'XOR',

    'IMP', 'RIMP', 'IFF',

    'SHARP',

    'ENDL',

    'COMMA',

    'ASSIGN',

    'EQ', # equal
    'GT', # greater than
    'LT', # less than

    'GE', # greater or equal
    'LE', # less or equal

    'NE', # not equal

    'MUL', 'DIV', 'ADD', 'SUB',

    'DOTS',

    'LBRA', 'RBRA', 'LPAR', 'RPAR', 'LCUR', 'RCUR',

    'STRING',
    }

# Regular expression rules for tokens
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

@regex(r'\".*\"')
def t_STRING(t):
    t.value = str(t.value[1:-1])
    return t

@regex(r"\n+")
def t_newline(t):
    t.lexer.lineno += len(t.value)

@regex(r"[a-zA-Z_][a-zA-Z0-9_']*")
def t_NAME(t):
    t.value = Var(t.value)
    return t

@regex(r"[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
def t_NUMBER(t):
    t.value = Number(t.value)
    return t

def t_error(t):
    stderr << f"SyntaxError at {t} <Lexer>"

# String containing ignored characters between tokens
t_ignore = r' \t'

t_ignore_COMMENT = r'%.*'

t_ignore_MULTICOMMENT = r'\%\{[\s\S]*?\}\%'