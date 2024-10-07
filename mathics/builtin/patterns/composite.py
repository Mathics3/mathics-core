# -*- coding: utf-8 -*-
"""
Composite Patterns


"""

from typing import Optional as OptionalType, Union

from mathics.core.attributes import A_HOLD_ALL, A_HOLD_FIRST, A_PROTECTED
from mathics.core.builtin import BinaryOperator, Builtin, PatternObject, PostfixOperator
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, SymbolVerbatim
from mathics.core.pattern import BasePattern, StopGenerator
from mathics.core.systemsymbols import SymbolBlank

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.composite"


class _StopGeneratorExcept(StopGenerator):
    pass


class Alternatives(BinaryOperator, PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Alternatives.html</url>

    <dl>
      <dt>'Alternatives[$p1$, $p2$, ..., $p_i$]'
      <dt>'$p1$ | $p2$ | ... | $p_i$'
      <dd>is a pattern that matches any of the patterns $p1$, $p2$, \
        ...., $p_i$.
    </dl>

    >> a+b+c+d/.(a|b)->t
     = c + d + 2 t

    Alternatives can also be used for string expressions:
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


class HoldPattern(PatternObject):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/HoldPattern.html</url>

    <dl>
      <dt>'HoldPattern[$expr$]'
      <dd>is equivalent to $expr$ for pattern matching, but \
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


class Longest(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Longest.html</url>

    <dl>
      <dt>'Longest[$pattern$]'
      <dd>is a pattern object that matches the longest sequence consistent \
      with the pattern $p$.
    </dl>

    >> StringCases["aabaaab", Longest["a" ~~ __ ~~ "b"]]
     = {aabaaab}

    >> StringCases["aabaaab", Longest[RegularExpression["a+b"]]]
     = {aab, aaab}
    """

    summary_text = "the longest part matching a string pattern"


class Pattern(PatternObject):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Pattern.html</url>

    <dl>
      <dt>'Pattern[$symb$, $pattern$]'
      <dt>'$symb$ : $pattern$'
      <dd>assigns the name $symb$ to the pattern $pattern$.
      <dt>'$symb$_$head$'
      <dd>is equivalent to '$symb$ : _$head$' (accordingly with '__' \
        and '___').
      <dt>'$symb$ : $pattern$ : $default$'
      <dd>is a pattern with name $symb$ and default value $default$, \
        equivalent to 'Optional[$pattern$ : $symb$, $default$]'.
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

    Nested 'Pattern' assigns multiple names to the same pattern. Still, \
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
        from mathics.builtin.patterns.defaults import OptionsPattern

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


class Repeated(PostfixOperator, PatternObject):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Repeated.html</url>

    <dl>
      <dt>'Repeated[$pattern$]'
      <dd>matches one or more occurrences of $pattern$.
    </dl>

    >> a_Integer.. // FullForm
     = Repeated[Pattern[a, Blank[Integer]]]
    >> 0..1//FullForm
     = Repeated[0]
    >> {{}, {a}, {a, b}, {a, a, a}, {a, a, a, a}} /. {Repeated[x : a | b, 3]} -> x
     = {{}, a, {a, b}, a, {a, a, a, a}}
    >> f[x, 0, 0, 0] /. f[x, s:0..] -> s
     = Sequence[0, 0, 0]
    """

    arg_counts = [1, 2]
    messages = {
        "range": (
            "Range specification in integers (max or {min, max}) "
            "expected at position `1` in `2`."
        )
    }

    operator = ".."
    summary_text = "match to one or more occurrences of a pattern"

    def init(
        self,
        expr: Expression,
        min_idx: int = 1,
        evaluation: OptionalType[Evaluation] = None,
    ):
        self.pattern = BasePattern.create(expr.elements[0], evaluation=evaluation)
        self.max = None
        self.min = min_idx
        if len(expr.elements) == 2:
            element_1 = expr.elements[1]
            allnumbers = not any(
                element.get_int_value() is None for element in element_1.get_elements()
            )
            if element_1.has_form("List", 1, 2) and allnumbers:
                self.max = element_1.elements[-1].get_int_value()
                self.min = element_1.elements[0].get_int_value()
            elif element_1.get_int_value():
                self.max = element_1.get_int_value()
            else:
                self.error("range", 2, expr)

    def match(self, expression: Expression, pattern_context: dict):
        """Match with Repeated[...]"""
        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]
        evaluation = pattern_context["evaluation"]
        elements = expression.get_sequence()
        if len(elements) < self.min:
            return
        if self.max is not None and len(elements) > self.max:
            return

        def iter_fn(yield_iter, rest_elements, vars_dict):
            if rest_elements:
                # for new_vars_dict, rest in self.pattern.match(rest_elements[0],
                # vars_dict, evaluation):
                def yield_match(new_vars_dict, rest):
                    # for sub_vars_dict, sub_rest in iter(rest_elements[1:],
                    #                                new_vars):
                    #    yield sub_vars_dict, rest
                    iter_fn(yield_iter, rest_elements[1:], new_vars_dict)

                self.pattern.match(
                    rest_elements[0],
                    {
                        "yield_func": yield_match,
                        "vars_dict": vars_dict,
                        "evaluation": evaluation,
                    },
                )
            else:
                yield_iter(vars_dict, None)

        # for vars_dict, rest in iter(elements, vars):
        #    yield_func(vars_dict, rest)
        iter_fn(yield_func, elements, vars_dict)

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (self.min, self.max)


class RepeatedNull(Repeated):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RepeatedNull.html</url>

    <dl>
      <dt>'RepeatedNull[$pattern$]'
      <dd>matches zero or more occurrences of $pattern$.
    </dl>

    >> a___Integer...//FullForm
     = RepeatedNull[Pattern[a, BlankNullSequence[Integer]]]
    >> f[x] /. f[x, 0...] -> t
     = t
    """

    operator = "..."
    summary_text = "match to zero or more occurrences of a pattern"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, min_idx=0, evaluation=evaluation)


class Shortest(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Shortest.html</url>

    <dl>
      <dt>'Shortest[$pattern$]'
      <dd>is a pattern object that matches the shortest sequence consistent with the pattern $p$.
    </dl>

    >> StringCases["aabaaab", Shortest["a" ~~ __ ~~ "b"]]
     =  {aab, aaab}

    >> StringCases["aabaaab", Shortest[RegularExpression["a+b"]]]
     = {aab, aaab}
    """

    summary_text = "the shortest part matching a string pattern"


class Verbatim(PatternObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Verbatim.html</url>

    <dl>
      <dt>'Verbatim[$expr$]'
      <dd>prevents pattern constructs in $expr$ from taking effect, \
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


# TODO: Implement `KeyValuePattern` and `OrderlessPatternSequence`
