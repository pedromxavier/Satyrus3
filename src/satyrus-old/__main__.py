#! /usr/bin/env python3
"""
"""
# Standard Library
import sys

def main(argv: list):
    """
    Parameters
    ----------
    argv: list
        Command line arguments list.
    """
    try:
        from satyrus import SATCLI
    except ImportError:
        raise SystemError("SATyrus3 is not correctly installed. See 'https://satyrus3.github.io/docs/' for installation details.")
    else:
        SATCLI.run(argv)

if __name__ == '__main__':
    main(sys.argv[1:]) # Here we go!