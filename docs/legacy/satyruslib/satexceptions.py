from satutils import default

# TODO: i don't need all this damn exceptions

class SATError(Exception):
  """All kinds of exceptions raised by the SATParser module"""
  
  def __init__(self, line, msg):
    self.msg = msg
    self.line = line

  def __str__(self):
    return "line %d: " % self.line + self.msg

class SATLexerError(SATError):
  """Exception raised for lexer errors"""

  def __init__(self, line, msg):
    self.msg = msg
    self.line = line

  def __str__(self):
    return "line %d: " % self.line + self.msg

class SATParseError(SATError):
  """Exception raised for all parse errors"""
  
  def __init__(self, **kwargs):
    if kwargs.has_key('msg'):
      self.msg = kwargs['msg']
    elif kwargs.has_key('file'):
      self.msg = "file %s: syntax error" % kwargs['file']
    else:
      self.msg = "syntax error in input file"
    
    if kwargs.has_key('line'):
      self.msg += ", at line %d" % kwargs['line']

    if kwargs.has_key('column'):
      self.msg += ", at column %d" % kwargs['column']

  def __str__(self):
    return self.msg

class SATNameError(SATError):
  """Exception raised when an undefined name is found"""

  def __init__(self, **kwargs):
    line = kwargs['line']
    if kwargs.has_key('msg'):
      self.msg = "line %d: %s" % (line, kwargs['msg'])
    else:
      name = kwargs['name']
      self.msg = "line %d: name '%s' is not defined" % (line, name)

  def __str__(self):
    return self.msg

class SATTypeError(SATError):
  """Exception raised when types don't match"""

  def __init__(self, line, name=None, **kwargs): 
    self.line = line
    self.name = " %s:" % name if name else ""
    if kwargs.has_key('msg'):
      self.msg = kwargs['msg']
    elif kwargs.has_key('expected_type'):
      self.msg = "should be of type " + kwargs['expected_type']
    elif kwargs.has_key('expected_types'):
      self.msg = "should be of one of this types: " + ', '.join(
          kwargs['expected_types'])
    else:
      assert False

  def __str__(self):
    return "line %d:%s " % (self.line, self.name) + self.msg

class SATIOError(SATError):
  """Exception raised when an IO operation fails"""

  def __init__(self, line, msg):
    self.msg = msg
    self.line = line

  def __str__(self):
    return "line %d: " % self.line + self.msg

class SATValueError(SATError):
  """Exception raised when an unexpected value is found. A negative index, for
  instance"""

  def __init__(self, line, msg, file=None):
    self.line = line
    self.msg = msg
    self.file = file

  def __str__(self):
    return "%sline: %d: %s" % (default(
      "", self.file, lambda x: "file: %s, " % x), self.line, self.msg)

class SATImportError(SATError):
  """Exception raised when a required lib is not found"""

  def __init__(self, lib):
    self.lib = lib

  def __str__(self):
    return "In order to run SATyrus, you must install %s." % self.lib

if __name__ == "__main__":
  print SATImportError("python-ply")
