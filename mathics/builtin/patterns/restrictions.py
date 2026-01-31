# -*- coding: utf-8 -*-
"""
Restrictions on Patterns


"""
from typing import Optional as OptionalType, Tuple

from mathics.core.atoms import Integer, Number, Rational, Real, String
from mathics.core.attributes import A_HOLD_REST, A_PROTECTED
from mathics.core.builtin import InfixOperator, PatternObject, Test
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.keycomparable import (
    PATTERN_SORT_KEY_CONDITIONAL,
    PATTERN_SORT_KEY_PATTERNTEST,
)
from mathics.core.pattern import BasePattern
from mathics.core.symbols import Atom, SymbolTrue

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.restrictions"


class Condition(InfixOperator, PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Condition.html</url>

    <dl>
      <dt>'Condition'[$pattern$, $expr$]
      <dt>'$pattern$ /; $expr$'
      <dd>places an additional constraint on $pattern$ that only \
          allows it to match if $expr$ evaluates to 'True'.
    </dl>

    The controlling expression of a 'Condition' can use variables from \
    the pattern:
    >> f[3] /. f[x_] /; x>0 -> t
     = t
    >> f[-3] /. f[x_] /; x>0 -> t
     = f[-3]

    'Condition' can be used in an assignment:
    >> f[x_] := p[x] /; x>0
    >> f[3]
     = p[3]
    >> f[-3]
     = f[-3]
    """

    arg_counts = [2]
    # Don't know why this has attribute HoldAll in Mathematica
    attributes = A_HOLD_REST | A_PROTECTED
    summary_text = "conditional definition"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        self.test = expr.elements[1]
        # if (expr.elements[0].get_head_name() == "System`Condition" and
        #    len(expr.elements[0].elements) == 2):
        #    self.test = Expression(SymbolAnd, self.test, expr.elements[0].elements[1])
        #    self.pattern = BasePattern.create(expr.elements[0].elements[0])
        # else:
        self.pattern = BasePattern.create(expr.elements[0], evaluation=evaluation)

    def match(self, expression: Expression, pattern_context: dict):
        """Match with Condition pattern"""
        # for new_vars_dict, rest in self.pattern.match(expression, vars_dict,
        # evaluation):
        evaluation = pattern_context["evaluation"]
        yield_func = pattern_context["yield_func"]

        def yield_match(new_vars_dict, rest):
            test_expr = self.test.replace_vars(new_vars_dict)
            test_result = test_expr.evaluate(evaluation)
            if test_result is SymbolTrue:
                yield_func(new_vars_dict, rest)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

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
        # Remove the bit "inconditional" to increase
        # the priority of this pattern.
        sub[0] &= PATTERN_SORT_KEY_CONDITIONAL
        return tuple(sub)


class PatternTest(InfixOperator, PatternObject):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PatternTest.html</url>

    <dl>
      <dt>'PatternTest'[$pattern$, $test$]
      <dt>'$pattern$ ? $test$'
      <dd>constrains $pattern$ to match $expr$ only if the \
          evaluation of '$test$[$expr$]' yields 'True'.
    </dl>

    >> MatchQ[3, _Integer?(#>0&)]
     = True
    >> MatchQ[-3, _Integer?(#>0&)]
     = False
    >> MatchQ[3, Pattern[3]]
     : First element in pattern Pattern[3] is not a valid pattern name.
     = False
    """

    arg_counts = [2]
    summary_text = "match to a pattern conditioned to a test result"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        # This class has an important effect in the general performance,
        # since all the rules that requires specify the type of patterns
        # call it. Then, for simple checks like `NumberQ` or `NumericQ`
        # it is important to have the fastest possible implementation.
        # To to this, we overwrite the match method taking it from the
        # following dictionary. Here also would get some advantage by
        # singletonizing the Symbol class and accessing this dictionary
        # using an id() instead a string...

        match_functions = {
            "System`AtomQ": self.match_atom,
            "System`StringQ": self.match_string,
            "System`NumericQ": self.match_numericq,
            "System`NumberQ": self.match_numberq,
            "System`RealValuedNumberQ": self.match_real_numberq,
            "Internal`RealValuedNumberQ": self.match_real_numberq,
            "System`Posive": self.match_positive,
            "System`Negative": self.match_negative,
            "System`NonPositive": self.match_nonpositive,
            "System`NonNegative": self.match_nonnegative,
        }

        self.pattern = BasePattern.create(expr.elements[0], evaluation=evaluation)
        self.test = expr.elements[1]
        testname = self.test.get_name()
        self.test_name = testname
        match_function = match_functions.get(testname, None)
        if match_function:
            self.match = match_function

    def match_atom(self, expression: Expression, pattern_context: dict):
        """Match function for AtomQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            # Here we use a `for` loop instead an all over iterator
            # because in Cython this is faster, since it avoids a function
            # call. For pure Python, it is the opposite.
            for item in items:
                if not isinstance(item, Atom):
                    break
            else:
                yield_func(vars_2, None)

        # TODO: clarify why we need to use copy here.
        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_string(self, expression: Expression, pattern_context: dict):
        """Match function for StringQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            for item in items:
                if not isinstance(item, String):
                    break
            else:
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_numberq(self, expression: Expression, pattern_context: dict):
        """Match function for NumberQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            for item in items:
                if not isinstance(item, Number):
                    break
            else:
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_numericq(self, expression: Expression, pattern_context: dict):
        """Match function for NumericQ"""
        yield_func = pattern_context["yield_func"]
        evaluation = pattern_context["evaluation"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            for item in items:
                if not (isinstance(item, Number) or item.is_numeric(evaluation)):
                    break
            else:
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_real_numberq(self, expression: Expression, pattern_context: dict):
        """Match function for RealValuedNumberQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            for item in items:
                if not isinstance(item, (Integer, Rational, Real)):
                    break
            else:
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_positive(self, expression: Expression, pattern_context: dict):
        """Match function for PositiveQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            if all(
                isinstance(item, (Integer, Rational, Real)) and item.value > 0
                for item in items
            ):
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_negative(self, expression: Expression, pattern_context: dict):
        """Match function for NegativeQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            if all(
                isinstance(item, (Integer, Rational, Real)) and item.value < 0
                for item in items
            ):
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_nonpositive(self, expression: Expression, pattern_context: dict):
        """Match function for NonPositiveQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            if all(
                isinstance(item, (Integer, Rational, Real)) and item.value <= 0
                for item in items
            ):
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def match_nonnegative(self, expression: Expression, pattern_context: dict):
        """Match function for NonNegativeQ"""
        yield_func = pattern_context["yield_func"]

        def yield_match(vars_2, rest):
            items = expression.get_sequence()
            if all(
                isinstance(item, (Integer, Rational, Real)) and item.value >= 0
                for item in items
            ):
                yield_func(vars_2, None)

        pattern_context = pattern_context.copy()
        pattern_context["yield_func"] = yield_match
        self.pattern.match(expression, pattern_context)

    def quick_pattern_test(self, candidate, test, evaluation: Evaluation):
        """Pattern test for some other special cases"""
        if test == "System`NegativePowerQ":
            return (
                candidate.has_form("Power", 2)
                and isinstance(candidate.elements[1], (Integer, Rational, Real))
                and candidate.elements[1].value < 0
            )
        if test == "System`NotNegativePowerQ":
            return not (
                candidate.has_form("Power", 2)
                and isinstance(candidate.elements[1], (Integer, Rational, Real))
                and candidate.elements[1].value < 0
            )

        try:
            builtin = evaluation.definitions.get_definition(test, True).builtin
        except KeyError:
            return None

        if builtin is not None and isinstance(builtin, Test):
            return builtin.test(candidate)
        return None

    def match(self, expression: Expression, pattern_context: dict):
        """Match expression with PatternTest"""
        evaluation = pattern_context["evaluation"]
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]

        # def match(self, yield_func, expression, vars_dict, evaluation, **kwargs):
        # for vars_2, rest in self.pattern.match(expression, vars_dict, evaluation):
        def yield_match(vars_2, rest):
            testname = self.test_name
            items = expression.get_sequence()
            for item in items:
                item = item.evaluate(evaluation)
                quick_test = self.quick_pattern_test(item, testname, evaluation)
                if quick_test is False:
                    break
                if quick_test is True:
                    continue
                    # raise StopGenerator
                test_expr = Expression(self.test, item)
                test_value = test_expr.evaluate(evaluation)
                if test_value is not SymbolTrue:
                    break
                    # raise StopGenerator
            else:
                yield_func(vars_2, None)

        # try:
        self.pattern.match(
            expression,
            {
                "yield_func": yield_match,
                "vars_dict": vars_dict,
                "evaluation": evaluation,
            },
        )
        # except StopGenerator:
        #    pass

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> Tuple[int, int]:
        return self.pattern.get_match_count(vars_dict)

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
        # Remove the bit "not pattern test" to increase
        # the priority of this pattern.
        sub[0] &= PATTERN_SORT_KEY_PATTERNTEST
        return tuple(sub)
