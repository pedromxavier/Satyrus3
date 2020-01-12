"""
This 
"""

from sat_engine import *;




def main(argc : int, argv : list):

    if argc == 2:
        fname = argv[1]

        engine = Engine(lexer, parser);

        with open(fname, 'r') as file:

            code = file.read()

            engine.compile(code)
    else:
        stderr << "File Path missing."

if __name__ == '__main__':
    argc, argv = len(sys.argv), sys.argv

    main(argc, argv)

source = __doc__
