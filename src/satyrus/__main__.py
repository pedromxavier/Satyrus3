#! /usr/bin/env python3
"""Satyrus3 script entry point.
"""
from . import CLI

def main():
    import sys
    CLI.run(sys.argv)