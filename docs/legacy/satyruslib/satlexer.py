#!/usr/bin/python

import re,sys
from satexceptions import SATLexerError

# SATyrus's keywords
keywords = [
  'and', 'correlation', 'exists', 'forall', 'from', 'in', 'intgroup', 'level', 
  'not', 'optgroup', 'or', 'penalties', 'where'
]

# Tokens are keywords plus some other code entities, such as identifies, 
# strings, etc
tokens = [ w.upper() for w in keywords ] + [ 
  'EQ', 'EQV', 'IDENT', 'INTEGER', 'LI', 'NOTEQ', 'RI', 'STRING', 
  'LT', 'LE', 'GT', 'GE' 
]

# One character tokens. They are identified by the regular expression 
# that defines them. So, '=' defines the '=' token, '+' defines the '+' token,
# and so on
literals = ['=','+','-','*','/',',',';',':','(',')','[',']','{','}']

# Each one of this regular expressions match one of the tokens specified above
# in the 'tokens' list (except for keywords)
t_EQ    = r'=='
t_NOTEQ = r'\!='
t_LT    = r'<'
t_LE    = r'<='
t_GT    = r'>'
t_GE    = r'>='
t_LI    = r'->'     
t_RI    = r'<-'
t_EQV   = r'<->'

def t_INTEGER(t):
  r'\d+'
  t.value = int(t.value)
  return t

def t_IDENT(t):
  # Identifiers must begin with a letter or a underscore. After the first
  # character, digits are also allowed.
  r'[a-zA-Z_][a-zA-Z_0-9]*'

  # Check for keywords. If a lexeme matches an entry in the keywords list,
  # a t_LEXEME is generated. Otherwise, a t_ID is generated.
  if t.value in keywords:
    t.type = t.value.upper()
  return t

def t_STRING(t):
  # A string is a sequence of characters embraced in double quotes
  r'\"([^\\"]+|\\"|\\\\)*\"'
  t.value = t.value[1:-1] # removing quotes # XXX: decode("string-escape")?
  return t

# Whitespaces and tabs are ignored
t_ignore = ' \t'

# Counting newlines
def t_NEWLINE(t):
  r'\n'
  t.lexer.lineno += 1

# Single line comments start with a #
t_ignore_SINGLE_LINE_COMMENT = r'//.*'

# Multi line comments are enclosed by /* */
def t_MULTI_LINE_COMMENT(t):
  r'/\*(.|\n)*?\*/'
  t.lexer.lineno += t.value.count('\n')

def get_column(input, token):
  i = token.lexpos
  while i > 0:
    if input[i] == '\n': break
    i -= 1
  column = token.lexpos - i
  return column

# Error handling rule
def t_error(t):
  raise SATLexerError(t. lineno, "illegal character '%s'" % t.value[0])
  #t.lexer.skip(1)

# Testing the lexer
if __name__ == "__main__":
  from ply import lex
  lexer = lex.lex()
  data = sys.stdin.read()
  lexer.input(data)
  while 1:
    tok = lexer.token()
    if not tok: break
    print tok
