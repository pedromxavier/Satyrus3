# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Add Lexer to Pygments ---------------------------------------------------

from pygments.lexer import RegexLexer
from pygments import token
from sphinx.highlighting import lexers

class SATishLexer(RegexLexer):
    name = 'SATish'
    aliases = ['satish']
    filenames = ['*.sat']

    tokens = {
        'root': [
            (r'\#\{[\S\s]*?\}\#', token.Comment.Multiline),
            (r'\#.*?$', token.Comment.Singleline),
            (r'[-+]?[0-9]*\.?[0-9]+([Ee][-+]?[0-9]+)?', token.Number),
            (r'\(int\)', token.Keyword),
            (r'\(opt\)', token.Keyword),
            (r'\(', token.Punctuation),
            (r'\)', token.Punctuation),
            (r'\[', token.Punctuation),
            (r'\]', token.Punctuation),
            (r'\{', token.Punctuation),
            (r'\}', token.Punctuation),
            (r'\;', token.Punctuation),
            (r'\:', token.Punctuation),
            (r'\,', token.Punctuation),
            (r'\@', token.Operator),
            (r'\$', token.Operator),
            (r'\&', token.Operator),
            (r'\|', token.Operator),
            (r'\^', token.Operator),
            (r'\~', token.Operator),
            (r'\<\-\>', token.Operator),
            (r'\<\-', token.Operator),
            (r'\-\>', token.Operator),
            (r'\+', token.Operator),
            (r'\-', token.Operator),
            (r'\*', token.Operator),
            (r'\!\=', token.Operator),
            (r'\=\=', token.Operator),
            (r'\<\=', token.Operator),
            (r'\>\=', token.Operator),
            (r'\=', token.Operator),
            (r'\<', token.Operator),
            (r'\>', token.Operator),
            (r'\?[a-zA-Z_][a-zA-Z0-9_]*\:', token.Literal),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', token.Name),
            (r'\s', token.Whitespace)
            #(r'.*', token.Text),
        ],
    }

lexers['satish'] = SATishLexer(startinline=True)

# -- Project information -----------------------------------------------------

project = 'Satyrus'
author = 'Pedro Maciel Xavier'
copyright = f'2021, {author}'


# The full version, including alpha/beta/rc tags
release = '3.0.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['recommonmark', 'sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# ----------------------------------------------------------------------------
