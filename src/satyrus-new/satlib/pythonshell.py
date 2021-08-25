class PythonError(Exception):
    ...

class PythonShell:

    def __init__(self):
        self.globals = {**globals()}

    def __call__(self, code: str, evaluate=False):
        if evaluate:
            try:
                bytecode = compile(code, '<pyshell>', 'eval')
                return eval(bytecode, globals=self.globals)
            except Exception as error:
                raise PythonError(*error.args)
        else:
            try:
                bytecode = compile(code, '<pyshell>', 'exec')
                return exec(bytecode, globals=self.globals)
            except Exception as error:
                raise PythonError(*error.args)

