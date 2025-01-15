#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from llvmlite import ir

    int_type = ir.IntType(64)
    real_type = ir.DoubleType()
    bool_type = ir.IntType(1)
    void_type = ir.VoidType()
except:
    int_type = int
    real_type = float
    bool_type = bool
    void_type = type(None)
