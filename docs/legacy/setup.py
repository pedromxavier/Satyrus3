#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup
from satyruslib import __VERSION__

author = 'Bruno França'
author_email = 'bfmonteiro@gmail.com'
url = 'http://www.lam.ufrj.br/projects/satyrus'

setup(
  name = 'SATyrus',
  version = __VERSION__,
  url = url,
  author = author,
  author_email = author_email,
  description = 'A SAT-based Neuro-Symbolic Architecture for Constraint Processing.',
  requires = ['ply'],
  packages = ['satyruslib'],
  scripts = ['satyrus'],
)
