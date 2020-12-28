r"""
   _____      _________     _______  _    _  _____
  / ____\  /\|__   __\ \   / /  __ \| |  | |/ ____\
 | (____  /  \  | |   \ \_/ /| |__) | |  | | (____ 
  \___  \/ /\ \ | |    \   / |  _  /| |  | |\___  \ 
  ____) / ____ \| |     | |  | | \ \| |__| |____) |
 |_____/_/    \_\_|     |_|  |_|  \_ \____/ \_____/


"""
import sys
import os

def main(argc: int, argv: list):
    """ :: Satyrus CLI ::
        =================
    """
    import argparse
    from satyrus import SatAPI

    kwargs = {
        'description' : __doc__
    }

    parser = argparse.ArgumentParser(**kwargs)
    
    parser.add_argument("source", help="source file")
    parser.add_argument("-o", "--out", dest="out", help="output format", choices=SatAPI.options)
    parser.add_argument("--legacy", action='store_true')

    args = parser.parse_args()

    print(f'ARGS: {args}')

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)