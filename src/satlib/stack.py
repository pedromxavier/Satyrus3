## Standard Library
from collections import deque

class Stack:

    def __init__(self, buffer=None, limit=None):
        self.__stack = deque([] if buffer is None else buffer, limit)

    def push(self, x):
        self.__stack.append(x)

    def pop(self):
        return self.__stack.pop()

    def __getitem__(self, index):
        return self.__stack.__getitem__(index)

    def __iter__(self):
        return iter(self.__stack)

    def __bool__(self):
        return bool(self.__stack)

    def __len__(self):
        return len(self.__stack)

    def __contains__(self, x):
        return x in self.__stack

    @property
    def top(self):
        return self[-1]
