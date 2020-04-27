## Standard Library
from collections import deque

class Stack:

    def __init__(self, buffer=None, limit=None):
        self.__stack = deque([] if buffer is None else buffer, limit)

    def add(self, x):
        return self.__stack.append(x)

    def pop(self):
        return self.__stack.pop()

    def __iter__(self):
        return iter(self.__stack)

    def __bool__(self):
        return bool(self.__stack)

    def __contains__(self, x):
        return x in self.__stack
