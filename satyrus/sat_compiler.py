"""
The SATyrus Compiler translates .sat code
into .sco (SATyrus compiled object) which
is basially a dictionary (JSON-like) with
the following keys:

{
	'int' : (list), 	 # integrity constraints
	'opt' : (list), 	 # optimality constraints
	'precision' : (int), # decimal precision
	'epsilon' : (float), # tiebreak factor
	'penalty' : (float), # base penalty value
}
"""
from sat_parser import SatParser

class Compiler:

	DEFAULT_SCO = {
		'int' : [],  	  # integrity constraints
		'opt' : [],  	  # optimality constraints
		'precision' : 10, # decimal precision
		'epsilon' : 1E-6, # tiebreak factor
		'penalty' : 1, 	  # base penalty value
	}
	
	def __init__(self, lexer=None, parser=None):
		self.lexer = lexer
		self.parser = parser

	def __call__(self, source):
		code = self.parser.parse(source)

		return code, Compiler.DEFAULT_SCO




		
