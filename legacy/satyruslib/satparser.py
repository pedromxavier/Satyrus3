#!/usr/bin/python

import os, re, sys
from functools import partial
from operator import eq, ne, itemgetter
from os.path import splitext
from satexceptions import *
from sattypes import *
try:
  from ply import lex, yacc
except ImportError:
  raise SATImportError("python-ply")
import satlexer
from satutils import *
from aima_python.logic import Expr as Formula, to_cnf, eliminate_disjunctions
from ampl import AmplInterface
from xpress import XpressInterface

def instantiate(quantifier, domain, formulae, context):
  """Given a domain of values, this function generates all possible formulas 
  that can be generated by binding the indexes inside the original formula 
  with values on the domain"""

  indexes = '{'
  bounds = ''
  assts = ''

  intervs = domain[0]
  if len(domain) == 2:
    asserts = domain[1]
  else:
    asserts = None

  for t in intervs:
    indexes += "\'%s\':%s," % (t[0], t[0])
    bounds += " for %s in range(%s,%s) " % (t[0], t[1], t[2] + '+1') 
    # FIXME fuck, this is horrible. seriously, that '+1' is shit
    # please, PLEASE, fix that

  if asserts:
    for t in asserts:
      assts += "if %s %s %s " % (t[0], t[1], t[2])

  indexes = indexes.rstrip(',') + '}'
  expr = '(' + indexes + bounds + assts + ')'

  indexes = eval(expr, context)
  form_list = map(lambda i: formulae.instantiate(i), indexes)

  if len(form_list) == 0:
    return None
  elif len(form_list) == 1:
    return form_list[0]
  else:
    op = '|' if quantifier == 'forall' else '&'
    return Formula(op, *form_list)

class Parser(object):
  """Base class for the SATyrus parser."""

  tokens = ()
  precedence = ()

  def __init__(self, **kwargs):
    # symbol table
    self.symbols = {}

    # penalty levels 
    self.penalties = {}
    self.penalty_values = {}
    self.penalty2level = {}
    self.known_penalty_ids = set()

    # string of data to parse. Usually, this is the whole content of a file
    self.data = kwargs.get('data', "")

    # output file
    self.outfiles = kwargs['outfiles']

    # output 
    self.ampl   = kwargs['ampl']
    self.xpress = kwargs['xpress']

    # penalties lower bound
    self.lower_bound = kwargs['lower_bound']

    # simplify energy function
    self.simplify = kwargs['simplify']

    # solver used to solve the energy function
    self.solver = kwargs['solver']

    modname = os.path.split(os.path.splitext(__file__)[0])[1]
    self.tabmodule = modname + "_tab"

    # build the lexer
    self.lexer = lex.lex(module=satlexer)

    # build the parser
    self.parser = yacc.yacc(module=self, tabmodule=self.tabmodule)
    self.has_wta = False

  def get_column(self, p):
    return satlexer.get_column(self.data, p)

  def parse(self, data=None):
    if data: self.data = data
    return self.parser.parse(self.data)


class SATParser(Parser):
  """The parser of SATyrus."""

  precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),

    ('left', 'LI', 'RI'),
    ('left', 'EQV'),
    ('left', 'AND', 'OR'),
    ('right', 'NOT'),
  )

  from satlexer import tokens

  def read_struct_from_file(self, s, fd, line):
    rx_int = re.compile('^(0|[1-9]\d*)$')
    d = s.ndimensions
    filename = fd.name
    for lineno, line in enumerate(fd.readlines()):
      tokens = re.split(r',|=', line.strip('\n').replace(' ',''))
      if len(tokens) != d+1:
        raise SATParseError(line = lineno+1, file=filename)
      else:
        neuron = tokens.pop()
        if not re.match(rx_int, neuron):
          raise SATValueError(lineno + 1, 
              "neuron value must be a positive integer", filename)
        if filter(lambda tok: not re.match(rx_int, tok), tokens):
          raise SATValueError(
              lineno+1, "index value must be a positive integer", filename)
        # XXX: do i need to worry about an exception here?
        key = tuple(map(int, tokens))
        if not s.bounds_check(tokens):
          raise SATValueError(lineno+1, "index out of bounds", filename)
        s[key] = int(neuron)    
    fd.close()

  def eval_expr(self, expr, lineno):
    try:
      return eval(expr, self.symbols)
    except NameError, exn:
      raise SATNameError(line = lineno, msg = str(exn))

  def int_or_str_atom(self, atom):
    if isinstance(atom, int):
      return atom
    s = self.symbols[atom.name]
    if isinstance(s, int):
      return s
    x = s[atom.eval_index()]
    if x is None:
      return str(atom)
    else:
      return x

  def to_energy_function(self, s):
    """Returns a tuple of strings: the arguments of the energy function and the 
    actual function."""
    #assert isinstance(s, Formula)

    # base case
    if len(s.args) == 0:
      x = self.int_or_str_atom(s.op)
      if isinstance(x, int):
        return [], str(x)
      else:
        return [x], x

    # inductive step
    if s.op == '~':
      assert len(s.args) == 1
      args, ops = self.to_energy_function(s.args[0])
      return args, '(1 - %s)' % ops

    if s.op == '&':
      op = '*'
    elif s.op == '|':
      op = '+'
    else:
      assert False

    args = set()
    ops = '('

    for new_args, new_ops in map(self.to_energy_function, s.args):
      for a in new_args: args.add(a)
      ops += '%s %s ' % (new_ops, op)

    ops = ops.rstrip('%s ' % op) + ')'

    return args, ops

  def to_simplifyed_energy_function(self, s):
    #assert isinstance(s, Formula)

    # base case
    if len(s.args) == 0:
      x = self.int_or_str_atom(s.op)
      if isinstance(x, int):
        return [], x
      else:
        return [x], Symbol(x)

    # inductive step
    if s.op == '~':
      assert len(s.args) == 1
      args, ops = self.to_simplifyed_energy_function(s.args[0])
      return args, one_minus(ops)

    if s.op == '&':
      operation = prod
    elif s.op == '|':
      operation = sum
    else:
      assert False

    args = set()
    ops = []

    for new_args, new_ops in map(self.to_simplifyed_energy_function, s.args):
      args.update(new_args)
      ops.append(new_ops)

    return args, operation(ops)

  def eval_penalties(self, line, pid2coeffs, pid2nclauses):
    # sort the levels
    levels = sorted(self.penalties)

    # evaluate the weights
    weights_by_level = {}
    weights_by_penalty = {}
    for level, penaltylist in self.penalties.iteritems():
      corrlist = map(lambda p: p.correlation, penaltylist)
      max_weight = lcm(*corrlist)
      weights_by_level[level] = max_weight
      for p in penaltylist:
        weights_by_penalty[p.id] = max_weight / p.correlation

    # evaluate the coefficients
    coefficients = {}
    for pid, coef in pid2coeffs.iteritems():
      level = self.penalty2level[pid]
      if level in coefficients:
        curr_max_coeff = coefficients[level]
        coefficients[level] = max(pid2coeffs[pid], curr_max_coeff)
      else:
        coefficients[level] = pid2coeffs[pid]

    # evaluate the number of clauses
    nclauses = {}
    for pid, nc in pid2nclauses.iteritems():
      level = self.penalty2level[pid]
      if level in nclauses:
        nclauses[level] += nc
      else:
        nclauses[level] = nc

    # do the shit
    level0 = levels[0]
    penalties_by_level = {}

    if self.lower_bound:
      beta0 = self.lower_bound
    else:
      beta0 = max(1, coefficients[level0])

    penalties_by_level[level0] = beta0
    for penalty in self.penalties[level0]:
      pweight = weights_by_penalty[penalty.id]
      self.penalty_values[penalty.id] = pweight * beta0

    if len(levels) == 1:
      return

    # XXX: should epsilon be a command line argument?
    epsilon = 1e-6

    level1 = levels[1]
    base = nclauses[level0] * beta0
    penalties_by_level[level1] = base + epsilon
    for penalty in self.penalties[level1]:
      pweight = weights_by_penalty[penalty.id]
      self.penalty_values[penalty.id] = pweight * base + epsilon

    for i in range(2, len(levels)): 
      prev_level = levels[i-1]
      prev_weight = weights_by_level[prev_level]
      prev_penalty = penalties_by_level[prev_level]
      base += nclauses[prev_level] * prev_penalty * coefficients[prev_level] *\
          prev_weight
      curr_level = levels[i]

      penalties_by_level[curr_level] = base + epsilon
      for penalty in self.penalties[curr_level]:
        pweight = weights_by_penalty[penalty.id]
        self.penalty_values[penalty.id] = pweight * base + epsilon

  ############################### Parsing ###################################

  #_______________________________ S _______________________________________#
  def p_program(self, p):
    '''program : listdefinition listconstraint penalties'''

    constraints = []
    n_clauses = {}
    max_coefficient = {}

    ## getting clauses ##
    for penalty_group, penalty_id, quantifiers, formulae, lineno in p[2]:

      if penalty_group == "intgroup":
        # XXX
        #if self.has_wta and penalty_id != "wta":
        #  eliminate_disjunctions(formulae)
        clauses = to_cnf(~formulae)
      else:
        clauses = to_cnf(formulae)

      # instantiate the free variables
      try:
        if quantifiers:
          for quantifier, domain in quantifiers:
            clauses = instantiate(quantifier, domain, clauses, self.symbols)
        # else: 
          # nothing to instantiate
      except NameError, exn:
        raise SATNameError(line = lineno, msg = str(exn))
      except TypeError, exn:
        raise SATTypeError(line = lineno, msg = str(exn))

      # Getting number of clauses
      if clauses is not None:
        number_of_clauses = len(clauses.args)
        candidate_max_coef = 1 # XXX: for now, max_coefficient isn't used
      else:
        # no clause was generated
        number_of_clauses = 0
        candidate_max_coef = 0

      # TODO: ask priscila about n_clauses. 
      # number_of_clauses after == number_of_clauses before instantiate?

      # update number of clauses at level p
      try:
        n_clauses[penalty_id] += number_of_clauses
      except KeyError:
        n_clauses[penalty_id] = number_of_clauses
      
      # update maximum coefficient at level p
      try:
        curr_max_coef = max_coefficient[penalty_id]
        max_coefficient[penalty_id] = max(curr_max_coef, candidate_max_coef)
      except KeyError:
        max_coefficient[penalty_id] = candidate_max_coef

      constraints.append((penalty_id, clauses))


    ## computing the penalties ##
    self.eval_penalties(p[3], max_coefficient, n_clauses)

    ## generating the energy function ##
    arguments = set()
    
    if self.simplify:
      from sympy import Symbol
      global Symbol
      terms = []
      for group, formulae in constraints:
        penalty = self.penalty_values[group]
        args, term = self.to_simplifyed_energy_function(formulae)
        arguments = arguments.union(args)
        terms.append(penalty * term)
      
      equation = sum(terms)
    else:
      equation = ""
      for group, formulae in constraints:
        penalty = self.penalty_values[group]
        args, term = self.to_energy_function(formulae)
        arguments = arguments.union(args)
        equation += "%f * (%s) + " % (penalty, term)
      
      equation = equation.rstrip("+ ")

    if self.ampl:
      ampl = AmplInterface(arguments, equation, self.solver)
      ampl.write(self.outfiles)
    
    if self.xpress:
      # TODO model name
      xpress = XpressInterface(arguments, equation)
      xpress.write(self.outfiles)

  #____________________________ Definitions ________________________________#

  # this list contruction is totally stoled from BNFC's strategy of building 
  # lists ( http://www.cs.chalmers.se/Cs/Research/Language-technology/BNFC/ )
  def p_listdefinition(self, p):
    '''listdefinition : empty
                       | listdefinition definition ";" '''
    if p[1] is None:
      p[0] = []
    else:
      p[1].append(p[2])
      p[0] = p[1]

  # scalar variables
  def p_expr_assignment(self, p):
    '''definition : IDENT '=' expr'''
    expr = self.eval_expr(p[3], p.lineno(2))
    if not isinstance(expr, int):
      raise SATTypeError(p.lineno(2), p[1], expected_type = 'int')
    self.symbols[p[1]] = expr

  # non-scalar variables
  def p_struct_definition(self, p):
    '''definition : IDENT '(' dimensions ')' '''
    # This is not actually pretty. I'm handling this error here to avoid
    # tracking position information on all grammar symbols
    if isinstance(p[3][0], str): 
      exn_type, exn_msg = p[3]
      lineno = p.lineno(2)
      if exn_type == "name_error":
        raise SATNameError(line = lineno, msg = exn_msg)
      elif exn_type == "value_error":
        raise SATValueError(line = lineno, msg = exn_msg)
      else:
        raise SATTypeError(line = lineno, msg = exn_msg)

    ndims, bounds_check = p[3]
    self.symbols[p[1]] = neuronalStruct(ndims, bounds_check) 

  def p_expr_dimensions(self, p):
    '''dimensions : listexpr''' 
    dims = []
    # Propagate error message when something goes wrong while parsing listexpr
    try:
      for expr in p[1]:
        d = eval(expr, self.symbols)
        if not isinstance(d, int):
          p[0] = "type_error", "dimensions must be positive integers"; return
        elif d <= 0:
          p[0] = "value_error", "dimensions must be positive integers"; return
        dims.append(d) 
    except NameError, exn:
      p[0] = "name_error", str(exn); return

    # Here is where functional programming takes control. 'dimensions' is a 
    # list of the form [ exp1, exp2, ..., expn ] where each expression is 
    # either an integer or a scalar variable. We want to build a function f 
    # that takes a tuple of indexes as argument and check if the indexes are 
    # valid ones. By valid we mean: if dimensions = [ dim1, dim2, ..., dimn ]
    # and indexes = [ i1, i2, ..., in ], then 
    # 1 <= i1 <= dim1 and 1 <= i2 <= dim2 and ... and 1 <= idxn <= dimn  
    # must be satisfied

    def check_dimensions(t):
      # t is a list of indexes. Fist of all, the number of indexes must be
      # equal to the number of dimensions
      assert len(t) == len(dims)

      # This is a little more tricky. For a tuple 't' of indexes and a list 
      # 'dims' of dimensions, we want to check if 1 <= t_i <= dims_i , for 
      # every 1 <= i <= len(t) (note that len (t) = len(dims)).
      # 'lambda x,y: 1 <= x <= y' creates a function that takes two arguments 
      # and checks if 1 <= x <= y; therefore, 
      # map(lambda x,y: 1 <= x <= y, t, dims) results in a list of the form 
      return all(map(lambda x,y: 1 <= x <= y, t, dims))

    # returns a tuple composed by the number of dimensions and a function that
    # checks if a tuple of indexes is valid
    p[0] = len(dims), check_dimensions

  def p_interv_dimensions(self, p):
    '''dimensions : domain'''

    ranges, asserts = p[1] 

    aux0 = ','.join(map(lambda r: r[0], ranges))
    aux1 = ' and '.join(map(lambda r: '(%s<=%s<%s)' % (r[1],r[0],r[2]), ranges))
    aux2 = ' and '.join(map(lambda a: '(%s%s%s)' % (a[0], a[1], a[2]), asserts))
    if aux2:
      tst = "lambda %s: %s and %s" % (aux0, aux1, aux2)
    else:
      tst = "lambda %s: %s" % (aux0, aux1)
    try:
      return eval(tst, self.symbols)
    except NameError, exn:
      p[0] = str(exn)

  def p_domain(self, p):
    '''domain : listinterval
              | listinterval AND listassertion'''
    if len(p) == 2:
      p[0] = p[1],   []
    else:
      p[0] = p[1], p[3]

  def p_listinterval(self, p):
    '''listinterval : interval
                    | listinterval ',' interval'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  def p_interval(self, p):
    '''interval : IDENT IN '(' expr ',' expr ')' '''
    p[0] = p[1], p[4], p[6]

  def p_listassertion(self, p):
    '''listassertion : assertion
                     | listassertion ',' assertion'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  def p_assertion(self, p):
    '''assertion : expr EQ expr
                 | expr NOTEQ expr
                 | expr LT expr
                 | expr LE expr
                 | expr GT expr
                 | expr GE expr'''
    p[0] = p[1], p[2], p[3]

  def p_struct_init(self, p):
    '''definition : IDENT '=' struct_body
                  | IDENT FROM STRING'''
    try:
      s = self.symbols[p[1]]
    except LookupError:
      raise SATNameError(line = p.lineno(1), name = p[1])
    if not isinstance(s, neuronalStruct):
      raise SATTypeError(p.lineno(1), p[1], 
          expected_type = neuronalStruct.__name__)

    if p[2] == '=': 
      s.set_mapping(p[3])
    else:
      try:
        fd = open(p[3], 'r')
      except:
        raise SATIOError(p.lineno(1), 
            "can't open \'%s\' for reading: %s" % (p[3], sys.exc_info()[1]))
      else:
        self.read_struct_from_file(s, fd, p.lineno(3))

  def p_struct_body(self, p):
    '''struct_body : '[' listmapping ']' '''
    p[0] = p[2]

  def p_listmapping(self, p):
    '''listmapping : mapping
                   | listmapping ";" mapping'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  def p_mapping(self, p):
    '''mapping : key ':' INTEGER'''
    p[0] = tuple(p[1]), p[3], p.lineno(2)

  def p_key(self, p):
    '''key : listinteger
           | "(" listinteger ")" '''
    p[0] = p[1] if len(p) == 2 else p[2]

  def p_listinteger(self, p):
    '''listinteger : INTEGER
                   | listinteger "," INTEGER'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  # _____________________________ Constraints ______________________________# 
  def p_listconstraint(self, p):
    '''listconstraint : empty 
                      | listconstraint constraint ";" '''
    if p[1] is None:
      p[0] = []
    else:
      p[1].append(p[2])
      p[0] = p[1]

  def p_constraint(self, p):
    '''constraint : INTGROUP IDENT ":" constraintRHS
                  | OPTGROUP IDENT ":" constraintRHS'''
    penalty_group = p[1]
    penalty_id = p[2]

    if penalty_id == 'wta':
      if penalty_group == 'optgroup':
        raise SATValueError(p.lineno(2), "optimality constraints can't be WTAs")
      else:
        self.has_wta = True

    self.known_penalty_ids.add(penalty_id)

    domain, lineno, formulae = p[4]
    
    p[0] = penalty_group, penalty_id, domain, formulae, lineno

  def p_constraintRHS(self, p):
    '''constraintRHS : quantifiers formulae'''
    p[0] = p[1][0], p[1][1], p[2]

  def p_quantifiers(self, p):
    '''quantifiers : empty
                   | listquantifier ':' '''
    lineno = p.lineno(2) if len(p) == 3 else None
    p[0] = p[1], lineno

  def p_listquantifier(self, p):
    '''listquantifier : quantifier
                      | listquantifier ';' quantifier'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  def p_quantifier(self, p):
    '''quantifier : FORALL '{' listident '}' WHERE domain
                  | EXISTS '{' listident '}' WHERE domain'''
    p[0] = p[1], p[6]

  def p_listident(self, p):
    '''listident : IDENT
                 | listident ',' IDENT'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  def p_formulae(self, p):
    '''formulae : wwf 
                | INTEGER "(" wwf ")"
                | atom "(" wwf ")" '''
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = Formula(p[1]) & p[3]

  def p_binary_wwf(self, p):
    '''wwf : wwf OR wwf
           | wwf AND wwf
           | wwf LI wwf
           | wwf RI wwf
           | wwf EQV wwf'''
    if p[2] == 'or':
      p[0] = p[1] | p[3]
    elif p[2] == 'and':
      p[0] = p[1] & p[3]
    elif p[2] == '->':
      p[0] = p[1] >> p[3]
    elif p[2] == '<-':
      p[0] = p[1] << p[3]
    elif p[2] == '<->':
      p[0] = p[1] % p[3]
    else:
      assert false

  def p_unary_wwf(self, p):
    '''wwf : NOT wwf'''
    p[0] = ~p[2]

  def p_ident_wwf(self, p):
    '''wwf : atom'''
    p[0] = Formula(p[1])

  def p_wwf_group(self, p):
    '''wwf : "(" wwf ")" '''
    p[0] = p[2]

  def p_atom(self, p):
    '''atom : IDENT
            | IDENT listindex'''
    try:
      # check the symbol table
      s = self.symbols[p[1]]
      if isinstance(s, int):
        if len(p) == 2:
          # if it is a scalar, create an atom
          p[0] = atom(p[1], p.lineno(1))
        else:
          raise SATTypeError(p.lineno(1), p[1], 
              msg = "int variable is unsubscriptable")
      elif isinstance(s, neuronalStruct):
        # it has a list of indexes?
        if len(p) == 3:
          # yes. We then check if the number of indexes equals the number of 
          # dimensions of the respective neuronalStruct
          if len(p[2]) == s.ndimensions:
            # everything is fine, so we create an atom
            p[0] = atom(p[1], p.lineno(1), p[2])
          else:
            # wrong number of dimensions
            raise SATValueError(p.lineno(1), 
                "Wrong number of dimensions for struct \'%s\'" % p[1])
        else:
          # it hasn't a list of indexes, so we raise an exception complaining
          # about that
          raise SATTypeError(p.lineno(1), p[1],
              msg = "neuronalStruct variable needs a subcript")
      else:
        # if it's neither a scalar or a neuronalStruct, it shouldn't be here
        raise SATTypeError(p.lineno(1), p[1], 
            expected_types = ('int', neuronalStruct.__name__))
    except LookupError:
      # if the symbol is not contained in the symbol table, report undefined
      # symbol
      raise SATNameError(line = p.lineno(1), name = p[1])

  def p_listindex(self, p):
    '''listindex : index
                 | listindex index'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[2])
      p[0] = p[1]

  def p_index(self, p):
    '''index : '[' expr ']' '''
    p[0] = p[2]

  def p_listexpr(self, p):
    '''listexpr : expr
                | listexpr ',' expr'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[1].append(p[3])
      p[0] = p[1]

  def p_expr_binary(self, p):
    '''expr : expr '+' expr
            | expr '-' expr
            | expr '*' expr
            | expr '/' expr'''
    p[0] = p[1] + p[2] + p[3]

  def p_expr_unary(self, p):
    '''expr : '-' expr %prec UMINUS'''
    p[0] = p[1] + p[2]

  def p_expr_number(self, p):
    '''expr : INTEGER'''
    p[0] = str(p[1])

  def p_expr_variable(self, p):
    '''expr : IDENT'''
    p[0] = p[1]

  def p_expr_group(self, p):
    '''expr : '(' expr ')' '''
    p[0] = p[1] + p[2] + p[3]

  # ___________________________ Penalties __________________________________#
  def p_penalties(self, p):
    '''penalties : PENALTIES ':' listpenalty'''
    p[0] = p.lineno(1)

  def p_listpenalty(self, p):
    '''listpenalty : penalty ';'
                   | penalty ';' listpenalty'''
    pass

  def p_penalty(self, p):
    '''penalty : IDENT ':' penalty_tuple'''
    pid = p[1]
    # was this penalty id used?
    if pid in self.known_penalty_ids:
      level, correlation = p[3]
      # check if penalty id is in some other level
      if pid in self.penalty2level:
        raise SATValueError(p.lineno(1), 
            "%s is already in level %s" % (pid, level))

      self.penalty2level[pid] = level

      p = penalty(pid, level, correlation)
      if level in self.penalties:
        self.penalties[level].append(p)
      else:
        self.penalties[level] = [p]
    elif self.symbols.has_key(pid):
      # IDENT is not of type constraint group
      raise SATTypeError(p.lineno(1), pid, expected_type = "constraint group")
    else:
      # IDENT could not be found. Report undefined symbol
      raise SATNameError(line = p.lineno(1), name = pid)

  def p_penalty_tuple(self, p):
    '''penalty_tuple : LEVEL INTEGER ',' CORRELATION INTEGER'''
    level, correlation = p[2], p[5]
    if level < 0:
      raise SATValueError(p.lineno(3),"levels must be non-negative intergers")
    if correlation < 1:
      raise SATValueError(p.lineno(3),"correlations must be positive intergers")
    p[0] = level, correlationp

  # Empty rule
  def p_empty(self, p):
    '''empty :'''
    p[0] = None

  # Error rule for syntax errors
  def p_error(self, p):
    if not p: 
      raise SATParseError(msg = "Unexpect end of file")
    else:
      raise SATParseError(line = p.lineno, column = self.get_column(p))

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  if len(sys.argv) == 2:
    data = open(sys.argv[1]).read()
    parser = SATParser(data)
    result = parser.parse()
