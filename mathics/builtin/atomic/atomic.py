# -*- coding: utf-8 -*-
"""Atomic Primitives
"""

from mathics.builtin.base import (
    Builtin,
    Test,
)


class AtomQ(Test):
    """
    <dl>
    <dt>'AtomQ[$expr$]'
        <dd>returns 'True' if $expr$ is an expression which cannot be divided into subexpressions, or 'False' otherwise.

        An expression that cannot be divided into subparts is called called an "atom".
    </dl>

    Numbers are atoms:
    >> AtomQ[1.2]
     = True

    So are symbolic constants:
    >> AtomQ[2 + I]
     = True

    A 'Symbol' not bound to a value is an atom too:
    >> AtomQ[x]
     = True

    On the other hand, expressions aren't atoms:
    >> AtomQ[2 + Pi]
     = False

    Note that evaluation or the binding of $x$ to an expression is taken into account:
    >> x = 2 + Pi; AtomQ[x]
     = False

    Again, note that the expression evaluation to a number occurs before 'AtomQ' evaluated:
    >> AtomQ[2 + 3.1415]
     = True

    #> Clear[x]
    """

    summary_text = "tests whether an expression is an atom"

    def test(self, expr):
        return expr.is_atom()


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

    summary_text = "finds the head of any expression, including an atom"

    def apply(self, expr, evaluation):
        "Head[expr_]"

        return expr.get_head()
