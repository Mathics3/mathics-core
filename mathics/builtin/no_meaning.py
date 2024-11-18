# -*- coding: utf-8 -*-
# Note: this will be redone soon to pull no-meaning operator information from operators.yml out
# of the MathicsScanner project.
"""
Operators without Built-in Meanings

Not all operators recognized by the Mathics3 are associated with functions that have built‐in meanings.
You can use these operators as a way to build up your own notation within the Mathics3.
"""

from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.builtin import BinaryOperator


class Star(BinaryOperator):
    r"""
    Star <url>
    :WML link:
    https://reference.wolfram.com/language/ref/Star.html</url>

    <dl>
      <dt>'Star[$x$, $y$, ...]'
      <dd>displays $x$ ⋆ $y$ ⋆ ...
    </dl>

    >> Star[x, y, z]
     = x ⋆ y ⋆ z

    >> a \[Star] b
     = a ⋆ b
    """

    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see below.
    formats = {
        (("InputForm", "OutputForm", "StandardForm"), "Star[args__]"): (
            'Infix[{args}, "⋆"]'
        ),
    }

    operator = "⋆"  # \u22C6
    summary_text = "star symbol"
