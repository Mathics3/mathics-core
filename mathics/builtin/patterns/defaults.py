# -*- coding: utf-8 -*-
"""
Pattern Defaults


"""

from typing import Optional as OptionalType, Tuple

from mathics.core.builtin import BinaryOperator, PatternObject
from mathics.core.element import BaseElement, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.pattern import BasePattern
from mathics.eval.patterns import get_default_value

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.defaults"


class Optional(BinaryOperator, PatternObject):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Optional.html</url>

    <dl>
      <dt>'Optional[$patt$, $default$]'
      <dt>'$patt$ : $default$'
      <dd>is a pattern which matches $patt$, which if omitted
        should be replaced by $default$.
    </dl>

    >> f[x_, y_:1] := {x, y}
    >> f[1, 2]
     = {1, 2}
    >> f[a]
     = {a, 1}

    Note that '$symb$ : $patt$' represents a 'Pattern' object. However, there is no
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
    operator = ":"
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


class OptionsPattern(PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OptionsPattern.html</url>

    <dl>
      <dt>'OptionsPattern[$f$]'
      <dd>is a pattern that stands for a sequence of options given \
        to a function, with default values taken from 'Options[$f$]'. \
        The options can be of the form '$opt$->$value$' or \
        '$opt$:>$value$', and might be in arbitrarily nested lists.

      <dt>'OptionsPattern[{$opt1$->$value1$, ...}]'
      <dd>takes explicit default values from the given list. The \
        list may also contain symbols $f$, for which 'Options[$f$]' is \
        taken into account; it may be arbitrarily nested. \
        'OptionsPattern[{}]' does not use any default values.
    </dl>

    The option values can be accessed using 'OptionValue'.

    >> f[x_, OptionsPattern[{n->2}]] := x ^ OptionValue[n]
    >> f[x]
     = x ^ 2
    >> f[x, n->3]
     = x ^ 3

    Delayed rules as options:
    >> e = f[x, n:>a]
     = x ^ a
    >> a = 5;
    >> e
     = x ^ 5

    Options might be given in nested lists:
    >> f[x, {{{n->4}}}]
     = x ^ 4
    """

    arg_counts = [0, 1]
    summary_text = "a sequence of optional named arguments"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        try:
            self.defaults = expr.elements[0]
        except IndexError:
            # OptionsPattern[] takes default options of the nearest enclosing
            # function. Set to not None in self.match
            self.defaults = None

    def match(self, expression: Expression, pattern_context: dict):
        """Match with an OptionsPattern"""
        head = pattern_context.get("head", None)
        evaluation = pattern_context["evaluation"]
        if self.defaults is None:
            self.defaults = head
            if self.defaults is None:
                # we end up here with OptionsPattern that do not have any
                # default options defined, e.g. with this code:
                # f[x:OptionsPattern[]] := x; f["Test" -> 1]
                # set self.defaults to an empty List, so we don't crash.
                self.defaults = ListExpression()
        defaults = self.defaults
        values = (
            defaults.get_option_values(
                evaluation, allow_symbols=True, stop_on_error=False
            )
            if isinstance(defaults, EvalMixin)
            else {}
        )
        sequence = expression.get_sequence()
        for options in sequence:
            option_values = (
                options.get_option_values(evaluation)
                if isinstance(options, EvalMixin)
                else None
            )
            if option_values is None:
                return
            values.update(option_values)
        new_vars_dict = pattern_context["vars_dict"].copy()
        for name, value in values.items():
            new_vars_dict["_option_" + name] = value
        pattern_context["yield_func"](new_vars_dict, None)

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (0, None)

    def get_match_candidates(
        self, elements: Tuple[BaseElement], pattern_context: dict
    ) -> tuple:
        """
        Return the sub-tuple of elements that matches with the pattern.
        """

        def _match(element: Expression):
            return element.has_form(("Rule", "RuleDelayed"), 2) or element.has_form(
                "List", None
            )

        return tuple((element for element in elements if _match(element)))
