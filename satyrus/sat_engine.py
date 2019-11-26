from sat_errors import *;
from sat_parser import *;

class Engine(object):
    ''' Engine Prototype
    '''

    __ref__ = None

    def __new__(cls, lexer, parser):
        if cls.__ref__ is None:
            obj = object.__new__(cls)
            Engine.__init__(obj, lexer, parser)
            cls.__ref__ = obj
        return cls.__ref__

    def __init__(engine, lexer, parser):
        engine.memory = {};

        engine.lexer = lexer;
        engine.lexer.t_error.error = Engine.T_ERROR;

        engine.parser = parser;
        engine.parser.p_run.run = Engine.P_RUN;
        engine.parser.p_error.error = Engine.P_ERROR;

        engine.code = None;

    @staticmethod
    def T_ERROR(t):
        ...

    @staticmethod
    def P_ERROR(p):
        ...

    @staticmethod
    def P_RUN(code : list):
        if Engine.__ref__ is None:
            raise SatCompilation_Error("Engine was not instantiated.");
        else:
            Engine.__ref__.run(code);

    def __lshift__(engine, source : str):
        try:
            engine.parse(source)
        except SatError as error:
            stderr << error.msg
            return
        except Exception as error:
            raise error

    def run(engine, code : list):
        engine.code = code;
        engine.compile();
        engine.execute();
        engine.code = None;

    def parse(engine, code : str):
        engine.parser.parse(code)

    def compile(engine):
        if engine.code is not None:
            engine.code = [stmt.compile(engine) for stmt in engine.code]
        else:
            raise SatCompilation_Error("code is none.")

    def execute(engine):
        if engine.code is not None:
            engine.code = [stmt.execute(engine) for stmt in engine.code]
        else:
            raise SatCompilation_Error("code is none.")

    def eval(engine, value, types=None):
        if type(value) is Var:
            value = engine.read_memory(value)

        if types is None or type(value) in types:
            return value

        else:
            error_msg = ERROR_MSGS['Engine.eval'][0].format(type(value))
            raise SatType_Error(error_msg)

    def read_memory(engine, name):
        if name in engine.memory:
            return engine.memory[name]
        else:
            error_msg = ERROR_MSGS['Engine.read_memory'][0].format(name)
            raise SatName_Error(error_msg)

engine = Engine(lexer, parser);
