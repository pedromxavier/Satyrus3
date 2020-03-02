from satypes import *;

from sly import Lexer;

class SatLexer(Lexer):
    ## regex tokens
    regex = _

    # Set of token names.   This is always required
    tokens = {
        NAME, NUMBER,

        FORALL, EXISTS, EXISTS_ONE,

        NOT, AND, OR, XOR,

        IMP, RIMP, IFF,

        SHARP,

        ENDL,

        COMMA,

        ASSIGN,

        EQ, # equal
        GT, # greater than
        LT, # less than

        GE, # greater or equal
        LE, # less or equal

        NE, # not equal

        MUL, DIV, ADD, SUB,

        DOTS,

        LBRA, RBRA, LPAR, RPAR, LCUR, RCUR,

        STRING,
        }

    # String containing ignored characters between tokens
    ignore = ' \t'

    # Regular expression rules for tokens
    DOTS = r'\:'

    LBRA = r'\['
    RBRA = r'\]'

    LPAR = r'\('
    RPAR = r'\)'

    LCUR = r'\{'
    RCUR = r'\}'

    FORALL = r'\@'
    EXISTS = r'\$'
    EXISTS_ONE = r'\!\$'

    NOT = r'\~'

    AND = r'\&'

    OR = r'\|'

    XOR = r'\^'

    IMP = r'\-\>'

    RIMP = r'\<\-'

    IFF = r'\<\-\>'

    COMMA = r'\,'

    DIV = r'\/'

    MUL = r'\*'

    ADD = r'\+'

    SUB = r'\-'

    ENDL = r'\;'

    ASSIGN = r'\='

    EQ = r'\=\='
    GT = r'\>'
    LT = r'\<'

    GE = r'\>\='
    LE = r'\<\='

    NE = r'\!\='

    SHARP = r'\#'

    @regex(r'\".*\"')
    def STRING(t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r"\n+")
    def NEWLINE(t):
        t.lexer.lineno += len(t.value)

    @regex(r"[a-zA-Z_][a-zA-Z0-9_']*")
    def NAME(t):
        t.value = Var(t.value)
        return t

    @regexr(r"[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
    def NUMBER(t):
        t.value = Number(t.value)
        return t

    def error(t):
        stderr << f"SyntaxError at {t} <Lexer>"

    ignore = r' \t'
    
    ignore_COMMENT = r'%.*'

    ignore_MULTICOMMENT = r'\%\{[\s\S]*?\}\%'
