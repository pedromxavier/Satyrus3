.. Satyrus documentation master file, created by
   sphinx-quickstart on Wed Feb 24 17:46:52 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SATish Language
***************

Syntax
======

SATish syntax follows most of the design patterns found in mainstream programming languages such as C/C++, Fortran and Python and should be of easy understanding for the begginer programmer.

Assignment
----------

.. code-block:: none

   # constant definition
   n = 3;

   x[n][n] = { 
       (1, 1): 1, # sets first element to 1
       (3, 3): 0  # sets last element to 0
   }; 

   y[n]; #

Constraints
-----------

.. code-block:: none
   
   (int) const[1]:
       @{i = [1:n]} # forall i from 1 to n
       ${j = [1:n]} # exists j from 1 to n
       x[i] -> y[j]; # x_i implies y_j

Legacy Syntax
=============
One might want to use the older SATish syntax, present in the previous versions of the compiler. This can be achieved with the ``--legacy`` option through the command line interface or via the ``legacy`` keyword argument supplied to the ``SatAPI`` and ``Satyrus`` constructors.

.. code-block:: shell

   $ satyrus oldsource.sat --legacy

.. code-block:: python
   
   >>> from satyrus import SatAPI
   >>> sat = SatAPI('oldsource.sat', legacy=True)

..  * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`