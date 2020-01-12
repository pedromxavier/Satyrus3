"""
The SATyrus Compiler translates .sat code
into .sco (SATyrus compiled object) which
is basially a dictionary (JSON-like) with
the following keys:

{
	'int' : [...],  # integrity constraints
	'opt' : [...],  # optimality constraints
	'prec' : (int),  # decimal precision
	'eps' : (float), # tiebreak factor
	'val' : (float),  # base penalty value

	'memory' : {},
}
"""
from sat_parser import parser

class Compiler:

	DEFAULT_SCO = {
		'int' : [],  # integrity constraints
		'opt' : [],  # optimality constraints
		'prec' : 10,  # decimal precision
		'eps' : 1E-6, # tiebreak factor
		'val' : 1, # base penalty value

		'memory' : {},
	}
	
	def __init__(self, parser):
		self.parser = parser

	def __call__(self, source):
		code = self.parser.parse(source)

		return code, Compiler.DEFAULT_SCO

compiler = Compiler(parser)


		
