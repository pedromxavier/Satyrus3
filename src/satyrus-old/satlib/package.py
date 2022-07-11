from os import urandom
import sys
import site
from pathlib import Path

PACKAGE = "satyrus_data"


def package_path(*, package: str = PACKAGE, fname: str = None) -> Path:
    """"""
    if fname is None:
        sys_path = Path(sys.prefix).joinpath(package)
        usr_path = Path(site.USER_BASE).joinpath(package)
    else:
        sys_path = Path(sys.prefix).joinpath(package, fname)
        usr_path = Path(site.USER_BASE).joinpath(package, fname)

    if not sys_path.exists():
        if not usr_path.exists():
            raise FileNotFoundError(f"File or Directory '{fname}' not installed in '{package}'")
        else:
            return usr_path
    else:
        return sys_path


__all__ = ["PACKAGE", "package_path"]
