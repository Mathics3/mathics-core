# -*- coding: utf-8 -*-
"""
Mathics ``Compile`` implementation.

Here we have routines for compiling Mathics code.

At present, we use LLVM for this.
"""
import importlib

from .base import CompileArg as CompileArg, CompileError as CompileError
from .types import (
    bool_type as bool_type,
    int_type as int_type,
    real_type as real_type,
    void_type as void_type,
)

if importlib.util.find_spec("llvmlite"):
    from .compile import _compile as _compile
    from .ir import IRGenerator as IRGenerator

    has_llvmlite = True
else:
    has_llvmlite = False
