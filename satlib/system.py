""" :: System ::
    ============
"""

## Standard Library
import os
import sys
import shutil
import warnings

## Local
from .stack import Stack

class DirStack(Stack):

    def push(self, path: str):
        try:
            os.chdir(path)
            Stack.push(self, os.path.abspath(os.getcwd()))
        except FileNotFoundError:
            raise
    
    def pop(self):
        if len(self) >= 2:
            path = Stack.pop(self)
            os.chdir(self.top)
            return path
        else:
            os.chdir(self.top)
            return self.top

class System(object):

    home = None
    ready = False

    __ref__ = None

    def __new__(cls):
        if cls.__ref__ is None:
            cls.__ref__ = object.__new__(cls)
        return cls.__ref__

    def __init__(self):
        self.dir_stack = DirStack([self.home])

    def dir_push(self, path: str):
        self.dir_stack.push(path)

    def dir_pop(self):
        return self.dir_stack.pop()

system = System()