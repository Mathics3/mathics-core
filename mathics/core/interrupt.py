# -*- coding: utf-8 -*-
"""Evaluation interrupts"""


class EvaluationInterrupt(Exception):
    pass


class AbortInterrupt(EvaluationInterrupt):
    pass


class TimeoutInterrupt(EvaluationInterrupt):
    pass


class ReturnInterrupt(EvaluationInterrupt):
    def __init__(self, expr):
        self.expr = expr


class BreakInterrupt(EvaluationInterrupt):
    pass


class ContinueInterrupt(EvaluationInterrupt):
    pass


class WLThrowInterrupt(EvaluationInterrupt):
    def __init__(self, value, tag=None):
        self.tag = tag
        self.value = value
