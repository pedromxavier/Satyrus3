import string, types, sys
from operator import and_, invert
from satexceptions import *

class neuronalStruct(dict):
  """Structs of neurons"""

  def __init__(self, ndimensions, bounds_check):
    assert ndimensions > 0
    assert bounds_check.__class__ is types.FunctionType
    self.ndimensions = ndimensions
    self.bounds_check = bounds_check
    self.default = None
    self.initialized = False

  def set_mapping(self, mapping_list):
    for key, value, lineno in mapping_list:
      if len(key) != self.ndimensions:
        raise SATValueError(lineno, "invalid index: " + str(key))
      elif self.bounds_check(key):
        self[key] = value
      else:
        raise SATValueError(lineno, "index out of bounds: " + str(key))

  def __missing__(self, k):
    return None

class atom(object):
  """Instances of this class represent particular points inside a 
  neuronalStruct."""

  def __init__(self, name, lineno, indexes=None):
    assert isinstance(name, str)
    self.name = name
    self.lineno = lineno
    self.indexes = indexes[:] if indexes else None
    self.context = {}
    self.index_map = []

  def __repr__(self):
    if self.index_map:
      return self.name + ''.join(map(lambda i: '[%s]' % i, self.index_map))
    else:
      return self.name

  def __str__(self):
    if self.index_map:
      return self.name + '_' + '_'.join(map(lambda i: str(i), self.index_map))
    else:
      return self.name

  def copy(self):
    new_atom = atom(self.name, self.lineno, self.indexes)
    new_atom.context = self.context.copy()
    return new_atom

  def update_context(self, context):
    self.context.update(context) 

  def eval_index(self):
    try:
      for idx in self.indexes:
        if isinstance(idx, str):
          i = eval(idx, self.context, {})
          if isinstance(i, int):
            self.index_map.append(i)
          else:
            raise SATTypeError(line = self.lineno, name = str(i), 
                msg = "indexes must be integers")
    except NameError:
      raise SATValueError(self.lineno, "%s: unbound atom" % repr(self))
    return tuple(self.index_map)

class penalty():
  def __init__(self, id, level, correlation):
    assert isinstance(id, str)
    assert isinstance(level, int) 
    assert isinstance(correlation, int)
    self.id = id
    self.level = level
    self.correlation = correlation

  def __repr__(self):
    return "(%s, %d, %d)" % (self.id, self.level, self.weight)
 
if __name__ == "__main__":
  a = atom('foo', ['x', 'y-1'])
  a.eval('x', 10)
  print a
  a.eval('y', 5)
  print a
