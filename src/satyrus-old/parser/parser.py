"""
"""
# Standard Library

# Third-Party
from ply import lex, yacc
from cstream import stderr, DEBUG

# Local
from ..satlib import Source, Stack, PythonShell, Timing
from ..error import (
    EXIT_FAILURE,
    SATParserError,
    SATSyntaxError,
    SATExit,
)
from ..types import Expr, Var, Number, String, SATType
from ..symbols import SYS_CONFIG, DEF_CONSTANT, DEF_ARRAY, DEF_CONSTRAINT
from ..symbols import T_IDX, T_ADD, T_NEG, T_LOOP




class SATParser(object):

    tokens = SATLexer.tokens

    precedence = (
        ("left", "ADD", "SUB"),
        ("left", "MUL", "DIV", "MOD"),
        ("left", "POW"),
        ("left", "IMP", "RIMP", "IFF"),
        ("left", "XOR", "OR"),
        ("left", "AND"),
        ("left", "NOT"),
        ("left", "EQ", "NE", "GE", "LE", "GT", "LT"),
        ("left", "FORALL", "EXISTS", "UNIQUE"),
        ("left", "DOTS"),
        ("left", "LBRA", "RBRA"),
        ("left", "LCUR", "RCUR"),
        ("left", "LPAR", "RPAR"),
        ("left", "CONFIG"),
        ("left", "NAME"),
        ("left", "STRING", "NUMBER"),
        ("left", "ENDL"),
        ("left", "PYTHON"),
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

    def __lshift__(self, error: SATParserError):
        self.error_stack.push(error)

    def exit(self, code: int):
        raise SATExit(code)

    def interrupt(self):
        """"""
        while self.error_stack:
            stderr << self.error_stack.popleft()

        self.exit(EXIT_FAILURE)

    def checkpoint(self):
        """"""
        if self.error_stack:
            self.interrupt()

    @Timing.timer(level=DEBUG, section="Parser.parse")
    def parse(self, source: Source):
        ## Input
        self.source = source

        ## Initialize Lexer
        self.lexer = SATLexer(self.source)

        ## Initialize Parser
        self.parser = yacc.yacc(module=self, debug=False)

        ## Run Parser
        if not self.source:
            self << SATSyntaxError("Empty File.", target=self.source.eof)
        else:
            self.parser.parse(self.source)

        ## Checkpoint
        self.checkpoint()

        ## Output
        return self.bytecode

    def run(self, code: list):
        self.bytecode = [cmd for cmd in code if cmd is not None]

    def p_start(self, p):
        """\
        start : code
        """
        self.run(p[1])

    def p_code(self, p):
        """\
        code : code stmt
             | stmt
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_stmt(self, p):
        """\
        stmt : sys_config ENDL
             | def_constant ENDL
             | def_array ENDL
             | def_constraint ENDL
        """
        p[0] = p[1]

    def p_sys_config(self, p):
        """\
        sys_config : CONFIG NAME DOTS sys_config_args
        """
        name = p[2]
        args = p[4]
        p[0] = (SYS_CONFIG, name, args)

    def p_sys_config_args(self, p):
        """\
        sys_config_args : sys_config_args COMMA sys_config_arg
                        | sys_config_arg
        """
        if len(p) == 4:
            p[0] = [*p[1], p[3]]
        else:
            p[0] = [p[1]]

    def p_sys_config_arg(self, p):
        """\
        sys_config_arg : NUMBER
                       | STRING
        """
        p[0] = p[1]

    def p_def_constant(self, p):
        """\
        def_constant : varname ASSIGN expr
        """
        p[0] = (DEF_CONSTANT, p[1], p[3])

    def p_literal(self, p):
        """\
        literal : constant
                | varname
        """
        p[0] = p[1]

    def p_constant(self, p):
        """\
        constant : NUMBER
        """
        p[0] = p[1]

    def p_name(self, p):
        """\
        name : NAME
        """
        p[0] = String(p[1], source=self.source, lexpos=p.lexpos(1))

    def p_varname(self, p):
        """\
        varname : NAME
        """
        p[0] = Var(p[1], source=self.source, lexpos=p.lexpos(1))

    def p_def_array(self, p):
        """\
        def_array : varname shape ASSIGN array_buffer
                  | varname shape
        """
        name = p[1]
        shape = p[2]

        if len(p) == 5:  # array declared
            buffer, dense = p[4]
        else:  # implicit array
            buffer, dense = None, False

        p[0] = (DEF_ARRAY, name, shape, buffer, dense)

    def p_shape(self, p):
        """\
        shape : shape index
              | index
        """
        if len(p) == 3:
            p[0] = (*p[1], p[2])
        else:
            p[0] = (p[1],)

    def p_index(self, p):
        """\
        index : LBRA expr RBRA
        """
        p[0] = p[2]

    def p_array_buffer(self, p):
        """\
        array_buffer : dense_array_buffer
                     | sparse_array_buffer
        """
        p[0] = p[1]

    def p_dense_array_buffer(self, p):
        """\
        dense_array_buffer : LBRA dense_array RBRA
        """
        p[0] = (p[2], True)

    def p_sparse_array_buffer(self, p):
        """\
        sparse_array_buffer : LCUR sparse_array RCUR
        """
        p[0] = (p[2], False)

    def p_dense_array(self, p):
        """\
        dense_array : dense_array COMMA dense_array_item
                    | dense_array_item
                    | dense_array_buffer
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_dense_array_item(self, p):
        """\
        dense_array_item : expr
        """
        p[0] = p[1]

    def p_sparse_array(self, p):
        """\
        sparse_array : sparse_array COMMA sparse_array_item
                     | sparse_array_item
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_sparse_array_item(self, p):
        """\
        sparse_array_item : sparse_array_index DOTS expr
        """
        p[0] = (p[1], p[3])

    def p_array_index(self, p):
        """\
        sparse_array_index : LPAR expr_seq RPAR
        """
        p[0] = p[2]

    def p_expr_seq(self, p):
        """\
        expr_seq : expr_seq COMMA expr
                 | expr
        """
        if len(p) == 4:
            p[0] = (*p[1], p[3])
        else:
            p[0] = (p[1],)

    def p_def_constraint(self, p):
        """\
        def_constraint : LPAR name RPAR varname LBRA expr RBRA DOTS expr
                       | LPAR name RPAR varname DOTS expr
        """
        cons_type = p[2]
        cons_name = p[4]

        if len(p) == 10:
            level = p[6]
            expr = p[9]
        else:
            level = None
            expr = p[6]

        p[0] = (DEF_CONSTRAINT, cons_type, cons_name, expr, level)

    def p_loop(self, p):
        """\
        loop : quant LCUR varname ASSIGN domain COMMA conditions RCUR
             | quant LCUR varname ASSIGN domain RCUR
        """
        if len(p) == 9:
            p[0] = (p[1], p[3], p[5], p[7])
        else:
            p[0] = (p[1], p[3], p[5], None)

    def p_quant(self, p):
        """\
        quant : FORALL
              | EXISTS
              | UNIQUE
        """
        p[0] = p[1]

    def p_domain(self, p):
        """\
        domain : LBRA expr DOTS expr DOTS expr RBRA
               | LBRA expr DOTS expr RBRA
        """
        if len(p) == 8:
            p[0] = (p[2], p[4], p[6])
        else:
            p[0] = (p[2], p[4], None)

    def p_conditions(self, p):
        """\
        conditions : conditions COMMA condition
                   | condition
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_condition_expr(self, p):
        """\
        condition : expr
        """
        p[0] = p[1]

    def p_condition(self, p):
        """\
        expr : expr EQ expr
             | expr GT expr
             | expr LT expr
             | expr GE expr
             | expr LE expr
             | expr NE expr
        """
        p[0] = Expr(p[2], p[1], p[3], source=self.source, lexpos=p.lexpos(2))

    def p_expr(self, p):
        """\
        expr : literal
        """
        p[0] = p[1]

    def p_expr1(self, p):
        """\
        expr : NOT expr
             | ADD expr
             | SUB expr
        """
        p[0] = Expr(p[1], p[2], source=self.source, lexpos=p.lexpos(1))

    def p_expr2(self, p):
        """\
        expr : expr AND expr
             | expr OR expr
             | expr XOR expr
             | expr ADD expr
             | expr SUB expr
             | expr MUL expr
             | expr POW expr
             | expr DIV expr
             | expr MOD expr
             | expr IMP expr
             | expr RIMP expr
             | expr IFF expr
        """
        if p[2] == T_NEG:
            p[0] = Expr(
                T_ADD,
                p[1],
                Expr(T_NEG, p[3], source=self.source, lexpos=p.lexpos(2)),
                source=self.source,
                lexpos=p.lexpos(2),
            )
        else:
            p[0] = Expr(p[2], p[1], p[3], source=self.source, lexpos=p.lexpos(2))

    def p_expr_index(self, p):
        """\
        expr : expr LBRA expr RBRA
        """
        p[0] = Expr(T_IDX, p[1], p[3], source=self.source, lexpos=p.lexpos(2))

    def p_expr_par(self, p):
        """\
        expr : LPAR expr RPAR
        """
        p[0] = p[2]

    def p_expr_loop(self, p):
        """\
        expr : loop expr
        """
        p[0] = Expr(T_LOOP, p[1], p[2])

    def p_error(self, t):
        target = SATType()
        if t:
            target.lexinfo = self.source.getlex(t.lexpos)
            if hasattr(t, "string"):
                msg = f"Unexpected Token '{t.string}'"
            else:
                msg = f"Unexpected Token '{t.value}'"
        else:
            target = self.source.eof
            msg = "Unexpected End Of File"
        self << SATSyntaxError(msg=msg, target=target)
        return None

    def chrpos(self, lineno: int, lexpos: int):
        return lexpos - self.source.table[lineno - 1] + 1
