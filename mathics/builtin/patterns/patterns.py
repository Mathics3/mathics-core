# -*- coding: utf-8 -*-
"""
Defining patterns.
"""

from typing import Optional as OptionalType, Union

from mathics.core.atoms import Integer, Number, Rational, Real, String
from mathics.core.attributes import A_HOLD_ALL, A_HOLD_FIRST, A_HOLD_REST, A_PROTECTED
from mathics.core.builtin import BinaryOperator, Builtin, PatternObject, Test
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, SymbolVerbatim
from mathics.core.pattern import BasePattern, StopGenerator
from mathics.core.symbols import Atom, SymbolTrue
from mathics.core.systemsymbols import SymbolBlank

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.patterns"


class PatternTest(BinaryOperator, PatternObject):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PatternTest.html</url>

    <dl>
      <dt>'PatternTest[$pattern$, $test$]'
      <dt>'$pattern$ ? $test$'
      <dd>constrains $pattern$ to match $expr$ only if the
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
    operator = "?"
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

        builtin = None
        builtin = evaluation.definitions.get_definition(test)
        if builtin:
            builtin = builtin.builtin
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

    def get_match_count(self, vars_dict: OptionalType[dict] = None):
        return self.pattern.get_match_count(vars_dict)


class Alternatives(BinaryOperator, PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Alternatives.html</url>

    <dl>
      <dt>'Alternatives[$p1$, $p2$, ..., $p_i$]'
      <dt>'$p1$ | $p2$ | ... | $p_i$'
      <dd>is a pattern that matches any of the patterns '$p1$, $p2$,
        ...., $p_i$'.
    </dl>

    >> a+b+c+d/.(a|b)->t
     = c + d + 2 t

    Alternatives can also be used for string expressions
    >> StringReplace["0123 3210", "1" | "2" -> "X"]
     = 0XX3 3XX0
    """

    arg_counts = None
    needs_verbatim = True
    operator = "|"
    summary_text = "match to any of several patterns"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        self.alternatives = [
            BasePattern.create(element, evaluation=evaluation)
            for element in expr.elements
        ]

    def match(self, expression: Expression, pattern_context: dict):
        """Match with Alternatives"""
        for alternative in self.alternatives:
            # for new_vars_dict, rest in alternative.match(
            #     expression, vars_dict, evaluation):
            #     yield_func(new_vars_dict, rest)
            alternative.match(expression, pattern_context)

    def get_match_count(
        self, vars_dict: OptionalType[dict] = None
    ) -> Union[None, int, tuple]:
        range_lst = None
        for alternative in self.alternatives:
            sub = alternative.get_match_count(vars_dict)
            if range_lst is None:
                range_lst = tuple(sub)
            else:
                if sub[0] < range_lst[0]:
                    range_lst[0] = sub[0]
                if range_lst[1] is None or sub[1] > range_lst[1]:
                    range_lst[1] = sub[1]
        return tuple(range_lst)


class _StopGeneratorExcept(StopGenerator):
    pass


class Except(PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Except.html</url>

    <dl>
      <dt>'Except[$c$]'
      <dd>represents a pattern object that matches any expression except \
          those matching $c$.

      <dt>'Except[$c$, $p$]'
      <dd>represents a pattern object that matches $p$ but not $c$.
    </dl>

    >> Cases[{x, a, b, x, c}, Except[x]]
     = {a, b, c}

    >> Cases[{a, 0, b, 1, c, 2, 3}, Except[1, _Integer]]
     = {0, 2, 3}

    Except can also be used for string expressions:
    >> StringReplace["Hello world!", Except[LetterCharacter] -> ""]
     = Helloworld
    """

    arg_counts = [1, 2]
    summary_text = "match to expressions that do not match with a pattern"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        self.c = BasePattern.create(expr.elements[0], evaluation=evaluation)
        if len(expr.elements) == 2:
            self.p = BasePattern.create(expr.elements[1], evaluation=evaluation)
        else:
            self.p = BasePattern.create(Expression(SymbolBlank), evaluation=evaluation)

    def match(self, expression: Expression, pattern_context: dict):
        """Match with Exception Pattern"""

        def except_yield_func(vars_dict, rest):
            raise _StopGeneratorExcept(True)

        new_pattern_context = pattern_context.copy()
        new_pattern_context["yield_func"] = except_yield_func

        try:
            self.c.match(expression, new_pattern_context)
        except _StopGeneratorExcept:
            pass
        else:
            self.p.match(expression, pattern_context)


class Verbatim(PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Verbatim.html</url>

    <dl>
      <dt>'Verbatim[$expr$]'
      <dd>prevents pattern constructs in $expr$ from taking effect,
        allowing them to match themselves.
    </dl>

    Create a pattern matching 'Blank':
    >> _ /. Verbatim[_]->t
     = t
    >> x /. Verbatim[_]->t
     = x

    Without 'Verbatim', 'Blank' has its normal effect:
    >> x /. _->t
     = t
    """

    arg_counts = [1, 2]
    summary_text = "take the pattern elements as literals"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        self.content = expr.elements[0]

    def match(self, expression: Expression, pattern_context: dict):
        """Match with Verbatim Pattern"""
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]

        if self.content.sameQ(expression):
            yield_func(vars_dict, None)


class HoldPattern(PatternObject):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/HoldPattern.html</url>

    <dl>
      <dt>'HoldPattern[$expr$]'
      <dd>is equivalent to $expr$ for pattern matching, but
        maintains it in an unevaluated form.
    </dl>

    >> HoldPattern[x + x]
     = HoldPattern[x + x]
    >> x /. HoldPattern[x] -> t
     = t

    'HoldPattern' has attribute 'HoldAll':
    >> Attributes[HoldPattern]
     = {HoldAll, Protected}
    """

    arg_counts = [1]
    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "took the expression as a literal pattern"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        self.pattern = BasePattern.create(expr.elements[0], evaluation=evaluation)

    def match(self, expression: Expression, pattern_context: dict):
        # for new_vars_dict, rest in self.pattern.match(
        #     expression, vars_dict, evaluation):
        #     yield new_vars_dict, rest
        self.pattern.match(expression, pattern_context)


class Pattern(PatternObject):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Pattern.html</url>

    <dl>
      <dt>'Pattern[$symb$, $patt$]'
      <dt>'$symb$ : $patt$'
      <dd>assigns the name $symb$ to the pattern $patt$.
      <dt>'$symb$_$head$'
      <dd>is equivalent to '$symb$ : _$head$' (accordingly with '__'
        and '___').
      <dt>'$symb$ : $patt$ : $default$'
      <dd>is a pattern with name $symb$ and default value $default$,
        equivalent to 'Optional[$patt$ : $symb$, $default$]'.
    </dl>

    >> FullForm[a_b]
     = Pattern[a, Blank[b]]
    >> FullForm[a:_:b]
     = Optional[Pattern[a, Blank[]], b]

    'Pattern' has attribute 'HoldFirst', so it does not evaluate its name:
    >> x = 2
     = 2
    >> x_
     = x_

    Nested 'Pattern' assign multiple names to the same pattern. Still,
    the last parameter is the default value.
    >> f[y] /. f[a:b,_:d] -> {a, b}
     = f[y]
    This is equivalent to:
    >> f[a] /. f[a:_:b] -> {a, b}
     = {a, b}
    'FullForm':
    >> FullForm[a:b:c:d:e]
     = Optional[Pattern[a, b], Optional[Pattern[c, d], e]]

    >> f[] /. f[a:_:b] -> {a, b}
     = {b, b}
    """

    name = "Pattern"

    arg_counts = [2]

    attributes = A_HOLD_FIRST | A_PROTECTED

    messages = {
        "patvar": "First element in pattern `1` is not a valid pattern name.",
        "nodef": (
            "No default setting found for `1` in " "position `2` when length is `3`."
        ),
    }

    rules = {
        (
            "MakeBoxes[Verbatim[Pattern][symbol_Symbol, blank_Blank|"
            "blank_BlankSequence|blank_BlankNullSequence], "
            "f:StandardForm|TraditionalForm|InputForm|OutputForm]"
        ): "MakeBoxes[symbol, f] <> MakeBoxes[blank, f]",
        # 'StringForm["`1``2`", HoldForm[symbol], blank]',
    }

    formats = {
        "Verbatim[Pattern][symbol_, "
        "pattern_?(!MatchQ[#, _Blank|_BlankSequence|_BlankNullSequence]&)]": (
            'Infix[{symbol, pattern}, ":", 150, Left]'
        )
    }
    summary_text = "a named pattern"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        if len(expr.elements) != 2:
            self.error("patvar", expr)
        varname = expr.elements[0].get_name()
        if varname is None or varname == "":
            self.error("patvar", expr)
        super().init(expr, evaluation=evaluation)
        self.varname = varname
        self.pattern = BasePattern.create(expr.elements[1], evaluation=evaluation)

    def __repr__(self):
        return "<Pattern: %s>" % repr(self.pattern)

    def get_match_count(
        self, vars_dict: OptionalType[dict] = None
    ) -> Union[int, tuple]:
        return self.pattern.get_match_count(vars_dict)

    def match(self, expression: Expression, pattern_context: dict):
        """Match with a (named) pattern"""
        from mathics.builtin.patterns.options import OptionsPattern

        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]

        existing = vars_dict.get(self.varname, None)
        if existing is None:
            new_vars_dict = vars_dict.copy()
            new_vars_dict[self.varname] = expression
            pattern_context = pattern_context.copy()
            pattern_context["vars_dict"] = new_vars_dict
            # for vars_2, rest in self.pattern.match(
            #    expression, new_vars_dict, evaluation):
            #    yield vars_2, rest
            if isinstance(self.pattern, OptionsPattern):
                self.pattern.match(
                    expression=expression, pattern_context=pattern_context
                )
            else:
                self.pattern.match(
                    expression=expression, pattern_context=pattern_context
                )
        else:
            if existing.sameQ(expression):
                yield_func(vars_dict, None)

    def get_match_candidates(self, elements: tuple, pattern_context: dict) -> tuple:
        """
        Return a sub-tuple of elements that match with
        the pattern.
        Optional parameters provide information
        about the context where the elements and the
        patterns come from.
        """
        vars_dict = pattern_context.get("vars_dict", {})

        existing = vars_dict.get(self.varname, None)
        if existing is None:
            return self.pattern.get_match_candidates(elements, pattern_context)

        # Treat existing variable as verbatim
        verbatim_expr = Expression(SymbolVerbatim, existing)
        verbatim = Verbatim(verbatim_expr)
        return verbatim.get_match_candidates(elements, pattern_context)


class Shortest(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Shortest.html</url>

    <dl>
      <dt>'Shortest[$pat$]'
      <dd>is a pattern object that matches the shortest sequence consistent with the pattern $p$.
    </dl>

    >> StringCases["aabaaab", Shortest["a" ~~ __ ~~ "b"]]
     =  {aab, aaab}

    >> StringCases["aabaaab", Shortest[RegularExpression["a+b"]]]
     = {aab, aaab}
    """

    summary_text = "the shortest part matching a string pattern"


class Longest(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Longest.html</url>

    <dl>
      <dt>'Longest[$pat$]'
      <dd>is a pattern object that matches the longest sequence consistent \
      with the pattern $p$.
    </dl>

    >> StringCases["aabaaab", Longest["a" ~~ __ ~~ "b"]]
     = {aabaaab}

    >> StringCases["aabaaab", Longest[RegularExpression["a+b"]]]
     = {aab, aaab}
    """

    summary_text = "the longest part matching a string pattern"


class Condition(BinaryOperator, PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Condition.html</url>

    <dl>
      <dt>'Condition[$pattern$, $expr$]'
      <dt>'$pattern$ /; $expr$'
      <dd>places an additional constraint on $pattern$ that only
        allows it to match if $expr$ evaluates to 'True'.
    </dl>

    The controlling expression of a 'Condition' can use variables from
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
    operator = "/;"
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
