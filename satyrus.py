r""" Satyrus III - A compiler.
"""

import sys
import os

def main(argc: int, argv: list):
    """ :: Satyrus CLI ::
        =================
    """
    import argparse
    from satyrus import SatAPI
    from satyrus.satlib import stdout, stdwar, stderr

    kwargs = {
        'description' : __doc__
    }

    parser = argparse.ArgumentParser(**kwargs)
    
    parser.add_argument("source", help="source file")
    parser.add_argument("-o", "--out", dest="out", help="output format", choices=SatAPI.options)
    parser.add_argument("--legacy", action='store_true')

    args = parser.parse_args()

    ## Check source path
    source_path: str = str(args.source)

    if not os.path.exists(source_path):
        stderr << f"File `{os.path.abspath(source_path)}` doesn't exists."
        exit(1)

    ## Legacy mode
    legacy: bool = bool(args.legacy)

    if legacy:
        stdwar << f"Parser is in legacy mode."

    sat_api = SatAPI(source_path=source_path, legacy=legacy, solve=True)

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)