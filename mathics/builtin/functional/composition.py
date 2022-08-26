# -*- coding: utf-8 -*-

"""
Functional Composition and Operator Forms

<url>:Functional Composition: https://en.wikipedia.org/wiki/Function_composition_(computer_science)</url> is a way to combine simple functions to build more complicated ones.
Like the usual composition of functions in mathematics, the result of each function is passed as the argument of the next, and the result of the last one is the result of the whole.

The symbolic structure of Mathics makes it easy to create "operators" that can be composed and manipulated symbolically—forming "pipelines" of operations—and then applied to arguments.

Some built-in functions also directly support a "curried" form, in which they can immediately be given as symbolic operators.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.functional-composition"

from mathics.builtin.base import Builtin
from mathics.core.expression import Expression

from mathics.core.attributes import (
    flat as A_FLAT,
    one_identity as A_ONE_IDENTITY,
    protected as A_PROTECTED,
)


class Composition(Builtin):
    """
    <dl>
      <dt>'Composition[$f$, $g$]'
      <dd>returns the composition of two functions $f$ and $g$.
    </dl>

    >> Composition[f, g][x]
     = f[g[x]]
    >> Composition[f, g, h][x, y, z]
     = f[g[h[x, y, z]]]
    >> Composition[]
     = Identity
    >> Composition[][x]
     = x
    >> Attributes[Composition]
     = {Flat, OneIdentity, Protected}
    >> Composition[f, Composition[g, h]]
     = Composition[f, g, h]
    """

    attributes = A_FLAT | A_ONE_IDENTITY | A_PROTECTED

    rules = {
        "Composition[]": "Identity",
    }
    summary_text = "the composition of two or more functions"

    def apply(self, functions, args, evaluation):
        "Composition[functions__][args___]"

        functions = functions.get_sequence()
        args = args.get_sequence()
        result = Expression(functions[-1], *args)
        for f in reversed(functions[:-1]):
            result = Expression(f, result)
        return result


class Identity(Builtin):
    """
    <dl>
      <dt>'Identity[$x$]'
      <dd>is the identity function, which returns $x$ unchanged.
    </dl>
    X> Identity[x]
     = x
    X> Identity[x, y]
     = Identity[x, y]
    """

    rules = {
        "Identity[x_]": "x",
    }
    summary_text = "the identity function"


# TODO: ReverseApplied
