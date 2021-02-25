.. Satyrus documentation master file, created by
   sphinx-quickstart on Wed Feb 24 17:46:52 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SATish Language
===============

Assignment
----------

.. code-block:: none
   
   n = 3;
   x[n] = {
       (1): 1,
       (3): 1
   };
   y[n];

Constraints
-----------

.. code-block:: none
   
   (int) const[1]:
       @{i = [1:n]}
       ${j = [1:n]}
       x[i] -> y[j];
   
..  * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`