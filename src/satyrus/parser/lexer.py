# Third-Party
from ply import lex
from cstream import stderr

# Local
from ..error import *

def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback

    return decor

class SATLexer(object):
    """ """
    tokens = (
        # quantifiers
        "FORALL",
        "EXISTS",
        "UNIQUE",
        # logical
        "NOT",
        "AND",
        "OR",
        "XOR",
        # extended logical
        "IMP",
        "RIMP",
        "IFF",
        # punctuation
        "CONFIG",
        "ENDL",
        "COMMA",
        "ASSIGN",
        # comparison
        "EQ",
        "GT",
        "LT",
        "GE",
        "LE",
        "NE",
        # arithmetic
        "MUL",
        "DIV",
        "MOD",
        "ADD",
        "SUB",
        "POW",
        # more punctuation
        "DOTS",
        "LBRA",
        "RBRA",
        "LPAR",
        "RPAR",
        "LCUR",
        "RCUR",
        # literals
        "NAME",
        "NUMBER",
        "STRING",
    )

    def __init__(self, source, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)
        self.source = source
        self.error_stack = []

    def __lshift__(self, error: SATParserError):
        self.error_stack.push(error)

    def exit(self, code: int):
        raise SATExit(code)

    def interrupt(self):
        """"""
        while self.error_stack:
            error = self.error_stack.popleft()
            stderr << error

        self.exit(EXIT_FAILURE)

    def checkpoint(self):
        """"""
        if self.error_stack:
            self.interrupt()

    reserved = {
        "forall": "FORALL",
        "exists": "EXISTS",
        "unique": "UNIQUE",
        "wta": "UNIQUE",
        "sum": "EXISTS",
        "or": "OR",
        "xor": "XOR",
        "and": "AND",
        "iff": "IFF",
        "imp": "IMP",
        "not": "NOT",
        "pow": "POW",
    }

    op_map = {
        "FORALL": "FORALL",
        "EXISTS": "EXISTS",
        "UNIQUE": "UNIQUE",
        "OR": "|",
        "XOR": "^",
        "AND": "&",
        "IFF": "<->",
        "IMP": "->",
        "NOT": "~",
        "POW": "**",
    }

    # Regular expression rules for tokens
    t_DOTS = r"\:"

    t_LBRA = r"\["
    t_RBRA = r"\]"

    t_LPAR = r"\("
    t_RPAR = r"\)"

    t_LCUR = r"\{"
    t_RCUR = r"\}"

    t_NOT = r"\~"

    t_AND = r"\&"

    t_OR = r"\|"

    t_XOR = r"\^"

    t_IMP = r"\-\>"

    t_RIMP = r"\<\-"

    t_IFF = r"\<\-\>"

    t_COMMA = r"\,"

    t_DIV = r"\/"

    t_MOD = r"\%"

    t_POW = r"\*\*"
    t_MUL = r"\*"

    t_ADD = r"\+"

    t_SUB = r"\-"

    t_ENDL = r"\;"

    t_ASSIGN = r"\="

    t_EQ = r"\=\="
    t_GT = r"\>"
    t_LT = r"\<"

    t_GE = r"\>\="
    t_LE = r"\<\="

    t_NE = r"\!\="

    t_CONFIG = r"\?"

    @regex(r"\"(\\.|[^\"])*\"")
    def t_STRING(self, t):
        setattr(t, "string", t.value)
        t.value = String(t.value[1:-1])
        return t

    @regex(r"\n")
    def t_newline(self, _t):
        self.lexer.lineno += 1
        return None

    @regex(r"[a-zA-Z_][a-zA-Z0-9_]*")
    def t_NAME(self, t):
        setattr(t, "string", t.value)
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
            t.value = self.op_map[t.type]
        else:
            t.value = String(t.value)
        t.value = String(t.value)
        return t

    @regex(r"[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
    def t_NUMBER(self, t):
        setattr(t, "string", t.value)
        t.value = Number(t.value, source=self.source, lexpos=t.lexpos)
        return t

    # String containing ignored characters between tokens
    t_ignore = " \t"
    t_ignore_COMMENT = r"\#.*"

    @regex(r"\#\{[\s\S]*?\}\#")
    def t_ignore_MULTICOMMENT(self, t):
        self.lexer.lineno += str(t.value).count("\n")
        return None

    def t_error(self, t):
        stderr << f"Unknown token '{t.value}' at line {t.lineno}"
        if t:
            stderr << f"Syntax Error at line {t.lineno}:"
            stderr << self.source.lines[t.lineno - 1]
            stderr << f'{" " * (self.chrpos(t.lineno, t.lexpos))}^'
        else:
            stderr << "Unexpected End Of File."

    def chrpos(self, lineno, lexpos):
        return lexpos - self.source.table[lineno - 1] + 1
