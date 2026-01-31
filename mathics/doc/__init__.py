# -*- coding: utf-8 -*-
"""
A module and library that assists in organizing document data
located in static files and docstrings from
Mathics3 Builtin Modules. Builtin Modules are written in Python and
reside either in the Mathics3 core (mathics.builtin) or are packaged outside,
in Mathics3 Modules e.g. pymathics.natlang.

This data is stored in a way that facilitates:
* organizing information to produce a LaTeX file
* running documentation tests
* producing HTML-based documentation

The command-line utility ``docpipeline.py``, loads the data from
Python modules and static files, accesses the functions here.

Mathics Django also uses this library for its HTML-based documentation.

The Mathics3 builtin function ``Information[]`` also uses to provide the
information it reports.
As with reading in data, final assembly to a LaTeX file or running
documentation tests is done elsewhere.

FIXME: This code should be replaced by Sphinx and autodoc.
Things are such a mess, that it is too difficult to contemplate this right now.
Also there higher-priority flaws that are more more pressing.
In the shorter, we might we move code for extracting printing to a
separate package.
"""
