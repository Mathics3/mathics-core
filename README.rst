Welcome to Mathics Core!
========================

|Pypi Installs| |Latest Version| |Supported Python Versions| |SlackStatus|_

|Packaging status|


Mathics is a general-purpose computer algebra system (CAS).

However this repository contains just the Python modules for WL Built-in functions, variables, core primitives, e.g. Symbol, a parser to create Expressions, and an evaluator to execute them.

The home page for Mathics is https://mathics.org where you will find a list of screenshots and components making up the system.

Installing
----------

Installing locally, requires a number of dependencies and OS package dependencies.

See the `Installing Mathics <https://mathics-development-guide.readthedocs.io/en/latest/installing.html>`_ for instructions on installing Mathics3.

Running:
--------

Mathics3, the core library comes with a very simple command-line program called ``mathics``::

  $ mathics

  Mathics 5.0.3dev0
  on CPython 3.8.12 (heads/v2.3.4.1_release:4a6b4d3504, Jun  3 2022, 15:46:12)
  using SymPy 1.10.1, mpmath 1.2.1, numpy 1.23.1, cython 0.29.30

  Copyright (C) 2011-2022 The Mathics Team.
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

.. |SlackStatus| image:: https://mathics-slackin.herokuapp.com/badge.svg
.. _SlackStatus: https://mathics-slackin.herokuapp.com/
.. |Travis| image:: https://secure.travis-ci.org/Mathics3/mathics-core.svg?branch=master
.. _Travis: https://travis-ci.org/Mathics3/mathics-core
.. _PyPI: https://pypi.org/project/Mathics/
.. |mathicsscript| image:: https://github.com/Mathics3/mathicsscript/blob/master/screenshots/mathicsscript1.gif
.. |mathicssserver| image:: https://mathics.org/images/mathicsserver.png
.. |Latest Version| image:: https://badge.fury.io/py/Mathics3.svg
		 :target: https://badge.fury.io/py/Mathics3
.. |Pypi Installs| image:: https://pepy.tech/badge/Mathics3
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/Mathics3.svg
.. |Packaging status| image:: https://repology.org/badge/vertical-allrepos/mathics.svg
			    :target: https://repology.org/project/mathics/versions
