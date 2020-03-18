from ply import yacc

from sat_core.stream import stderr
from sat_types.error import SatError
from sat_lexer import SatLexer

lexer = SatLexer()

class SatParseError(SatError):
    ...

class SatParser:

    parser = None

    @classmethod
    def init(cls, parser):
        cls.parser = parser

    @classmethod
    def parse(cls, source):
        if cls.parser is not None:
            cls.parser.parse(source)
        else:
            raise SatParseError("Parser wasn't initialized.")

    @classmethod
    def run(cls, code):
        bytecode = [*code]

        return bytecode

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

def p_start(p):
    """ start : code
    """
    SatParser.run(p[1])

def p_code(p):
    """ code : code stmt
             | stmt
    """
    if len(p) == 3:
        p[0] = [*p[1], p[2]]
    else:
        p[0] = [ p[1],]

def p_stmt(p):
    """ stmt : sys_config ENDL
             | def_const ENDL
             | def_array ENDL
             | def_restr ENDL
    """
    p[0] = p[1]

def p_sys_config(p):
    """ sys_config : SHARP NAME DOTS NUMBER
                   | SHARP NAME DOTS STRING
    """
    p[0] = (p[2], p[4])

def p_def_const(p):
    """ def_const : NAME ASSIGN literal
    """
    p[0] = (p[1], p[3])

def p_literal(p):
    """ literal : NUMBER
                | NAME
    """
    p[0] = p[1]

def p_def_array(p):
    """ def_array : NAME shape ASSIGN array_buffer
                  | NAME shape
    """
    if len(p) == 5: # array declared
        buffer = p[4]
    else: # implicit array
        buffer = []

    p[0] = (p[1], p[2], buffer)

def p_shape(p):
    """ shape : shape index
              | index
    """
    if len(p) == 3:
        p[0] = (*p[1], p[2])
    else:
        p[0] = ( p[1],)

def p_index(p):
    """ index : LBRA literal RBRA
    """
    p[0] = p[2]

def p_array_buffer(p):
    """ array_buffer : LCUR array RCUR
    """
    p[0] = p[2]

def p_array(p):
    """ array : array COMMA array_item
              | array_item
    """
    if len(p) == 4:
        p[0] = [*p[1], p[3]]
    else:
        p[0] = [ p[1],]

def p_array_item(p):
    """ array_item : array_index DOTS literal
    """
    p[0] = (p[1], p[3])

def p_array_index(p):
    """ array_index : LPAR literal_seq RPAR
    """
    p[0] = p[2]

def p_literal_seq(p):
    """ literal_seq : literal_seq COMMA literal
                    | literal
    """
    if len(p) == 4:
        p[0] = (*p[1], p[3])
    else:
        p[0] = ( p[1],)

def p_def_restr(p):
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

def p_loops(p):
    """ loops : loops loop
              | loop
    """
    if len(p) == 3:
        p[0] = [*p[1], p[2]]
    else:
        p[0] = [ p[1],]

def p_loop(p):
    """ loop : quant LCUR NAME ASSIGN domain COMMA conditions RCUR
             | quant LCUR NAME ASSIGN domain RCUR
    """
    if len(p) == 9:
        p[0] = (p[1], p[3], p[5], p[7])
    else:
        p[0] = (p[1], p[3], p[5], None)

def p_quant(p):
    """ quant : FORALL
              | EXISTS
              | EXISTS_ONE
    """
    p[0] = p[1]

def p_domain(p):
    """ domain : LBRA literal DOTS literal DOTS literal RBRA
               | LBRA literal DOTS literal RBRA
    """
    if len(p) == 8:
        p[0] = (p[2], p[4], p[6])
    else:
        p[0] = (p[2], p[4], None)

def p_conditions(p):
    """ conditions : conditions COMMA condition
                   | condition
    """
    if len(p) == 4:
        p[0] = [*p[1], p[2]]
    else:
        p[0] = [p[1],]

def p_condition(p):
    """ condition : expr EQ expr
                  | expr GT expr
                  | expr LT expr
                  | expr GE expr
                  | expr LE expr
                  | expr NE expr
    """
    p[0] = p[1]

def p_condition_expr(p):
    """ condition : expr
    """
    p[0] = p[1]

def p_expr(p):
    """ expr : literal
    """
    p[0] = p[1]

def p_expr1(p):
    """ expr : NOT expr
             | ADD expr
             | SUB expr
    """
    p[0] = (p[1], p[2])

def p_expr2(p):
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

def p_expr_index(p):
    """ expr : expr LBRA expr RBRA
    """
    p[0] = ('[]', p[1], p[3])

def p_expr_par(p):
    """ expr : LPAR expr RPAR
    """
    p[0] = p[2]

def p_error(p):
    stderr << "SyntaxError at {} <Parser>".format(p)
        
SatParser.init(yacc.yacc())