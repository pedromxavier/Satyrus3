""" SATyrus Test File
"""

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

		(int) A[0]:

		@{i=[1:5]}
		${j=[1:3]}

		x[i] -> y[j];
		"""

		code, sco = compiler(source)

		print(code)

		print(sco)


if __name__ == '__main__':
	Test.api()

	Test.compiler()
