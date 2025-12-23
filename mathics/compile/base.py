#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class CompileError(Exception):
    pass


class CompileArg:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"{self.name}:{self.type}"
