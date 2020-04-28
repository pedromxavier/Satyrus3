""" :: System ::
    ============
"""

## Standard Library
import os
import sys
import shutil
import warnings

class system(object):

    ready = False

    @classmethod
    def init(cls):
        if not cls.ready:
            ## Load Home Path

            cls.ready = True
            raise NotImplementedError()
        else:
            warnings.warn(f"{cls} was already initialized.", RuntimeWarning)