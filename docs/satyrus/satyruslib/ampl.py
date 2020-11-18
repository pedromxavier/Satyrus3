from satutils import get_outfile

class AmplInterface(object):

  "Given an energy function and its variables, generates an AMPL model"

  model_template = \
"""# Variables:
%s

# Energy Function:
minimize f: %s;
"""

  input_file_template = \
"""model %s;
option solver %s;
solve;
display {i in 1.._nvars} (_varname[i], _var[i]);
"""


  def __init__(self, vars, func, solver):
    self.vars = vars
    self.func = func
    self.solver = solver

  def model(self):
    vars = '\n'.join(map(lambda v: "var %s binary;" % v, self.vars))
    func = str(self.func)
    return self.model_template % (vars, func)

  def input_file(self, model_filename):
    solver = self.solver
    return self.input_file_template % (model_filename, solver)

  def write(self, basename):
    # create ampl model file 
    model_filename = basename + ".mod"
    mod_fd = get_outfile(model_filename)
    mod_fd.write(self.model())
    mod_fd.close()

    # create ampl input file
    input_filename = basename + ".in"
    input_fd = get_outfile(input_filename)
    input_fd.write(self.input_file(model_filename))
    input_fd.close()


if __name__ == "__main__":
  vars = 'x', 'y'
  func = "x + (1 - y)"
  solver = "cplex"
  ampl = AmplInterface(vars, func, solver)
  ampl.write("/tmp/ampl")
