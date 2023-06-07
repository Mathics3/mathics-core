# -*- coding: utf-8 -*-

"""
Low-level Profiling

Low-level (Python) profile from inside the Mathics interpreter

"""

import cProfile
import pstats
import sys
from io import StringIO

from mathics.builtin import Builtin
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_PROTECTED
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolNull


class PythonCProfileEvaluation(Builtin):
    """
    <url>:Python:https://docs.python.org/3/library/profile.html</url>

    <dl>
      <dt>'PythonProfileEvaluation[$expr$]'
      <dd>profile $expr$ with the Python's cProfiler.
    </dl>

    >> PythonCProfileEvaluation[a + b + 1]
     = ...
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED
    summary_text = "profile the internal evaluation of an expression"

    def eval(self, expr: Expression, evaluation: Evaluation):
        "PythonCProfileEvaluation[expr_]"
        profile_result = SymbolNull
        textstream = StringIO()
        if sys.version_info >= (3, 8):
            with cProfile.Profile() as pr:
                result = expr.evaluate(evaluation)
                stats = pstats.Stats(pr, stream=textstream)
            stats.strip_dirs().sort_stats(-1).print_stats()
            # TODO: convert the string (or the statistics)
            # into something like a WL Table, by splitting the
            # rows and the columns. By now, just a string
            # is returned.
            profile_result = from_python(textstream.getvalue())
        else:
            result = expr.evaluate(evaluation)
        return ListExpression(result, profile_result)
