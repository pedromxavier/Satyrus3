from sat_lexer import *;

import ply.yacc as yacc;

precedence = (

)

def p_run(p):
    """
        run : code
    """
    p_run.run(p[1])

p_run.run = lambda p: None;

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
    # Stmt('#', 'name', 'value')
    p[0] = Stmt('#', p[2], p[4])

def p_def_const(p):
    """ def_const : NAME ASSIGN literal
    """
    # Stmt('=', 'name', 'value')
    p[0] = Stmt('=', p[1], p[3])

def p_literal(p):
    """ literal : NUMBER
                | NAME
    """
    p[0] = p[1]

def p_def_array(p):
    """ def_array : NAME shape ASSIGN array_buffer
                  | NAME shape
    """
    # Stmt('=', 'name', 'shape', 'buffer')
    if len(p) == 5: # array declared
        buffer = p[4]
    else: # implicit array
        buffer = []

    p[0] = Stmt('=', p[1], p[2], buffer)

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
    """ def_restr : LPAR NAME RPAR NAME RBRA literal RBRA DOTS loops expr
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

    p[0] = Stmt(':', type, name, level, loops, expr)

def p_loops(p):
    """ loops : loops loop
              | loop
    """
    if len(p) == 3:
        p[0] = [*p[1], p[3]]
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

def p_error(p):
    return p_error.error(p)

p_error.error = lambda p: None;

parser = yacc.yacc()
parser.p_run = p_run;
parser.p_error = p_error;
