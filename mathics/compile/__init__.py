# -*- coding: utf-8 -*-
"""
Mathics3 ``Compile`` implementation.

Here we have routines for compiling Mathics3 code.

At present, we use LLVM for this.
"""
import importlib

from mathics.compile.base import CompileArg, CompileError
from mathics.compile.types import bool_type, int_type, real_type, void_type

if importlib.util.find_spec("llvmlite"):
    from mathics.compile.compile import _compile
    from mathics.compile.ir import IRGenerator

    has_llvmlite = True
else:
    has_llvmlite = False

__all__ = [
    "CompileArg",
    "CompileError",
    "IRGenerator",
    "_compile",
    "bool_type",
    "int_type",
    "real_type",
    "void_type",
]
