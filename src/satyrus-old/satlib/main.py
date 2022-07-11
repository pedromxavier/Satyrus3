"""
"""
# Future Imports
from __future__ import annotations

# Standard Library
import os
import posixpath
import traceback
from functools import wraps, reduce

os.path.join = posixpath.join

def arange(start: object, stop: object = None, step: object = None):
    """\
    arange(stop) -> [0, 1, ..., stop]
    arange(start, stop) -> [start, start + 1, ..., stop]
    arange(start, stop, step) -> [start, start + step, ..., stop]
    """
    ## Value Checking
    if step == 0:
        raise ValueError("Step must be non-zero.")

    ## Defaults
    if stop is None:
        stop = start
        start = 0

    if step is None:
        if start > stop:
            step = -1
        elif start <= stop:
            step = 1

    ## A bit more Value Checking
    if start > stop and step > 0 or start < stop and step < 0:
        raise ValueError(f"Infinite range in [{start}:{stop}:{step}].")

    ## Type Coercing
    if any(type(s) is float for s in {start, stop, step}):
        x = float(start)
        stop = float(stop)
        step = float(step)
    elif any(type(s) is int for s in {start, stop, step}):
        x = int(start)
        stop = int(stop)
        step = int(step)
    else:
        x = start

    ## Iterator Loop
    if step > 0:
        while x <= stop:
            yield x
            x += step
    else:
        while x >= stop:
            yield x
            x += step


def log(target: str = "satyrus.log") -> str:
    """\
    """
    trace: str = traceback.format_exc()
    with open(target, "w", encoding="utf8") as file:
        file.write(trace)
    return trace

def prompt(question: str, answers: dict[str, object]) -> Any:
    while True:
        answer: str = input(question).strip()

        if answer not in answers:
            continue
        else:
            return answers[answer]

__all__ = ["arange", "log", "prompt"]
