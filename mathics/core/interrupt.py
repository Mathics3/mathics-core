# -*- coding: utf-8 -*-
"""Evaluation interrupts"""


class EvaluationInterrupt(Exception):
    pass


class AbortInterrupt(EvaluationInterrupt):
    pass


class TimeoutInterrupt(EvaluationInterrupt):
    pass


class TimeConstrainedTimeout(BaseException):
    """Raised asynchronously in the evaluating thread when the time of
    a TimeConstrained runs out.

    It derives from BaseException, not Exception, so that the
    ``except Exception:`` handlers in builtins (around SymPy and
    mpmath calls, for instance) do not swallow it and let the
    evaluation go on with a partial result.

    The TimeConstrained whose time ran out turns it into its failure
    expression; see mathics.eval.datetime.eval_timeconstrained.
    """


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
