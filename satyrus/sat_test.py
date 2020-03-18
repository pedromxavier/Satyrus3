#/usr/bin/python3.8
""" SATyrus Test File
"""
from sat_core import *;

class Test:

	@staticmethod
	def api():
		## SATyrus API Test
		from sat_api import Sat

		sco = {
			'int' : [],
			'opt' : [],
			'prec': 20,
			'eps' : 1E-3,
			'n0'  : 1,

			'memory' : {},
		}

		print(Sat.execute(sco))


	@staticmethod
	def compiler():
		from sat_compiler import compiler

		source = """
# prec : 30;

m = 3;
n = 5;

x[m] = {(1) : 1, (m) : -1};
y[n] = {(1) : 0, (n) : +1};

(int) A[0]:

@{i=[1:m]}
${j=[1:n]}

x[i] -> y[j];
		"""

		code, sco = compiler(source)

		stdout << (source)

		print(code)

		print(sco)


if __name__ == '__main__':
	## Test.api()
	Test.compiler()