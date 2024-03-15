import os, sys, unittest
from functools import partial
# 'src' directory must be in PYTHONPATH
from satyruslib.satparser import SATParser
from satyruslib.satexceptions import *
from satyruslib.sattypes import neuronalStruct

## Constants

test_dir = "/tmp/satyrus_unit_test"

## Global variables

open_fds = {}

## Aux functions

def create_test_dir():
  if not os.path.isdir(test_dir): 
    os.mkdir(test_dir)

def delete_test_dir():
  os.rmdir(test_dir)

def create_test_file(filename):
  absolut_path = os.path.join(test_dir, filename)
  if not os.path.isfile(absolut_path):
    open_fds[filename] = open(absolut_path, 'a')

def delete_test_file(filename):
  absolut_path = os.path.join(test_dir, filename)
  if open_fds.has_key(filename): 
    open_fds[filename].close()
  os.unlink(absolut_path)

def chmod_test_file(filename, mode):
  absolut_path = os.path.join(test_dir, filename)
  os.chmod(absolut_path, mode)

def get_test_struct(dims):
  bounds_check = lambda t: all(map(lambda x,y: 1<=x<=y, t, dims))
  return neuronalStruct(len(dims), bounds_check)

def get_parser():
  return SATParser(
                    ampl=True,
                    outfiles="out",
                    lower_bound=None,
                    simplify=False,
                    solver="cplex",
                    xpress=False
                  )

## Tests

class TestSATLexerError(unittest.TestCase):
  """Test lexer errors"""

  def setUp(self):
    self.parser = get_parser()
    self.test = partial(self.assertRaises, SATLexerError, self.parser.parse)

  def test_invalid_caracters(self):
    self.test("#")
    self.test("o$")
    self.test("%")
    self.test("e@")
    self.test("^")


class TestSATParseError(unittest.TestCase):
  """Test cases written to catch parsing errors"""

  def setUp(self):
    self.parser = get_parser()
    self.test = partial(self.assertRaises, SATParseError, self.parser.parse)

  def test_declarations(self):
    self.test("x = ")
    self.test("x == 1;")
    self.test("a = b(2);")
    self.test("a(2, 1,);")
    self.test("a(2); b fro \"foo\";")
    self.test("a(2); b from foo\";")

  def test_struct_definition(self):
    # XXX: this isn't pretty, but it's easy to implement. 
    # Please, pretty prealse, with sugar on top, write some better code anytime
    # soon
    struct = get_test_struct([4, 6])
    test_file = os.tmpfile()

    test_file.write('1*,9')
    test_file.seek(0)
    self.assertRaises(SATParseError, self.parser.read_struct_from_file, 
        struct, test_file, 1)
    
    test_file.seek(0)
    test_file.write('0,1=1')
    test_file.seek(0)
    self.assertRaises(SATValueError, self.parser.read_struct_from_file, 
        struct, test_file, 1)

    test_file.seek(0)
    test_file.write('1,1=-1')
    test_file.seek(0)
    self.assertRaises(SATValueError, self.parser.read_struct_from_file, 
        struct, test_file, 1)


  def test_eof(self):
    self.test("a(2)")
    self.test("a(2); intgroup i1")
    self.test("a(2); intgroup i1: a[1]")
    self.test("a(2); intgroup i1: a[1]; optgroup o1: a[2]")
    self.test("a(2); intgroup i1: a[1]; optgroup o1: a[2]; penalties")
    self.test("a(2); intgroup i1: a[1]; optgroup o1: a[2]; penalties: i1 level")
    self.test("a(2); intgroup i1: a[1]; penalties: i1 level 0")
    #self.failUnless(self.parser.parse(
    #    "a(2); intgroup i1: a[1]; optgroup o1: a[2]; penalties: i1 level 0;"))


class TestSATNameError(unittest.TestCase):
  """Tests for SATNameErros, such as undefined symbols"""

  def setUp(self):
    self.parser = get_parser()
    self.test = partial(self.assertRaises, SATNameError, self.parser.parse)

  def test_declarations(self):
    self.test("x = y;")
    self.test("x = y + 1;")
    self.test("x = x;")
    self.test("x = 4 - x;")
    self.test("a(x);")
    self.test("a(2, x);")
    self.test("a(2); b from \"foo\";")
    self.test("a(b); b from \"foo\";")

  def test_constraints(self):
    # FIXME
    #self.test("a(2); intgroup i1: forall{i} where j in (1, 3): a[1]")
    self.test("a(2); intgroup i1: forall{i} where i in (1, 2): (a[1] or b[j])")

  def test_penalties(self):
    self.test("a = 1; intgroup i1: a; penalties: i2 level 0;")


class TestSATTypeError(unittest.TestCase):

  def setUp(self):
    self.parser = get_parser()
    self.test = partial(self.assertRaises, SATTypeError, self.parser.parse)

  def test_declarations(self):
    self.test("a(2); b = a;")
    self.test("a(2); b(a);")
    self.test("a(2); b(3, a);")
    self.test("a = 1; b(1); a from \"foo\";")

  def test_constraints(self):
    self.test("a = 1; intgroup i0: a[1];")
    self.test("a(1); intgroup i0: a;")
    self.test("""a(1); b(1); intgroup i0: forall{i} where i in (1, 4+b): a[1];
      penalties: i0 level 0;""")

  def test_penalties(self):
    self.test("a = 1; penalties: a level 0;")
    self.test("a(1); penalties: a level 0;")


class TestSATIOError(unittest.TestCase):

  def setUp(self):
    self.parser = get_parser()
    self.test = partial(self.assertRaises, SATIOError, self.parser.parse)

    create_test_dir()

    self.test_file = 'foo'
    create_test_file(self.test_file)
    chmod_test_file(self.test_file, 0100)

  def test_declarations(self):
    # this test will fail if there's a '/tmp/vsdfvdsbg' file :-P
    self.test("b(1); b from \"/tmp/vsdfvdsbg\";")
    self.test("b(1); b from \"%s\";" % self.test_file)

  def tearDown(self):
    delete_test_file(self.test_file)
    delete_test_dir()

class TestSATValueError(unittest.TestCase):

  def setUp(self):
    self.parser = get_parser()
    self.test = partial(self.assertRaises, SATValueError, self.parser.parse)

  def test_declarations(self):
    self.test("a(-2);")
    self.test("a(2, -1, 4);")
    self.test("a(2, 1, -4);")

  def test_constraints(self):
    self.test("a(2); intgroup i1: a[1][1];")
    self.test("a(2); intgroup i1: a[1][1][1];")
    self.test("a(2); b(2); intgroup i0: a[b]; penalties: i0 level 0;")
    # XXX to avoid generating a new parser everytime a self.test runs,
    # we use the same penalties identifiers for every test
    self.test("""a(2); intgroup i0: forall{i,j} where j in (1, 3): a[i];
      penalties: i0 level 0;""")
    self.test("""a(2); intgroup i0: forall{i} where i in (1, 3): a[j]; 
        penalties: i0 level 0;""")

if __name__ == "__main__":
  unittest.main()
