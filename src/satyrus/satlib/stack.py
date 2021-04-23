## Standard Library
from collections import deque

class Queue:

    def __init__(self, buffer=None, limit=None):
        self.__limit = limit
        self.__queue = deque([] if buffer is None else buffer, self.__limit)

    def clear(self):
        self.__queue.clear()

    def push(self, x: object):
        self.__queue.appendleft(x)

    def pop(self) -> object:
        return self.__queue.pop()

    def pushleft(self, x: object):
        self.__queue.appendleft(x)

    def popleft(self):
        return self.__queue.popleft()

    def copy(self):
        return self.__class__(buffer=self.__queue.copy(), limit=self.__limit)

    def __getitem__(self, index):
        return self.__queue.__getitem__(index)

    def __str__(self):
        return "\n".join(map(str, self.__queue))

    def __iter__(self):
        return iter(self.__queue)

    def __bool__(self):
        return bool(self.__queue)

    def __len__(self):
        return len(self.__queue)

    def __contains__(self, x):
        return x in self.__queue

    @property
    def top(self):
        return self.__queue[-1]

class Stack:

    def __init__(self, buffer=None, limit=None):
        self.__limit = limit
        self.__stack = deque([] if buffer is None else buffer, self.__limit)

    def clear(self):
        self.__stack.clear()

    def push(self, x: object):
        self.__stack.append(x)

    def pop(self) -> object:
        return self.__stack.pop()

    def pushleft(self, x: object):
        self.__stack.appendleft(x)

    def popleft(self):
        return self.__stack.popleft()

    def copy(self):
        return self.__class__(buffer=self.__stack.copy(), limit=self.__limit)

    def __getitem__(self, index):
        return self.__stack.__getitem__(index)

    def __str__(self):
        return "\n".join(map(str, reversed(self.__stack)))

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
        return self.__stack[-1]

__all__ = ["Stack", "Queue"]