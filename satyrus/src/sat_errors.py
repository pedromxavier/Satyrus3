class Error(BaseException):
    ''' Critical Error to be Logged.
    '''
    def __init__(self, msg=None):
        BaseException.__init__(self, msg)
        self.msg = f"\n{msg}" if msg is not None else ""

    def __str__(self):
        return f"Critical Error :({self.msg}"

class SatError(BaseException):

    def __init__(self, msg=None):
        BaseException.__init__(self, msg)

        if msg is None:
            msg = "."
        else:
            msg = f":\n{msg}."

        self.msg = f"{self.__class__.__name__[3:].replace('_',' ')}{msg}"

    def __str__(self):
        return self.msg

class SatCompilation_Error(SatError):
    ...

class SatSyntax_Error(SatError):

    def __init__(self, msg=None):
        SatError.__init__(self, msg)

        if msg is None:
            msg = ""
        else:
            msg = f" {msg}"

        self.msg = f"{self.__class__.__name__[3:].replace('_',' ')}{msg}"

class SatInvalid_Token(SatError):

    def __init__(self, msg=None):
        SatError.__init__(self, msg)

        if msg is None:
            msg = ""
        else:
            msg = f" {msg}"

        self.msg = f"{self.__class__.__name__[3:].replace('_',' ')}{msg}"

class SatIndex_Error(SatError):
    ...

class SatName_Error(SatError):
    ...

class SatType_Error(SatError):
    ...

ERROR_MSGS = {
    'Expr.__getitem__' : [
        "Expression Indexes must have the form {'i':0, 'j':1, ...}",
        ],

    'Stmt.c_array' : [
        "Array dimensions must be integers",
        "Array indices must be integers",
    ],

    'Engine.eval' : [
        "Inconsistent type '{}'",
    ],

    'Engine.read_memory' : [
        "Name '{}' is not defined",
    ],

    'Stmt.c_config' : [
        "Float precision must be specified as an integer",
        "Unreachable directory {}",
        'Path specification must be string as in "C:/Users/..."',
        "Unkown environment variable '{}'",
    ],
}
