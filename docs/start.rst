.. Satyrus documentation master file, created by
   sphinx-quickstart on Wed Feb 24 17:46:52 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
***************

Installation
============
Satyrus requires a 3.7+ CPython (`python.org <https://www.python.org/>`_) distribution. You may install it directly via `pip <https://pypi.org/>`_ or build from source.

Linux, OSx
----------
.. code-block:: bash
        
    $ python3 -m pip install satyrus

Windows
-------
.. code-block:: shell

    > pip install satyrus

Command line interface
======================
.. code-block:: shell

    $ satyrus --help
    $ satyrus source.sat

Python API
==========

.. code-block:: python

   >>> from satyrus import SatAPI
   >>> sat = SatAPI('source.sat')
   >>> x, e = sat['solver'].solve()

..  * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`