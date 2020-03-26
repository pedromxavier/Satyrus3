"""
"""
from ply import lex, yacc

from sat_core import stderr
from sat_types import SatError
from sat_types import Expr, Number, Var

from sat_types.tokens import T_SHARP, T_ASSING, T_DOTS

class SatParserError(SatError):
    pass

class SatLexerError(SatError):
    pass

def regex(pattern):
    def decor(callback):
        callback.__doc__ = pattern
        return callback
    return decor

class SatLexer(object):
    ## List of token names.
    tokens = (
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
        )

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
    def t_STRING(self, t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r"\n+")
    def t_newline(self, t):
        self.lexer.lineno += len(t.value)

    @regex(r"[a-zA-Z_][a-zA-Z0-9_']*")
    def t_NAME(self, t):
        t.value = Var(t.value)
        return t

    @regex(r"[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
    def t_NUMBER(self, t):
        t.value = Number(t.value)
        return t

    def t_error(self, t):
        stderr << f"SyntaxError at {t} <Lexer>"

    # String containing ignored characters between tokens
    t_ignore = ' \t'

    t_ignore_COMMENT = r'%.*'

    t_ignore_MULTICOMMENT = r'\%\{[\s\S]*?\}\%'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)

class SatParser(object):

    tokens = SatLexer.tokens

    precedence = (

        ('left', 'LBRA', 'RBRA'),

        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV'),

        ('left', 'XOR', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),

        ('left', 'IMP', 'RIMP', 'IFF'),

        ('left', 'EQ', 'NE', 'GE', 'LE', 'GT', 'LT'),

        ('left', 'FORALL', 'EXISTS', 'EXISTS_ONE'),

        ('left', 'LCUR', 'RCUR'),
        ('left', 'LPAR', 'RPAR'),
        
        ('left', 'DOTS'),

        ('left', 'SHARP'),

        ('left', 'NAME'),
        ('left', 'STRING', 'NUMBER'),

        ('left', 'ENDL'),
    )

    def __init__(self):
        self.lexer = SatLexer()
        self.parser = yacc.yacc(module=self)

        self.bytecode = None

    def parse(self, source):
        if not source:
            raise SatParserError('Empty source for parsing.')
        else:
            self.parser.parse(source)

    def run(self, code):
        self.bytecode = code

    def p_start(self, p):
        """ start : code
        """
        self.run(p[1])

    def p_code(self, p):
        """ code : code stmt
                 | stmt
        """
        if len(p) == 3:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [ p[1],]

    def p_stmt(self, p):
        """ stmt : sys_config ENDL
                 | def_const ENDL
                 | def_array ENDL
                 | def_restr ENDL
        """
        p[0] = p[1]

    def p_sys_config(self, p):
        """ sys_config : SHARP NAME DOTS NUMBER
                    | SHARP NAME DOTS STRING
        """
        p[0] = (T_SHARP, p[2], p[4])

    def p_def_const(self, p):
        """ def_const : NAME ASSIGN literal
        """
        p[0] = (p[1], p[3])

    def p_literal(self, p):
        """ literal : NUMBER
                    | NAME
        """
        p[0] = p[1]

    def p_def_array(self, p):
        """ def_array : NAME shape ASSIGN array_buffer
                    | NAME shape
        """
        if len(p) == 5: # array declared
            buffer = p[4]
        else: # implicit array
            buffer = []

        p[0] = (p[1], p[2], buffer)

    def p_shape(self, p):
        """ shape : shape index
                | index
        """
        if len(p) == 3:
            p[0] = (*p[1], p[2])
        else:
            p[0] = ( p[1],)

    def p_index(self, p):
        """ index : LBRA literal RBRA
        """
        p[0] = p[2]

    def p_array_buffer(self, p):
        """ array_buffer : LCUR array RCUR
        """
        p[0] = p[2]

    def p_array(self, p):
        """ array : array COMMA array_item
                | array_item
        """
        if len(p) == 4:
            p[0] = [*p[1], p[3]]
        else:
            p[0] = [ p[1],]

    def p_array_item(self, p):
        """ array_item : array_index DOTS literal
        """
        p[0] = (p[1], p[3])

    def p_array_index(self, p):
        """ array_index : LPAR literal_seq RPAR
        """
        p[0] = p[2]

    def p_literal_seq(self, p):
        """ literal_seq : literal_seq COMMA literal
                        | literal
        """
        if len(p) == 4:
            p[0] = (*p[1], p[3])
        else:
            p[0] = ( p[1],)

    def p_def_restr(self, p):
        """ def_restr : LPAR NAME RPAR NAME LBRA literal RBRA DOTS loops expr
                    | LPAR NAME RPAR NAME DOTS loops expr
        """
        type = p[2]
        name = p[4]
        
        if len(p) == 11:
            level = p[6]
            loops = p[9]
            expr = p[10]
        else:
            level = 0
            loops = p[6]
            expr = p[7]

        p[0] = (type, name, level, loops, expr)

    def p_loops(self, p):
        """ loops : loops loop
                | loop
        """
        if len(p) == 3:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [ p[1],]

    def p_loop(self, p):
        """ loop : quant LCUR NAME ASSIGN domain COMMA conditions RCUR
                | quant LCUR NAME ASSIGN domain RCUR
        """
        if len(p) == 9:
            p[0] = (p[1], p[3], p[5], p[7])
        else:
            p[0] = (p[1], p[3], p[5], None)

    def p_quant(self, p):
        """ quant : FORALL
                | EXISTS
                | EXISTS_ONE
        """
        p[0] = p[1]

    def p_domain(self, p):
        """ domain : LBRA literal DOTS literal DOTS literal RBRA
                | LBRA literal DOTS literal RBRA
        """
        if len(p) == 8:
            p[0] = (p[2], p[4], p[6])
        else:
            p[0] = (p[2], p[4], None)

    def p_conditions(self, p):
        """ conditions : conditions COMMA condition
                    | condition
        """
        if len(p) == 4:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [p[1],]

    def p_condition(self, p):
        """ condition : expr EQ expr
                    | expr GT expr
                    | expr LT expr
                    | expr GE expr
                    | expr LE expr
                    | expr NE expr
        """
        p[0] = p[1]

    def p_condition_expr(self, p):
        """ condition : expr
        """
        p[0] = p[1]

    def p_expr(self, p):
        """ expr : literal
        """
        p[0] = p[1]

    def p_expr1(self, p):
        """ expr : NOT expr
                | ADD expr
                | SUB expr
        """
        p[0] = (p[1], p[2])

    def p_expr2(self, p):
        """ expr : expr AND expr
                | expr OR expr
                | expr XOR expr
                | expr ADD expr
                | expr SUB expr
                | expr MUL expr
                | expr DIV expr
                | expr IMP expr
                | expr RIMP expr
                | expr IFF expr
        """
        p[0] = (p[2], p[1], p[3])

    def p_expr_index(self, p):
        """ expr : expr LBRA expr RBRA
        """
        p[0] = ('[]', p[1], p[3])

    def p_expr_par(self, p):
        """ expr : LPAR expr RPAR
        """
        p[0] = p[2]

    def p_error(self, p):
        stderr << f"SyntaxError at {p} <Parser>"