"""
Common Generic Option Values
"""

from mathics.core.builtin import Predefined, Test
from mathics.core.symbols import SymbolList


class All(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/All.html</url>

    <dl>
      <dt>'All'
      <dd>is an option value for a number of functions indicating to include everything.
    </dl>


    In list functions, it indicates all levels of the list.

    For example, in <url>
    :Part:
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/part</url>, \
    'All', extracts into a first column vector the first element of each of the \
    list elements:

    >> {{1, 3}, {5, 7}}[[All, 1]]
     = {1, 5}

    While in <url>
    :Take:
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/part</url>, \
    'All' extracts as a column matrix the first element as a list for each of the list \
    elements:

    >> Take[{{1, 3}, {5, 7}}, All, {1}]
     = {{1}, {5}}

    In <url>
    :Plot:
    /doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/general-graphical-plots/plot</url>, \
    setting the <url>
    :Mesh:
/doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/drawing-options-and-option-values/mesh</url> \
    option to 'All' will show the specific plot points:

    >> Plot[x^2, {x, -1, 1}, MaxRecursion->5, Mesh->All]
     = -Graphics-

    """

    summary_text = "option value that specify using everything"


class None_(Predefined):
    """
        <url>:WMA link:https://reference.wolfram.com/language/ref/None.html</url>

        <dl>
          <dt>'None'
          <dd>is a setting value for many options.
        </dl>

        Plot3D shows the mesh grid between computed points by default. This the <url>
        :Mesh:
/doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/drawing-options-and-option-values/mesh</url> \

        However, you hide the mesh by setting the 'Mesh' option value to 'None':

        >> Plot3D[{x^2 + y^2, -x^2 - y^2}, {x, -2, 2}, {y, -2, 2}, BoxRatios-> Automatic, Mesh->None]
         = -Graphics3D-
    """

    name = "None"
    summary_text = "option value that disables the option"


# Has this been removed from WL? I cannot find a WMA link.
class NotOptionQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NotOptionQ.html</url>

    <dl>
      <dt>'NotOptionQ'[$expr$]
      <dd>returns 'True' if $expr$ does not have the form of a valid \
          option specification.
    </dl>

    >> NotOptionQ[x]
     = True
    >> NotOptionQ[2]
     = True
    >> NotOptionQ["abc"]
     = True

    >> NotOptionQ[a -> True]
     = False
    """

    summary_text = "test whether an expression does not match the form of a valid option specification"

    def test(self, expr) -> bool:
        if hasattr(expr, "flatten_with_respect_to_head"):
            expr = expr.flatten_with_respect_to_head(SymbolList)
        if not expr.has_form("List", None):
            expr = [expr]
        else:
            expr = expr.elements
        return not all(
            e.has_form("Rule", None) or e.has_form("RuleDelayed", 2) for e in expr
        )


# Has this been removed from WL? I cannot find a WMA link.
class OptionQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OptionQ.html</url>

    <dl>
      <dt>'OptionQ'[$expr$]
      <dd>returns 'True' if $expr$ has the form of a valid option \
         specification.
    </dl>

    Examples of option specifications:
    >> OptionQ[a -> True]
     = True
    >> OptionQ[a :> True]
     = True
    >> OptionQ[{a -> True}]
     = True
    >> OptionQ[{a :> True}]
     = True

    Options lists are flattened when are applied, so
    >> OptionQ[{a -> True, {b->1, "c"->2}}]
     = True
    >> OptionQ[{a -> True, {b->1, c}}]
     = False
    >> OptionQ[{a -> True, F[b->1,c->2]}]
     = False

    'OptionQ' returns 'False' if its argument is not a valid option
    specification:
    >> OptionQ[x]
     = False
    """

    summary_text = (
        "test whether an expression matches the form of a valid option specification"
    )

    def test(self, expr) -> bool:
        if hasattr(expr, "flatten_with_respect_to_head"):
            expr = expr.flatten_with_respect_to_head(SymbolList)
        if not expr.has_form("List", None):
            expr = [expr]
        else:
            expr = expr.elements
        return all(
            e.has_form("Rule", None) or e.has_form("RuleDelayed", 2) for e in expr
        )


## FIXME: add:
## Full (distinct from graphics option?),
## Inherited,
## Manual
