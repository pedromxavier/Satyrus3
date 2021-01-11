import types
from operator import add, mul

# Introduced in python 2.6, module itertools
def product(*args, **kwds):
  # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
  # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
  pools = map(tuple, args) * kwds.get('repeat', 1)
  result = [[]]
  for pool in pools:
    result = [x+[y] for x in result for y in pool]
  for prod in result:
    yield tuple(prod)

def default(x, y, f=None):
  """If y is not None, returns y if f is None, otherwise returns f(y). If y is
  None, returns x.
  >>> default(1, None, None)
  1
  >>> default(1, 5, None)
  5
  >>> default(1, 5, lambda x: x + 1)
  6
  """
  if y:
    if f:
      return f(y)
    else:
      return y
  else:
    return x

def prod(seq=[]):
  """[x1, x2, x3, ..., xn] -> x1 * x2 * x3 * ... * xn
  >>> prod([1,2,3,4,5])
  120
  >>> prod()
  1
  """
  return reduce(mul, seq, 1)

def one_minus(x):
  """x -> 1 - x
  >>> one_minus(0)
  1
  >>> one_minus(4)
  -3
  """
  return 1 - x

def get_outfile(file):
  try:
    # XXX: is this windows compatible?
    return open(file, 'w')
  except:
    sys.exit("Error: can't open %s for writing: %s" % (file, 
      sys.exc_info()[1]))

def lcm(*args):
  """Least commom multiple of a n-uple of integers
  >>> lcm(1,2,3)
  6
  >>> lcm(4,8)
  8
  >>> lcm(10,4,20)
  20
  """
  sum = args[0]
  while any(map(lambda x: sum % x != 0, args)):
    sum += args[0]
  return sum

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  #a = [xrange(10), xrange(4)]
  #for i in product(*a):
  #  print i
