"""
#prec : 33;
#dir  : "C:/Users/Pedro/Desktop/UFRJ";

%{ ------------------------ }
 * Satyrus III Code Example
 *
 *
 { ------------------------ }%


m = 5;
n = 3;

dist[n][n] = { % Distances Array Definition
    (1,1) : 1,
    (n,n) : 1
};

x[m][n]; % Solution Array Declaration

y[m] = {(1) : 1, (2) : 0, (3) : +4, (4) : 2, (5) : -1};
"""

"""
(int) A[0]: % Integrity Constraint at level 0

@ {i = [1:5]}
@ {j = [1:5]}
@ {k = [1:5]}

c[i][j] -> x[i][k] & y[j][k];

(int) B[1]: % Integrity Constraint at level 1

@ {i = [1:5]}
@ {j = [1:5]}
@ {k = [1:5]}

c[i][j] -> x[i][k] & y[j][k];

(opt) C: % Optimality Constraint  (level 0 as default)

@ {i = [1:5]}
@ {j = [1:5]}
@ {k = [1:5]}

c[i][j] -> x[i][k] & y[j][k];
"""

from sat_engine import *;

def main(argc : int, argv : list):

    if argc == 2:
        fname = argv[1]

        engine = Engine(lexer, parser);

        with open(fname, 'r') as file:

            code = file.read()

            engine.compile(code)

        stdalt << f"Float Prec : {dcm.context.prec}"
        stdalt << f"Dir : {os.getcwd()}"

    else:
        stderr << "File Path missing."

if __name__ == '__main__':
    argc, argv = len(sys.argv), sys.argv

    main(argc, argv)

source = __doc__
