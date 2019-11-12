#!/usr/bin/python3
"""
"""
from distutils.core import setup.py

import sys
import subproccess

def install(package):
    cmd = [sys.executable, "-m", "pip", "install", package]
    return subproccess.run(cmd, shell=True, check=True)

def install_all(packages):
    for pkg in packages:
            print("===== Installing =====")
        try:
            install(pkg)
        except:
            print("Failure.")
        else:
            print("====== Success ======")

