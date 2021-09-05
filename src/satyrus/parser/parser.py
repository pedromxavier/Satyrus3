"""
"""
## Standard Library
import itertools as it

## Third-Party
from ply import lex, yacc

from cstream import stderr, stdout

## Local
from ..satlib import Source, Stack, PythonShell, PythonError, Timing
from ..error import SatParserError, SatLexerError, SatTypeError, SatSyntaxError, SatValueError, SatPythonError, SatExit
from ..types import Expr, Var, Number, String, SatType, PythonObject
from ..symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT, CMD_PYTHON
from ..symbols import T_IDX, T_ADD, T_NEG

def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback
    return decor

class SatLexer(object):

    ## List of token names.
    tokens = (
        'FORALL', 'EXISTS', 'UNIQUE', # quantifiers

        'NOT', 'AND', 'OR', 'XOR', # logical

        'IMP', 'RIMP', 'IFF', # extended logical

        'CONFIG',

        'ENDL',

        'COMMA',

        'ASSIGN',

        'EQ', # equal
        'GT', # greater than
        'LT', # less than

        'GE', # greater or equal
        'LE', # less or equal

        'NE', # not equal

        'MUL', 'DIV', 'MOD', 'ADD', 'SUB', # arithmetic

        'DOTS',

        'LBRA', 'RBRA', 'LPAR', 'RPAR', 'LCUR', 'RCUR',

        'NAME', 'NUMBER', 'STRING',

        'PYTHON'
        )

    def __init__(self, source, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)
        self.source = source

        self.error_stack = Stack()

        ## Separate python shell
        self.python_shell = PythonShell()

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

    reserved = {
        'forall' : 'FORALL',
        'exists' : 'EXISTS',
        'unique' : 'UNIQUE',
        'or' : 'OR',
        'xor': 'XOR',
        'and': 'AND',
        'iff': 'IFF',
        'imp': 'IMP',
        'not': 'NOT',
    }

    op_map = {
        'FORALL' : '@',
        'EXISTS' : '$',
        'UNIQUE' : '$!',
        'OR' : '|',
        'XOR': '^',
        'AND': '&',
        'IFF': '<->',
        'IMP': '->',
        'NOT': '~',
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
    t_UNIQUE = r'\$\!'

    t_NOT = r'\~'

    t_AND = r'\&'

    t_OR = r'\|'

    t_XOR = r'\^'

    t_IMP = r'\-\>'

    t_RIMP = r'\<\-'

    t_IFF = r'\<\-\>'

    t_COMMA = r'\,'

    t_DIV = r'\/'

    t_MOD = r'\%'

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

    t_CONFIG = r'\?'

    @regex(r'\"(\\.|[^\"])*\"')
    def t_STRING(self, t):
        t.value = String(t.value[1:-1])
        return t

    @regex(r'\`(\\.|[^\`])*\`')
    def t_PYTHON(self, t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r"\n")
    def t_newline(self, t):
        self.lexer.lineno += 1
        return None

    @regex(r"[a-zA-Z_][a-zA-Z0-9_]*")
    def t_NAME(self, t):
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
            t.value = self.op_map[t.type]
        else:
            t.value = String(t.value)
        t.value = String(t.value)
        return t

    @regex(r"[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
    def t_NUMBER(self, t):
        t.value = Number(t.value, source=self.source, lexpos=t.lexpos)
        return t

    # String containing ignored characters between tokens
    t_ignore = ' \t'
    t_ignore_COMMENT = r'\#.*'

    @regex(r'\#\{[\s\S]*?\}\#')
    def t_ignore_MULTICOMMENT(self, t):
        self.lexer.lineno += str(t.value).count('\n')
        return None

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

class SatParser(object):

    tokens = SatLexer.tokens

    precedence = (

        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV', 'MOD'),

        ('left', 'XOR', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),

        ('left', 'IMP', 'RIMP', 'IFF'),

        ('left', 'EQ', 'NE', 'GE', 'LE', 'GT', 'LT'),

        ('left', 'FORALL', 'EXISTS', 'UNIQUE'),

        ('left', 'DOTS'),

        ('left', 'LBRA', 'RBRA'),
        ('left', 'LCUR', 'RCUR'),
        ('left', 'LPAR', 'RPAR'),

        ('left', 'CONFIG'),

        ('left', 'NAME'),

        ('left', 'STRING', 'NUMBER'),

        ('left', 'ENDL'),

        ('left', 'PYTHON')
    )

    def __init__(self):
        ## Input
        self.source = None
        ## Output
        self.bytecode = None

        ## Lex & Yacc
        self.lexer = None
        self.parser = None

        self.error_stack = Stack()

        ## Python Shell
        self.python_shell = PythonShell()

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

    @Timing.timer(level=1, section="Parser.parse")
    def parse(self, source: Source):
        ## Input
        self.source = source
        
        ## Initialize Lexer
        self.lexer = SatLexer(self.source)

        ## Initialize Parser
        self.parser = yacc.yacc(module=self, debug=False)
        
        ## Run Parser
        if not self.source:
            self << SatSyntaxError("Empty File.", target=self.source.eof)
        else:
            self.parser.parse(self.source)

        ## Checkpoint
        self.checkpoint()

        ## Output
        return self.bytecode
            
    def run(self, code : list):
        self.bytecode = [cmd for cmd in code if cmd is not None]

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
                 | def_constant ENDL
                 | def_array ENDL
                 | def_constraint ENDL
                 | cmd_python ENDL
        """
        p[0] = p[1]

    def p_cmd_python(self, p):
        """ cmd_python : PYTHON
        """
        ## Executes python command
        self.python_shell(p[1], evaluate=False)

        p[0] = None

    def p_sys_config(self, p):
        """ sys_config : CONFIG NAME DOTS sys_config_args
        """
        name = self.get_arg(p, 2)
        args = p[4]
        p[0] = (SYS_CONFIG, name, args)

    def p_sys_config_args(self, p):
        """ sys_config_args : sys_config_args COMMA sys_config_arg
                            | sys_config_arg
        """
        if len(p) == 4:
            p[0] = [*p[1], self.get_arg(p, 3)]
        else:
            p[0] = [self.get_arg(p, 1)]

    def p_sys_config_arg(self, p):
        """ sys_config_arg : NUMBER
                           | STRING
        """
        p[0] = p[1]

    def p_def_constant(self, p):
        """ def_constant : varname ASSIGN expr
        """
        p[0] = (DEF_CONSTANT, p[1], p[3])

    def p_literal(self, p):
        """ literal : constant
                    | python_literal
                    | varname
        """
        p[0] = p[1]

    def p_constant(self, p):
        """ constant : NUMBER
        """
        p[0] = p[1]

    def p_varname(self, p):
        """ varname : NAME
        """
        p[0] = Var(p[1], source=self.source, lexpos=p.lexpos(1))

    def p_python_literal(self, p):
        """ python_literal : PYTHON
        """
        py_code = self.get_arg(p, 1)

        try:
            py_object = PythonObject(self.python_shell(str(py_code), evaluate=True))
        except PythonError as error:
            self << SatPythonError(*error.args)
        finally:
            self.checkpoint()
        
        self.source.propagate(py_code, py_object)

        p[0] = py_object

    def p_def_array(self, p):
        """ def_array : varname shape ASSIGN array_buffer
                      | varname shape
        """
        name = p[1]
        shape = p[2]

        if len(p) == 5: # array declared
            buffer = p[4]
        else: # implicit array
            buffer = None

        p[0] = (DEF_ARRAY, name, shape, buffer)

    def p_shape(self, p):
        """ shape : shape index
                  | index
        """
        if len(p) == 3:
            p[0] = (*p[1], p[2])
        else:
            p[0] = (p[1],)

    def p_index(self, p):
        """ index : LBRA expr RBRA
        """
        p[0] = p[2]

    def p_array_buffer(self, p):
        """ array_buffer : LCUR array RCUR
                         | python_literal
        """
        if len(p) == 4: ## default buffer
            p[0] = p[2]
        else: ## python literal
            p[1]

    def p_array(self, p):
        """ array : array COMMA array_item
                  | array_item
        """
        if len(p) == 4:
            p[0] = [*p[1], p[3]]
        else:
            p[0] = [ p[1],]

    def p_array_item(self, p):
        """ array_item : array_index DOTS expr
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

    def p_def_constraint(self, p):
        """ def_constraint : LPAR NAME RPAR varname LBRA literal RBRA DOTS loops expr
                           | LPAR NAME RPAR varname DOTS loops expr
        """
        type_= String(p[2], source=self.source, lexpos=p.lexpos(2))
        name = p[4]
        
        if len(p) == 11:
            level = p[6]
            loops = p[9]
            expr  = p[10]
        else:
            level = None
            loops = p[6]
            expr  = p[7]

        p[0] = (DEF_CONSTRAINT, type_, name, loops, expr, level)

    def p_loops(self, p):
        """ loops : loop_stack
                  |
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = []

    def p_loop_stack(self, p):
        """ loop_stack : loop_stack loop
                       | loop
        """
        if len(p) == 3:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [ p[1],]

    def p_loop(self, p):
        """ loop : quant LCUR varname ASSIGN domain COMMA conditions RCUR
                 | quant LCUR varname ASSIGN domain RCUR
        """
        if len(p) == 9:
            p[0] = (p[1], p[3], p[5], p[7])
        else:
            p[0] = (p[1], p[3], p[5], None)

    def p_quant(self, p):
        """ quant : FORALL
                  | EXISTS
                  | UNIQUE
        """
        p[0] = p[1]

    def p_domain(self, p):
        """ domain : LBRA expr DOTS expr DOTS expr RBRA
                   | LBRA expr DOTS expr RBRA
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

    def p_condition_expr(self, p):
        """ condition : expr
        """
        p[0] = p[1]

    def p_condition(self, p):
        """ expr : expr EQ expr
                 | expr GT expr
                 | expr LT expr
                 | expr GE expr
                 | expr LE expr
                 | expr NE expr
        """
        p[0] = Expr(p[2], p[1], p[3], source=self.source, lexpos=p.lexpos(2))

    def p_expr(self, p):
        """ expr : literal
        """
        p[0] = p[1]

    def p_expr1(self, p):
        """ expr : NOT expr
                 | ADD expr
                 | SUB expr
        """
        p[0] = Expr(p[1], p[2], source=self.source, lexpos=p.lexpos(1))

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
            p[0] = Expr(T_ADD, p[1], Expr(T_NEG, p[3], source=self.source, lexpos=p.lexpos(2)), source=self.source, lexpos=p.lexpos(2))
        else:
            p[0] = Expr(p[2], p[1], p[3], source=self.source, lexpos=p.lexpos(2))

    def p_expr_index(self, p):
        """ expr : expr LBRA expr RBRA
        """
        p[0] = Expr(T_IDX, p[1], p[3], source=self.source, lexpos=p.lexpos(2))

    def p_expr_par(self, p):
        """ expr : LPAR expr RPAR
        """
        p[0] = p[2]

    def p_error(self, t):
        stderr[3] << f"Error Token: `{t}`"
        target = SatType()
        if t:
            target.lexinfo = self.source.getlex(t.lexpos)
            msg = "Invalid Syntax"
        else:
            target = self.source.eof
            msg = "Unexpected End Of File."
        self << SatSyntaxError(msg=msg, target=target)
        return None

    def chrpos(self, lineno: int, lexpos: int):
        return (lexpos - self.source.table[lineno - 1] + 1)        