#! /usr/bin/env python3
"""
"""
## Standard Library
import sys

def main(argv: list):
    """
    Parameters
    ----------
    argv: list
        Command line arguments list.
    """
    try:
        from satyrus import CLI
    except ImportError:
        raise SystemError("Satyrus3 is not correctly installed. See README for installation details.")
    else:
        CLI.run(argv)

if __name__ == '__main__':
    main(sys.argv) # Here we go!