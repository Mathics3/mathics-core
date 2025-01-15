# -*- coding: utf-8 -*-
"""
Mathics ``Compile`` implementation.

Here we have routines for compiling Mathics code.

At present, we use LLVM for this.
"""

try:
    import llvmlite

    has_llvmlite = True
except ImportError:
    has_llvmlite = False


from .base import CompileArg, CompileError
from .types import *

if has_llvmlite:
    from .compile import _compile
    from .ir import IRGenerator
