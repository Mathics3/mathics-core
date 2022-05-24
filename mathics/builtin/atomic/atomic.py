# -*- coding: utf-8 -*-
"""
Atomic Primitives
"""

from mathics.builtin.base import (
    Builtin,
    Test,
)

from mathics.core.atoms import Atom


class AtomQ(Test):
    """
    <dl>
      <dt>'AtomQ[$expr$]'
      <dd>returns 'True' if $expr$ is an expression which cannot be divided into subexpressions, or 'False' otherwise.

      An expression that cannot be divided into subparts is called called an "atom".
    </dl>

    Strings and expressions that produce strings are atoms:
    >> Map[AtomQ, {"x", "x" <> "y", StringReverse["live"]}]
     = {True, True, True}

    Numeric literals are atoms:
    >> Map[AtomQ, {2, 2.1, 1/2, 2 + I, 2^^101}]
     = {True, True, True, True, True}

    So are Mathematical Constants:
    >> Map[AtomQ, {Pi, E, I, Degree}]
     = {True, True, True, True}

    A 'Symbol' not bound to a value is an atom too:
    >> AtomQ[x]
     = True

    On the other hand, expressions with more than one 'Part' after evaluation, even those resulting in numeric values, aren't atoms:
    >> AtomQ[2 + Pi]
     = False

    Similarly any compound 'Expression', even lists of literals, aren't atoms:
    >> Map[AtomQ, {{}, {1}, {2, 3, 4}}]
     = {False, False, False}

    Note that evaluation or the binding of "x" to an expression is taken into account:
    >> x = 2 + Pi; AtomQ[x]
     = False

    Again, note that the expression evaluation to a number occurs before 'AtomQ' evaluated:
    >> AtomQ[2 + 3.1415]
     = True

    #> Clear[x]
    """

    summary_text = "test whether an expression is an atom"

    def test(self, expr):
        return isinstance(expr, Atom)


class Head(Builtin):
    """
    <dl>
      <dt>'Head[$expr$]'
      <dd>returns the head of the expression or atom $expr$.
    </dl>

    >> Head[a * b]
     = Times
    >> Head[6]
     = Integer
    >> Head[x]
     = Symbol
    """

    summary_text = "find the head of any expression, including an atom"

    def apply(self, expr, evaluation):
        "Head[expr_]"

        return expr.get_head()
