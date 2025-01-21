Welcome to Mathics Core!
========================

|PyPI Installs| |Latest Version| |Supported Python Versions|

|Packaging status|


Mathics3 is a general-purpose computer algebra system (CAS).

However this repository contains just the Mathics3 Kernel: Python
modules for WL Built-in functions, variables, core primitives,
e.g. Symbol, a parser to create Expressions, and an evaluator to
execute them.

The home page for Mathics is https://mathics.org where you will find a
list of screenshots and components making up the system.

Installing
----------

Installing locally, requires a number of dependencies and OS package dependencies.

See the `Installing Mathics3 <https://mathics-development-guide.readthedocs.io/en/latest/installing.html>`_ for instructions on installing Mathics3.

Running:
--------

Mathics3 Kernel comes with a very simple command-line program called ``mathics``::

  $ mathics

  Mathics 8.0.0
  on CPython 3.12.8 (main, Dec  9 2024, 11:38:23) [GCC 13.2.0]
  using SymPy 1.13.3, mpmath 1.3.0, numpy 1.26.4, cython Not installed

 Copyright (C) 2011-2025 The Mathics3 Team.
  This program comes with ABSOLUTELY NO WARRANTY.
  This is free software, and you are welcome to redistribute it
  under certain conditions.
  See the documentation for the full license.

  Quit by evaluating Quit[] or by pressing CONTROL-D.

  In[1]:=

Type ``mathics --help`` for options that can be provided.

For a more featureful frontend, see `mathicsscript
<https://pypi.org/project/mathicsscript/>`_.

For a Django front-end based web front-end see `<https://pypi.org/project/Mathics-Django/>`_.



Contributing
------------

Please feel encouraged to contribute to Mathics! Create your own fork, make the desired changes, commit, and make a pull request.


License
-------

Mathics is released under the GNU General Public License Version 3 (GPL3).

.. _PyPI: https://pypi.org/project/Mathics/
.. |mathicsscript| image:: https://github.com/Mathics3/mathicsscript/blob/master/screenshots/mathicsscript1.gif
.. |mathicssserver| image:: https://mathics.org/images/mathicsserver.png
.. |Latest Version| image:: https://badge.fury.io/py/Mathics3.svg
		 :target: https://badge.fury.io/py/Mathics3
.. |PyPI Installs| image:: https://pepy.tech/badge/Mathics3
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/Mathics3.svg
.. |Packaging status| image:: https://repology.org/badge/vertical-allrepos/mathics.svg
			    :target: https://repology.org/project/mathics/versions
