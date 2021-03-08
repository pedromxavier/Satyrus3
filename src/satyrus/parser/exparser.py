"""
"""
## Standard Library
import itertools as it

## Third-Party
from ply import lex, yacc

## Local
from ..satlib import stderr, stdout, Source, Stack, PythonShell, PythonError, track
from ..types.error import SatParserError, SatLexerError, SatTypeError, SatSyntaxError, SatValueError, SatPythonError, SatExit
from ..types import Expr, Var, Number, String, SatType, PythonObject
from ..types.symbols.tokens import T_IDX, T_ADD, T_NEG

def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback
    return decor

class ExprLexer(object):

    ## List of token names.
    tokens = (
        'NOT', 'AND', 'OR', 'XOR', # logical

        'IMP', 'RIMP', 'IFF', # extended logical

        'EQ', # equal
        'GT', # greater than
        'LT', # less than

        'GE', # greater or equal
        'LE', # less or equal

        'NE', # not equal

        'MUL', 'DIV', 'MOD', 'ADD', 'SUB', # arithmetic

        'LBRA', 'RBRA', 'LPAR', 'RPAR',

        'NAME', 'NUMBER'
        )

    def __init__(self, source, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)
        self.source = source

        self.error_stack = Stack()

    def __lshift__(self, error: SatParserError):
        self.error_stack.push(error)

    def exit(self, code: int):
        raise SatExit(code)

    def tokenize(self, data: str):
        self.lexer.input(data)

        while True:
            tok = self.lexer.token()
            if not tok: 
                break      # No more input
            print(tok)

    def interrupt(self):
        """
        """
        while self.error_stack:
            error = self.error_stack.popleft()
            stderr[0] << error
        else:
            self.exit(1)

    def checkpoint(self):
        """
        """
        if self.error_stack: self.interrupt()

    # Regular expression rules for tokens

    t_LBRA = r'\['
    t_RBRA = r'\]'

    t_LPAR = r'\('
    t_RPAR = r'\)'

    t_NOT = r'\~'

    t_AND = r'\&'

    t_OR = r'\|'

    t_XOR = r'\^'

    t_IMP = r'\-\>'

    t_RIMP = r'\<\-'

    t_IFF = r'\<\-\>'

    t_DIV = r'\/'

    t_MOD = r'\%'

    t_MUL = r'\*'

    t_ADD = r'\+'

    t_SUB = r'\-'

    t_EQ = r'\=\='
    t_GT = r'\>'
    t_LT = r'\<'

    t_GE = r'\>\='
    t_LE = r'\<\='

    t_NE = r'\!\='

    t_ignore = ' \t'

    @regex(r"\n")
    def t_newline(self, t):
        self.lexer.lineno += 1
        return None

    @regex(r"[a-zA-Z_][a-zA-Z0-9_]*")
    def t_NAME(self, t):
        t.value = String(t.value)
        return t

    @regex(r"[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
    def t_NUMBER(self, t):
        t.value = Number(t.value)
        return t

    def t_error(self, t):
        stderr << f"Unknown token '{t.value}' at line {t.lineno}"
        if t:
            stderr << f"Syntax Error at line {t.lineno}:"
            stderr << self.source.lines[t.lineno-1]
            stderr << f'{" " * (self.chrpos(t.lineno, t.lexpos))}^'
        else:
            stderr << "Unexpected End Of File."

    def chrpos(self, lineno, lexpos):
        return (lexpos - self.source.table[lineno - 1] + 1)

class ExprParser(object):

    tokens = ExprLexer.tokens

    precedence = (

        ('left', 'NAME'),

        ('left', 'NUMBER'),

        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV', 'MOD'),

        ('left', 'XOR', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),

        ('left', 'IMP', 'RIMP', 'IFF'),

        ('left', 'EQ', 'NE', 'GE', 'LE', 'GT', 'LT'),

        ('left', 'LBRA', 'RBRA'),
        ('left', 'LPAR', 'RPAR'),
    )

    def __init__(self):
        ## Input
        self.source = None
        ## Output
        self.expr = None

        ## Lex & Yacc
        ## Initialize Lexer
        self.lexer = ExprLexer(self.source)

        ## Initialize Parser
        self.parser = yacc.yacc(module=self, debug=False)

        self.error_stack = Stack()

    def __lshift__(self, error: SatParserError):
        self.error_stack.push(error)

    def exit(self, code: int):
        raise SatExit(code)

    def interrupt(self):
        """
        """
        while self.error_stack:
            error = self.error_stack.popleft()
            stderr[0] << error
        else:
            self.exit(1)

    def checkpoint(self):
        """
        """
        if self.error_stack: self.interrupt()

    def parse(self, source: str):
        ## Input
        self.source = Source.from_str(source)
        
        ## Run Parser
        if not self.source:
            self << SatSyntaxError("Empty File.", target=self.source.eof)
        else:
            self.parser.parse(self.source)

        ## Checkpoint
        self.checkpoint()

        ## Output
        return self.expr
            
    def run(self, expr: Expr):
        self.expr = expr

    def get_arg(self, p, index: int=None, track: bool=True):
        if index is None:
            value = p
            if track:
                value.lexinfo = {
                    'lineno' : None,
                    'lexpos' : None,
                    'chrpos' : None,
                    'source' : self.source,
                }
        else:
            value = p[index]
            if track:
                lineno = p.lineno(index)
                lexpos = p.lexpos(index)
                value.lexinfo = {
                    'lineno' : lineno,
                    'lexpos' : lexpos,
                    'chrpos' : self.chrpos(lineno, lexpos),
                    'source' : self.source,
                }
        return value

    def cast_type(self, x: object, type_caster: type):
        """ Casts type according to `type_caster(x: object) -> y: object`
            copying `lexinfo` data, if available.
        """
        if hasattr(x, 'lexinfo'):
            lexinfo = getattr(x, 'lexinfo')
            y = type_caster(x)
            setattr(y, 'lexinfo', lexinfo)
            return y
        else:
            return type_caster(x)

    def p_start(self, p):
        """ start : expr
        """
        self.run(p[1])

    def p_condition(self, p):
        """ expr : expr EQ expr
                 | expr GT expr
                 | expr LT expr
                 | expr GE expr
                 | expr LE expr
                 | expr NE expr
        """
        p[0] = Expr(p[2], p[1], p[3])

    def p_expr(self, p):
        """ expr : literal
        """
        p[0] = p[1]

    def p_expr1(self, p):
        """ expr : NOT expr
                 | ADD expr
                 | SUB expr
        """
        p[0] = Expr(p[1], p[2])

    def p_expr2(self, p):
        """ expr : expr AND expr
                 | expr OR expr
                 | expr XOR expr
                 | expr ADD expr
                 | expr SUB expr
                 | expr MUL expr
                 | expr DIV expr
                 | expr MOD expr
                 | expr IMP expr
                 | expr RIMP expr
                 | expr IFF expr
        """
        if p[2] == T_NEG:
            p[0] = Expr(T_ADD, p[1], Expr(T_NEG, p[3]))
        else:
            p[0] = Expr(p[2], p[1], p[3])

    def p_expr_index(self, p):
        """ expr : expr LBRA expr RBRA
        """
        p[0] = Expr(T_IDX, p[1], p[3])

    def p_expr_par(self, p):
        """ expr : LPAR expr RPAR
        """
        p[0] = p[2]

    def p_literal(self, p):
        """ literal : constant
                    | varname
        """
        p[0] = p[1]

    def p_constant(self, p):
        """ constant : NUMBER
        """
        p[0] = self.get_arg(p, 1)

    def p_varname(self, p):
        """ varname : NAME
        """
        p[0] = self.cast_type(self.get_arg(p, 1), Var)

    def p_error(self, t):
        stderr[5] << f"Error Token: `{t}`"
        target = SatType()
        if t:
            target.lexinfo = {
                'lineno' : t.lineno,
                'lexpos' : t.lexpos,
                'chrpos' : self.chrpos(t.lineno, t.lexpos),
                'source' : self.source,
            }
            msg = "Invalid Syntax"
        else:
            lineno = len(self.source.lines) - 1
            lexpos = len(self.source.lines[lineno]) - 1
            target.lexinfo = {
                'lineno' : lineno,
                'lexpos' : lexpos,
                'chrpos' : self.chrpos(lineno, lexpos),
                'source' : self.source,
            }
            msg = "Unexpected End Of File."
        self << SatSyntaxError(msg=msg, target=target)
        return None

    def chrpos(self, lineno: int, lexpos: int):
        return (lexpos - self.source.table[lineno - 1] + 1)        
