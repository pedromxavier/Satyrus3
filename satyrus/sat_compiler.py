"""
The SATyrus Compiler translates .sat code
into .sco (SATyrus compiled object) which
is basially a dictionary (JSON-like) with
the following keys:

{
	'int' : [...],  # integrity constraints
	'opt' : [...],  # optimality constraints
	'prec' : (int)  # decimal precision
	'eps' : (float) # tiebreak factor
	'val' : (float)  # base penalty value
}


"""
