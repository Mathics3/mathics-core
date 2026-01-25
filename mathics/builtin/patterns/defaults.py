# -*- coding: utf-8 -*-
"""
Pattern Defaults


"""

from typing import Optional as OptionalType

from mathics.core.builtin import InfixOperator, PatternObject
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.keycomparable import PATTERN_SORT_KEY_OPTIONAL
from mathics.core.pattern import BasePattern
from mathics.eval.patterns import get_default_value

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.patttern-defaults"


class Optional(InfixOperator, PatternObject):
    """<url>:WMA link:https://reference.wolfram.com/language/ref/Optional.html</url>

    <dl>
      <dt>'Optional'[$pattern$, $default$]
      <dt>'$pattern$ : $default$'
      <dd>is a pattern matching $pattern$; when $pattern$ is omitted, \
        $default$ is substituted for $pattern$.
    </dl>

    Optional is used to specify optional arguments in function signatures.

    Set up a default value of 1 for the pattern 'y_' in function 'f':

    >> f[x_, y_:1] := {x, y}

    Above, we put no spaces before or after ':', but they can be added. So:

    >> f[x_, y_: 1] := {x, y}

    is the same as the above.

    When we specify a value for the 'y' parameter, it has the value provided:
    >> f[a, 2]
     = {a, 2}

    But if the 'y' parameter is missing, we replace the parameter \
    using the default given in the delayed assignment above:

    >> f[a]
     = {a, 1}

    Both 'Optional' and <url>:Pattern:
    /doc/reference-of-built-in-symbols/rules-and-patterns/composite-patterns/pattern/</url> \
    use ':' as their operator symbol. And both operators are used to represent a pattern.

    The way to disambiguate which of the two is used is by the first or left operand. When \
    this is a $symbol$, like 'y', the ':' operator indicates a 'Pattern':

    >> y : 1 // FullForm
     = Pattern[y, 1]

    In contrast, we have a <i>pattern</i> to the left of the colon, like 'y_' we have an 'Optional' expression:

    >> y_ : 1 // FullForm
     = Optional[Pattern[y, Blank[]], 1]

    The special form 'y_.' is equivalent to 'Optional[y_]':

    >> FullForm[y_.]
     = Optional[Pattern[y, Blank[]]]

    In this situation, when the is 'y' parameter omitted, the value comes from <url>\
    :Default:/doc/reference-of-built-in-symbols/options-management/default/</url>:

    >> Default[g] = 4
     = 4

    >> g[x_, y_.] := {x, y}

    >> g[a]
     = {a, 4}

    Note that the 'Optional' operator binds more tightly than the \
    'Pattern'.  Keep this in mind when there is more than one colon, \
    juxtaposed, each representing different operators:

    >> x : _+y_ : d // FullForm
     = Pattern[x, Plus[Blank[], Optional[Pattern[y, Blank[]], d]]]

    """

    arg_counts = [1, 2]

    default_formats = False

    formats = {
        "Verbatim[Optional][pattern_Pattern, default_]": 'Infix[{HoldForm[pattern], HoldForm[default]}, ":", 140, Right]'
    }
    grouping = "Right"
    rules = {
        (
            "MakeBoxes[Verbatim[Optional]["
            "Verbatim[Pattern][symbol_Symbol,"
            "(kind:(Verbatim[Blank]|Verbatim[BlankSequence]|Verbatim[BlankNullSequence])[])]], "
            "(f:StandardForm|TraditionalForm)]"
        ): 'MakeBoxes[symbol, f] <> ToString[kind, f] <>"."',
        (
            "MakeBoxes[Verbatim[Optional]["
            "(kind:(Verbatim[Blank]|Verbatim[BlankSequence]|Verbatim[BlankNullSequence])[])], "
            "(f:StandardForm|TraditionalForm)]"
        ): 'ToString[kind, f]<>"."',
        # Two arguments
        (
            "MakeBoxes[Verbatim[Optional]["
            "Verbatim[Pattern][symbol_Symbol,"
            "(kind:(Verbatim[Blank]|Verbatim[BlankSequence]|Verbatim[BlankNullSequence])[]), value_]], "
            "(f:StandardForm|TraditionalForm)]"
        ): 'RowBox[{MakeBoxes[symbol, f], ToString[kind, f], ":",MakeBoxes[value, f]}]',
        (
            "MakeBoxes[Verbatim[Optional]["
            "(kind:(Verbatim[Blank]|Verbatim[BlankSequence]|Verbatim[BlankNullSequence])[]), value_], "
            "(f:StandardForm|TraditionalForm)]"
        ): 'RowBox[{ToString[kind, f], ":", MakeBoxes[value, f]}]',
    }
    summary_text = "an optional argument with a default value"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        self.pattern = BasePattern.create(expr.elements[0], evaluation=evaluation)
        if len(expr.elements) == 2:
            self.default = expr.elements[1]
        else:
            self.default = None

    def match(self, expression: Expression, pattern_context: dict):
        head = pattern_context.get("head", None)
        evaluation = pattern_context["evaluation"]
        element_index = pattern_context.get("element_index", None)
        element_count = pattern_context.get("element_count", None)
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]

        if expression.has_form("Sequence", 0):
            if self.default is None:
                if head is None:  # head should be given by match_element!
                    default = None
                else:
                    name = head.get_name()
                    default = get_default_value(
                        name, evaluation, element_index, element_count
                    )
                if default is None:
                    evaluation.message(
                        "Pattern", "nodef", head, element_index, element_count
                    )
                    return
            else:
                default = self.default

            expression = default
        # for vars_2, rest in self.pattern.match(expression, vars_dict, evaluation):
        #    yield vars_2, rest
        self.pattern.match(
            expression,
            {
                "yield_func": yield_func,
                "vars_dict": vars_dict,
                "evaluation": evaluation,
            },
        )

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (0, 1)

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_order

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        sub = list(self.pattern.pattern_precedence)
        sub[0] &= PATTERN_SORT_KEY_OPTIONAL
        return tuple(sub)
