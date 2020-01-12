""" SATyrus Test File
"""

## SATyrus API
from sat_api import Sat

sco = {
	'int' : [],
	'opt' : [],
	'prec': 20,
	'eps' : 1E-3,
	'n0'  : 1,

	'memory' : {},
}

Sat.execute(sco)
