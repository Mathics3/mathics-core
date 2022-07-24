#!/usr/bin/env python3
# cython: language_level=3
# -*- coding: utf-8 -*-

from mathics.core.element import KeyComparable
from mathics.core.expression import Expression
from mathics.core.symbols import strip_context
from mathics.core.pattern import Pattern, StopGenerator
from mathics.core.util import function_arguments

from itertools import chain


class StopGenerator_BaseRule(StopGenerator):
    pass


class BaseRule(KeyComparable):
    """
    This is the base class from which all other Rules are derived from.

    Rules are part of the rewriting system of Mathics. See https://en.wikipedia.org/wiki/Rewriting

    This class is not complete in of itself and subclasses should adapt or fill in
    what is needed. In particular ``do_replace()`` needs to be implemented.

    Important subclasses: BuiltinRule and Rule.
    """

    def __init__(self, pattern, system=False) -> None:
        self.pattern = Pattern.create(pattern)
        self.system = system

    def apply(
        self, expression, evaluation, fully=True, return_list=False, max_list=None
    ):
        result_list = []
        # count = 0

        if return_list and max_list is not None and max_list <= 0:
            return []

        def yield_match(vars, rest):
            if rest is None:
                rest = ([], [])
            if 0 < len(rest[0]) + len(rest[1]) == len(expression.get_elements()):
                # continue
                return
            options = {}
            for name, value in list(vars.items()):
                if name.startswith("_option_"):
                    options[name[len("_option_") :]] = value
                    del vars[name]
            new_expression = self.do_replace(expression, vars, options, evaluation)
            if new_expression is None:
                new_expression = expression
            if rest[0] or rest[1]:
                result = Expression(
                    expression.get_head(),
                    *list(chain(rest[0], [new_expression], rest[1]))
                )
            else:
                result = new_expression

            if isinstance(result, Expression):
                if result.elements_properties is None:
                    result._build_elements_properties()
                # Flatten out sequences (important for Rule itself!)
                result = result.flatten_pattern_sequence(evaluation)
            if return_list:
                result_list.append(result)
                # count += 1
                if max_list is not None and len(result_list) >= max_list:
                    # return result_list
                    raise StopGenerator_BaseRule(result_list)
            else:
                raise StopGenerator_BaseRule(result)

                # only first possibility counts

        try:
            self.pattern.match(yield_match, expression, {}, evaluation, fully=fully)
        except StopGenerator_BaseRule as exc:
            # FIXME: figure where these values are not getting set or updated properly.
            # For now we have to take a pessimistic view
            expr = exc.value
            # FIXME: expr is sometimes a list - why the changing types
            if hasattr(expr, "_elements_fully_evaluated"):
                expr._elements_fully_evaluated = False
                expr._is_flat = False  # I think this is fully updated
                expr._is_ordered = False
            return expr

        if return_list:
            return result_list
        else:
            return None

    def do_replace(self):
        raise NotImplementedError

    def get_sort_key(self) -> tuple:
        # FIXME: check if this makes sense:
        return tuple((self.system, self.pattern.get_sort_key(True)))


class Rule(BaseRule):
    """
    There are two kinds of Rules.  This kind of Rule transforms an
    Expression into another Expression based on the pattern and a
    replacement term and doesn't involve function application.

    Also, in contrast to BuiltinRule[], rule application cannot force
    a reevaluation of the expression when the rewrite/apply/eval step
    finishes.

    Here is an example of a Rule::
        F[x_] -> x^2   (* The same thing as: Rule[x_, x^2] *)


    ``F[x_]`` is a pattern and ``x^2`` is the replacement term. When
    applied to the expression ``G[F[1.], F[a]]`` the result is
    ``G[1.^2, a^2]``
    """

    def __init__(self, pattern, replace, system=False) -> None:
        super(Rule, self).__init__(pattern, system=system)
        self.replace = replace

    def do_replace(self, expression, vars, options, evaluation):
        new = self.replace.replace_vars(vars)
        new.options = options

        # if options is a non-empty dict, we need to ensure reevaluation of the whole expression, since 'new' will
        # usually contain one or more matching OptionValue[symbol_] patterns that need to get replaced with the
        # options' values. this is achieved through Expression.evaluate(), which then triggers OptionValue.apply,
        # which in turn consults evaluation.options to return an option value.

        # in order to get there, we copy 'new' using copy(reevaluate=True), as this will ensure that the whole thing
        # will get reevaluated.

        # if the expression contains OptionValue[] patterns, but options is empty here, we don't need to act, as the
        # expression won't change in that case. the Expression.options would be None anyway, so OptionValue.apply
        # would just return the unchanged expression (which is what we have already).

        if options:
            new = new.copy(reevaluate=True)

        return new

    def __repr__(self) -> str:
        return "<Rule: %s -> %s>" % (self.pattern, self.replace)


class BuiltinRule(BaseRule):
    """
    A BuiltinRule is a rule that has a replacement term that is associated
    a Python function rather than a Mathics Expression as happens in a Rule.

    Each time the Pattern part of the Rule matches an Expression, the
    matching subexpression is replaced by the expression returned
    by application of that function to the remaining terms.

    Parameters for the function are bound to parameters matched by the pattern.

    Here is an example taken from the symbol ``System`Plus``.
    It has has associated a BuiltinRule::

        Plus[items___] -> mathics.builtin.arithfns.basic.Plus.apply

    The pattern ``items___`` matches a list of Expressions.

    When applied to the expression ``F[a+a]`` the method ``mathics.builtin.arithfns.basic.Plus.apply`` is called
    binding the parameter  ``items`` to the value ``Sequence[a,a]``.

    The return value of this function is ``Times[2, a]`` (or more compactly: ``2*a``).
    When replaced in the original expression, the result is: ``F[2*a]``.

    In contrast to Rule, BuiltinRules can change the state of definitions
    in the the system.

    For example, the rule::

        SetAttributes[a_,b_] -> mathics.builtin.attributes.SetAttributes.apply

    when applied to the expression ``SetAttributes[F,  NumericFunction]``

    sets the attribute ``NumericFunction`` in the  definition of the symbol ``F`` and returns Null (``SymbolNull`)`.

    This will cause `Expression.evalate() to perform an additional ``rewrite_apply_eval()`` step.
    """

    def __init__(self, name, pattern, function, check_options, system=False) -> None:
        super(BuiltinRule, self).__init__(pattern, system=system)
        self.name = name
        self.function = function
        self.check_options = check_options
        self.pass_expression = "expression" in function_arguments(function)

    # If you update this, you must also update traced_do_replace
    # (that's in the same file TraceBuiltins is)
    def do_replace(self, expression, vars, options, evaluation):
        if options and self.check_options:
            if not self.check_options(options, evaluation):
                return None
        # The Python function implementing this builtin expects
        # argument names corresponding to the symbol names without
        # context marks.
        vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
        if self.pass_expression:
            vars_noctx["expression"] = expression
        if options:
            return self.function(evaluation=evaluation, options=options, **vars_noctx)
        else:
            return self.function(evaluation=evaluation, **vars_noctx)

    def __repr__(self) -> str:
        return "<BuiltinRule: %s -> %s>" % (self.pattern, self.function)

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["function"]
        odict["function_"] = (self.function.__self__.get_name(), self.function.__name__)
        return odict

    def __setstate__(self, dict):
        from mathics.builtin import builtins

        self.__dict__.update(dict)  # update attributes
        cls, name = dict["function_"]

        self.function = getattr(builtins[cls], name)
