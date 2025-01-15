# -*- coding: utf-8 -*-
"""
This is the core of ``mathics-core`` package.

Here you find the lowest, and most fundamental modules and classes.

Objects here are fundamental to the system. These include objects like
``Symbols``, ``Numbers``, ``Rational``, ``Expressions``, ``Patterns`` and
``Rules`` to name a few.

While some parts of ``mathics-core`` could conceivably be written in
Mathics, but are instead written in Python for efficiency, everything
here pretty much has to written in Python.
"""

from typing import Callable, Optional

# PRE_EVALUATION_HOOK allows a debugger or tracer
# to intercept each expression parsed in order to
# change or wrap certain definitions or even alter the query.
PRE_EVALUATION_HOOK: Optional[Callable] = None
