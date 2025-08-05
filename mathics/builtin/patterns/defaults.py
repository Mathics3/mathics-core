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
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Optional.html</url>

    <dl>
      <dt>'Optional'[$pattern$, $default$]
      <dt>'$pattern$ : $default$'
      <dd>is a pattern which matches $pattern$, which if omitted
        should be replaced by $default$.
    </dl>

    >> f[x_, y_:1] := {x, y}
    >> f[1, 2]
     = {1, 2}
    >> f[a]
     = {a, 1}

    Note that '$symb$ : $pattern$' represents a 'Pattern' object. However, there is no
    disambiguity, since $symb$ has to be a symbol in this case.

    >> x:_ // FullForm
     = Pattern[x, Blank[]]
    >> _:d // FullForm
     = Optional[Blank[], d]
    >> x:_+y_:d // FullForm
     = Pattern[x, Plus[Blank[], Optional[Pattern[y, Blank[]], d]]]

    's_.' is equivalent to 'Optional[s_]' and represents an optional parameter which, if omitted,
    gets its value from 'Default'.
    >> FullForm[s_.]
     = Optional[Pattern[s, Blank[]]]

    >> Default[h, k_] := k
    >> h[a] /. h[x_, y_.] -> {x, y}
     = {a, 2}
    """

    arg_counts = [1, 2]

    default_formats = False

    formats = {
        "Verbatim[Optional][pattern_Pattern, default_]": 'Infix[{HoldForm[pattern], HoldForm[default]}, ":", 140, Right]'
    }
    grouping = "Right"
    rules = {
        "MakeBoxes[Verbatim[Optional][Verbatim[Pattern][symbol_Symbol, Verbatim[_]]], f:StandardForm|TraditionalForm|InputForm|OutputForm]": 'MakeBoxes[symbol, f] <> "_."',
        "MakeBoxes[Verbatim[Optional][Verbatim[_]], f:StandardForm|TraditionalForm|InputForm|OutputForm]": '"_."',
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
    def element_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_precedence

    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        sub = list(self.pattern.get_sort_key(True))
        sub[0] &= PATTERN_SORT_KEY_OPTIONAL
        return tuple(sub)

    def get_sort_key(self, pattern_sort=True):
        if not pattern_sort:
            return self.expr.get_sort_key()

        sub = list(self.pattern.get_sort_key(True))
        sub[0] &= PATTERN_SORT_KEY_OPTIONAL
        return tuple(sub)
