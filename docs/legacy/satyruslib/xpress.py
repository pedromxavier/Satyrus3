from satutils import get_outfile

class XpressInterface(object):

  "Given an energy function and its variables, generates a Mosel model"

  model_template = \
"""model %s

uses \"mmxslp\"

declarations
%s
objdef: mpvar
end-declarations

%s

energy_function := %s
objdef = energy_function

SLPloadprob(objdef)
SLPminimize

writeln("Objective: ", getobjval)
%s
writeln

end-model
"""

  def __init__(self, vars, func, model_name=None):
    self.vars = vars
    self.func = func
    self.model_name = model_name if not model_name is None else "SATModel"

  def model(self):
    name = self.model_name
    func = str(self.func)

    vars = ""
    constrs = ""
    print_vars = ""

    for v in self.vars:
      vars += "%s: mpvar\n" % v
      constrs += "%s is_binary\n" % v
      print_vars += "writeln(\"%s = \", getsol(%s))\n" % (v, v)

    return self.model_template % (name, vars, constrs, func, print_vars)

  def write(self, basename):
    # create mosel model file 
    model_filename = basename + ".mos"
    mod_fd = get_outfile(model_filename)
    mod_fd.write(self.model())
    mod_fd.close()


if __name__ == "__main__":
  vars = 'x', 'y'
  func = "x + (1 - y)"
  model = "Test"
  xpress = XpressInterface(vars, func, model)
  xpress.write("/tmp/xpress")
