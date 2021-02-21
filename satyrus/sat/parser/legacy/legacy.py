"""
"""
## Standard Library
import itertools as it

## Third-Party
from ply import lex, yacc

## Local
from ....satlib import stderr, stdout, Source, Stack, track
from ...types.error import SatParserError, SatLexerError, SatTypeError, SatSyntaxError, SatValueError, SatWarning, SatExit
from ...types import Expr, Var, Number, String, SatType
from ...types.symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT, CONS_INT, CONS_OPT
from ...types.symbols.tokens import T_ADD, T_NEG, T_IDX, T_FORALL, T_EXISTS

def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback
    return decor

class SatLegacyLexer(object):

    ## Keywords
    keywords = [
		## load
		'from',

		## logic
		'and', 'or', 'not', 'xor',

		## constraints
		'optgroup', 'intgroup',
		'forall', 'exists',
		'in', 'where',

		## penalties
		'correlation', 'penalties', 'level'
    ]

    reserved = {kw: kw.upper() for kw in keywords}

    ## List of token names.
    tokens = (
        ## 'FORALL', 'EXISTS', # 'EXISTS_ONE', # quantifiers

        ## 'NOT', 'AND', 'OR', 'XOR', # logical

        'IMP', 'RIMP', 'IFF', # extended logical

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
        ) + tuple(map(str.upper, keywords))

    def __init__(self, source, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)
        self.source = source

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

    # Regular expression rules for tokens
    t_DOTS = r'\:'

    t_LBRA = r'\['
    t_RBRA = r'\]'

    t_LPAR = r'\('
    t_RPAR = r'\)'

    t_LCUR = r'\{'
    t_RCUR = r'\}'

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

    @regex(r'\"(\\.|[^\"])*\"')
    def t_STRING(self, t):
        t.value = String(t.value[1:-1])
        return t

    @regex(r"\n")
    def t_newline(self, t):
        self.lexer.lineno += 1
        return None

    @regex(r"[a-zA-Z_][a-zA-Z0-9_]*")
    def t_NAME(self, t):
        t.type = self.reserved.get(str(t.value),'NAME')
        t.value = String(t.value)
        return t

    @regex(r"[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?")
    def t_NUMBER(self, t):
        t.value = Number(t.value)
        return t

    # String containing ignored characters between tokens
    t_ignore = ' \t'
    t_ignore_COMMENT = r'\/\/.*'

    @regex(r'\#\*[\s\S]*?\*\/')
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

class SatLegacyParser(object):

    tokens = SatLegacyLexer.tokens

    extra_keywords = [
		## load
		'from',

		## constraints
		'optgroup', 'intgroup',
		'forall', 'exists',
		'in', 'where',

		## penalties
		'correlation', 'penalties', 'level'
    ]

    precedence = (
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV'),

        ('left', 'XOR', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),

        ('left', 'IMP', 'RIMP', 'IFF'),

        ('left', 'EQ', 'NE', 'GE', 'LE', 'GT', 'LT'),

        ('left', 'DOTS'),

        ('left', 'LBRA', 'RBRA'),
        ('left', 'LCUR', 'RCUR'),
        ('left', 'LPAR', 'RPAR'),

        ('left', 'NAME'),

        ('left', 'STRING', 'NUMBER'),

        ('left', 'ENDL'),
    )

    SYMBOL_TABLE = {
        'and': '&',
        'or': '|',
        'xor': '^',
        'not': '~'
    }

    def symbol_table(self, symbol: str):
        if symbol in self.SYMBOL_TABLE:
            return self.SYMBOL_TABLE[symbol]
        else:
            return symbol

    def __init__(self):
        ## Input
        self.source = None
        ## Output
        self.bytecode = None

        ## Lex & Yacc
        self.lexer = None
        self.parser = None

        self.error_stack = Stack()

        ## Lazy definitions
        self.array_table = {}
        self.constraint_table = {}

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

    def parse(self, source: Source):
        ## Input
        self.source = source
        
        ## Initialize Lexer
        self.lexer = SatLegacyLexer(self.source)

        ## Initialize Parser
        self.parser = yacc.yacc(module=self)
        
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
        """ start : definitions constraints penalties
        """
        self.run([*p[1], *p[2], *p[3]])

    def p_definitions(self, p):
        """ definitions : definitions definition
                        | definition
        """
        if len(p) == 3:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [ p[1],]

    def p_definition(self, p):
        """ definition : def_constant ENDL
                       | dec_array ENDL
                       | def_array ENDL
                       | FROM STRING ENDL
        """
        p[0] = p[1]

    def p_constraints(self, p):
        """ constraints : constraints constraint
                        | constraint
        """
        if len(p) == 3:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [ p[1],]

    def p_constraint(self, p):
        """ constraint : dec_constraint ENDL
        """
        p[0] = p[1]

    def p_def_constant(self, p):
        """ def_constant : varname ASSIGN constant
        """
        name = self.get_arg(p, 1)
        value = self.get_arg(p, 3)
        p[0] = (DEF_CONSTANT, name, value)

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

    def p_dec_array(self, p):
        """ dec_array : varname LPAR shape RPAR
        """
        name = self.get_arg(p, 1)
        shape = p[3]

        ## declare array
        self.array_table[name] = shape

        p[0] = (DEF_ARRAY, name, shape, None)

    def p_def_array(self, p):
        """ def_array : varname ASSIGN array_buffer
        """
        name = self.get_arg(p, 1)
        buffer = p[3]
        
        if name not in self.array_table:
            self << SatSyntaxError('Assignment to undeclared array structure.')
            self.checkpoint()
        else:
            shape = self.array_table[name]
            p[0] = (DEF_ARRAY, name, shape, buffer)

    def p_shape(self, p):
        """ shape : shape COMMA expr
                  | expr
        """
        if len(p) == 4:
            p[0] = (*p[1], p[3])
        else:
            p[0] = ( p[1],)

    def p_array_buffer(self, p):
        """ array_buffer : LBRA array RBRA
        """
        p[0] = p[2]
    
    def p_array(self, p):
        """ array : array ENDL array_item
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
        """ array_index : literal_seq
        """
        p[0] = p[1]

    def p_literal_seq(self, p):
        """ literal_seq : literal_seq COMMA literal
                        | literal
        """
        if len(p) == 4:
            p[0] = (*p[1], p[3])
        else:
            p[0] = ( p[1],)

    def p_dec_constraint(self, p):
        """ dec_constraint : group varname DOTS loops DOTS expr
        """
        type_= p[1]
        name = p[2]
        
        loops = p[4]
        expr  = p[6]

        constraint = (type_, name, loops, expr)

        if name in self.constraint_table:
            self.constraint_table[name].append(constraint)
        else:
            self.constraint_table[name] = [constraint]

    def p_group(self, p):
        """ group : INTGROUP
                  | OPTGROUP
        """
        group_name = self.get_arg(p, 1)
        if str(group_name) == 'intgroup':
            name = String(CONS_INT)
        elif str(group_name) == 'optgroup':
            name = String(CONS_OPT)
        else:
            raise NameError(f'Invalid group {group_name}')

        track(group_name, name)

        p[0] = name

    def p_loops(self, p):
        """ loops : loops ENDL loop_stack
                  | loop_stack
        """
        if len(p) == 4:
            p[0] = [*p[1], *p[3]]
        elif len(p) == 2:
            p[0] = p[1]
        elif len(p) == 1:
            p[0] = []

    def p_loop(self, p):
        """ loop_stack : quant LCUR var_stack RCUR WHERE domains AND conditions
                       | quant LCUR var_stack RCUR WHERE domains
        """
        loop_stack = []

        var_stack = set(p[3])

        domains = p[6]

        if len(p) == 9:
            conditions = p[8]
        else:
            conditions = None

        stack = set()

        quant = {'forall': T_FORALL, 'exists': T_EXISTS}[p[1].lower()]

        for var, a, b in domains:
            stack.add(var)

            loop = [quant, var, (a, b, None), None]

            loop_stack.append(loop)

        if var_stack != stack:
            self << SatSyntaxError('Loop and domain mismatch.', target=(var_stack ^ stack).pop())
            self.checkpoint()

        loop_stack[-1][-1] = conditions

        p[0] = loop_stack

    def p_var_stack(self, p):
        """ var_stack : var_stack COMMA varname
                      | varname
        """
        if len(p) == 4:
            p[0] = [*p[1], p[3]]
        else:
            p[0] = [ p[1],]
    
    def p_domains(self, p):
        """ domains : domains COMMA domain
                    | domain
        """
        if len(p) == 4:
            p[0] = [*p[1], p[3]]
        else:
            p[0] = [ p[1],]

    def p_quant(self, p):
        """ quant : FORALL
                  | EXISTS
        """
        p[0] = p[1]

    def p_domain(self, p):
        """ domain : varname IN LPAR literal COMMA literal RPAR
        """
        p[0] = (p[1], p[4], p[6])

    def p_conditions(self, p):
        """ conditions : conditions COMMA condition
                       | condition
        """
        if len(p) == 4:
            p[0] = [*p[1], p[3]]
        else:
            p[0] = [ p[1],]

    def p_condition(self, p):
        """ condition : expr EQ expr
                      | expr GT expr
                      | expr LT expr
                      | expr GE expr
                      | expr LE expr
                      | expr NE expr
        """
        p[0] = Expr(self.symbol_table(p[2]), p[1], p[3])

    def p_condition_expr(self, p):
        """ condition : expr
        """
        p[0] = p[1]

    def p_expr(self, p):
        """ expr : literal
        """
        p[0] = p[1]

    def p_unary_expr(self, p):
        """ expr : NOT expr
                 | ADD expr
                 | SUB expr
        """
        p[0] = Expr(self.symbol_table(p[1]), p[2])

    def p_binary_expr(self, p):
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
        symbol = self.symbol_table(p[2])
        if symbol == T_NEG:
            p[0] = Expr(T_ADD, p[1], Expr(T_NEG, p[3]))
        else:
            p[0] = Expr(symbol, p[1], p[3])

    def p_expr_index(self, p):
        """ expr : expr LBRA expr RBRA
        """
        p[0] = Expr(T_IDX, p[1], p[3])

    def p_expr_par(self, p):
        """ expr : LPAR expr RPAR
        """
        p[0] = p[2]

    def p_penalties(self, p):
        """ penalties : PENALTIES DOTS penalty_list
        """
        penalties = p[3]

        commands = []

        for name, level, cor in penalties: #pylint: disable=unused-variable
            if name not in self.constraint_table:
                self < SatWarning(f'Undefined constraint group {name} to be ignored.', target=name)
            else:
                index = 0
                for type_, name, loops, expr in self.constraint_table[name]:
                    if str(type_) == CONS_OPT and level == Number('0'):
                        level = None
                    commands.append((DEF_CONSTRAINT, type_, f"{name}-{index}", loops, expr, level))
                    index += 1

                    
        p[0] = commands

    def p_penalty_list(self, p):
        """ penalty_list : penalty_list penalty
                         | penalty
        """
        if len(p) == 3:
            p[0] = [*p[1], p[2]]
        else:
            p[0] = [ p[1],]
    
    def p_penalty(self, p):
        """ penalty : varname DOTS LEVEL NUMBER COMMA CORRELATION NUMBER ENDL
                    | varname DOTS LEVEL NUMBER ENDL
        """
        if len(p) == 9:
            p[0] = (p[1], p[4], p[7])
        else:
            p[0] = (p[1], p[4], None)

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