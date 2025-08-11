# -*- coding: utf-8 -*-
"""Rules are a core part of the way Mathematica and Mathics3 execute a
program.

Expressions which are transformed by rewrite rules (AKA transformation
rules) are handed by the `Rule` class.

There are also rules for how to match, assign function parameter
arguments, and then apply a Python "evaluation" function to a Mathics3 Expression.
These kinds of rules are handled by objects in the `FunctionApplyRule` class.

This module contains the classes for these two types of rules.

In a `FunctionApplyRule` rule, the match status of a rule depends on the evaluation return.

For example, suppose that we try to apply rule `F[x_]->x^2` to the expression `F[2]`. The pattern part of the rule,`F[x_]` matches
the expression, `Blank[x]` (or `x_`) is replaced by `2`, giving the substitution expression `2^2`. Evaluation then stops
looking for other rules to be applied over `F[2]`.

On the other hand, suppose that we define a `FunctionApplyRule` that associates `F[x_]` with the function:

.. code-block:: python

    class MyFunction(Builtin):
        ...
        def eval_f(self, x, evaluation) -> Optional[Expression]:
            "F[x_]"   # pattern part of FunctionApplyRule
            if x>3:
                return Expression(SymbolPower, x, Integer2)
            return None

Then, if we apply the rule to `F[2]`, the function is evaluated returning `None`. Then, in the evaluation loop, we get the same
effect as if the pattern didn't match with the expression. The loop continues then with the next rule associated with `F`.

Why do things this way?

Sometimes, the cost of deciding if the rule match is similar to the cost of evaluating the function. Suppose for example a rule

   F[x_/;(G[x]>0)]:=G[x]

with G[x] a computationally expensive function. To decide if G[x] is larger than 0, we need to evaluate it,
and once we have evaluated it, just need to return its value.

Also, this allows us to handle several rules in the same function, without relying on our very slow pattern-matching routines.
In particular, this is used for for some critical low-level tasks like building lists in iterators, processing arithmetic expressions,
plotting functions, or evaluating derivatives and integrals.

"""


from abc import ABC
from inspect import signature
from itertools import chain
from typing import Callable, Optional

from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.keycomparable import PATTERN_SORT_KEY_CONDITIONAL, KeyComparable
from mathics.core.pattern import BasePattern, StopGenerator
from mathics.core.symbols import SymbolTrue, strip_context


def _python_function_arguments(f):
    return signature(f).parameters.keys()


def function_arguments(f):
    return _python_function_arguments(f)


class StopGenerator_BaseRule(StopGenerator):
    """
    Signals that there are no more rules to check for pattern matching
    """

    pass


class RuleApplicationFailed(Exception):
    """
    Exception raised when a condition fails
    in the RHS, indicating that the match have failed.
    """

    pass


class BaseRule(KeyComparable, ABC):
    """This is the base class from which the FunctionApplyRule and
    Rule classes are derived from.

    Rules are part of the rewriting system of Mathics3. See
    https://en.wikipedia.org/wiki/Rewriting

    This class is not complete in of itself; subclasses must adapt or
    fill in what is needed. In particular either ``apply_rule()`` or
    ``apply_function()`` need to be implemented.

    Note: we want Rules to be serializable so that we can dump and
    restore Rules in order to make startup time faster.
    """

    def __init__(
        self,
        pattern: BaseElement,
        system: bool = False,
        evaluation: Optional[Evaluation] = None,
        attributes: Optional[int] = None,
    ) -> None:
        self.location: Optional[Callable] = None
        self.pattern = BasePattern.create(
            pattern, attributes=attributes, evaluation=evaluation
        )
        self.system = system

    def apply(
        self,
        expression: BaseElement,
        evaluation: Evaluation,
        fully: bool = True,
        return_list: bool = False,
        max_list: Optional[int] = None,
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
            apply_fn = (
                self.apply_function
                if isinstance(self, FunctionApplyRule)
                else self.apply_rule
            )
            try:
                new_expression = apply_fn(expression, vars, options, evaluation)
            except RuleApplicationFailed:
                return None
            if rest[0] or rest[1]:
                result = Expression(
                    expression.get_head(),
                    *list(chain(rest[0], [new_expression], rest[1])),
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
            self.pattern.match(
                expression,
                pattern_context={
                    "yield_func": yield_match,
                    "vars_dict": {},
                    "evaluation": evaluation,
                    "fully": fully,
                },
            )
        except StopGenerator_BaseRule as exc:
            # FIXME: figure where these values are not getting set or updated properly.
            # For now we have to take a pessimistic view
            expr = exc.value
            # FIXME: expr is sometimes a list - why the changing types
            if hasattr(expr, "_elements_fully_evaluated"):
                expr._elements_fully_evaluated = False
                expr._is_flat = False  # I think this is fully updated
                expr._is_ordered = False
            if (
                hasattr(expression, "location")
                and hasattr(expr, "location")
                and expression.location is not None
            ):
                expr.location = expression.location
            return expr

        if return_list:
            return result_list
        else:
            return None

    def apply_rule(
        self, expression: BaseElement, vars: dict, options: dict, evaluation: Evaluation
    ):
        raise NotImplementedError

    def apply_function(
        self, expression: BaseElement, vars: dict, options: dict, evaluation: Evaluation
    ):
        raise NotImplementedError

    def get_replace_value(self) -> BaseElement:
        raise ValueError

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        # FIXME: check if this makes sense:
        return tuple((self.system, self.pattern.element_order))

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        # FIXME: check if this makes sense:
        return tuple((self.system, self.pattern.pattern_precedence))

    def get_sort_key(self, pattern_sort=True) -> tuple:
        # FIXME: check if this makes sense:
        if pattern_sort:
            return self.pattern_precedence
        else:
            return self.element_order


# FIXME: the class name would be better called RewriteRule.
class Rule(BaseRule):
    """There are two kinds of Rules.  This kind of is a rewrite rule
    and transforms an Expression into another Expression based on the
    pattern and a replacement term and doesn't involve function
    application.

    In contrast to FunctionApplyRule[], rule application cannot force
    a reevaluation of the expression when the rewrite/apply/eval step
    finishes.

    Here is an example of a Rule::

        F[x_] -> x^2   (* The same thing as: Rule[x_, x^2] *)

    ``F[x_]`` is a pattern and ``x^2`` is the replacement term. When
    applied to the expression ``G[F[1.], F[a]]`` the result is
    ``G[1.^2, a^2]``

    Note: we want Rules to be serializable so that we can dump and
    restore Rules in order to make startup time faster.

    """

    def __init__(
        self,
        pattern: BaseElement,
        replace: BaseElement,
        system=False,
        evaluation: Optional[Evaluation] = None,
        attributes: Optional[int] = None,
    ) -> None:
        super(Rule, self).__init__(
            pattern, system=system, evaluation=evaluation, attributes=attributes
        )
        self.replace = replace

    def apply_rule(
        self, expression: BaseElement, vars: dict, options: dict, evaluation: Evaluation
    ):
        new = self.replace.replace_vars(vars)
        new.options = options

        while new.has_form("System`Condition", 2):
            new, cond = new.get_elements()
            if isinstance(cond, Expression):
                cond = cond.evaluate(evaluation)
            if cond is not SymbolTrue:
                raise RuleApplicationFailed()

        # If options is a non-empty dict, we need to ensure
        # reevaluation of the whole expression, since 'new' will
        # usually contain one or more matching OptionValue[symbol_]
        # patterns that need to get replaced with the options'
        # values. This is achieved through Expression.evaluate(),
        # which then triggers OptionValue.apply, which in turn
        # consults evaluation.options to return an option value.

        # In order to get there, we copy 'new' using
        # copy(reevaluate=True), as this will ensure that the whole
        # thing will get reevaluated.

        # If the expression contains OptionValue[] patterns, but
        # options is empty here, we don't need to act, as the
        # expression won't change in that case. the Expression.options
        # would be None anyway, so OptionValue.apply would just return
        # the unchanged expression (which is what we have already).

        if options:
            new = new.copy(reevaluate=True)

        return new

    def get_replace_value(self) -> BaseElement:
        """return the replace value"""
        return self.replace

    def __repr__(self) -> str:
        return "<Rule: %s -> %s>" % (self.pattern, self.replace)

    def get_sort_key(self, pattern_sort=True) -> tuple:
        # FIXME: check if this makes sense:
        if not pattern_sort:
            return tuple((self.system, self.pattern.get_sort_key(False)))

        sort_key = self.pattern.get_sort_key(True)
        if self.replace.has_form("System`Condition", 2):
            sort_key = list(sort_key)
            sort_key[0] = sort_key[0] & PATTERN_SORT_KEY_CONDITIONAL
            sort_key = tuple(sort_key)
        return tuple(
            (
                self.system,
                sort_key,
            )
        )


class FunctionApplyRule(BaseRule):
    """
    A FunctionApplyRule is a rule that has a replacement term that
    is associated a Python function rather than a Mathics Expression
    as happens in a transformation Rule.

    Each time the Pattern part of the Rule matches an Expression, the
    matching subexpression is replaced by the expression returned
    by application of that function to the remaining terms.

    Parameters for the function are bound to parameters matched by the pattern.

    Here is an example taken from the symbol ``System`Plus``.
    It has has associated a FunctionApplyRule::

        Plus[items___] -> mathics.builtin.arithfns.basic.Plus.apply

    The pattern ``items___`` matches a list of Expressions.

    When applied to the expression ``F[a+a]`` the method
    ``mathics.builtin.arithfns.basic.Plus.apply`` is called
    binding the parameter  ``items`` to the value ``Sequence[a,a]``.

    The return value of this function is ``Times[2, a]`` (or more compactly: ``2*a``).
    When replaced in the original expression, the result is: ``F[2*a]``.

    In contrast to (transformation) Rules, FunctionApplyRules can
    change the state of definitions in the the system.

    For example, the rule::

        SetAttributes[a_,b_] -> mathics.builtin.attributes.SetAttributes.apply

    when applied to the expression ``SetAttributes[F,  NumericFunction]``

    sets the attribute ``NumericFunction`` in the  definition of the symbol
    ``F`` and returns Null (``SymbolNull``).

    This will cause `Expression.evaluate() to perform an additional
    ``rewrite_apply_eval()`` step.

    """

    def __init__(
        self,
        name: str,
        pattern: Expression,
        function: Callable,
        check_options: Optional[Callable],
        system: bool = False,
        evaluation: Optional[Evaluation] = None,
        attributes: Optional[int] = None,
    ) -> None:
        super(FunctionApplyRule, self).__init__(
            pattern, system=system, attributes=attributes, evaluation=evaluation
        )
        self.name = name
        self.location = self.function = function
        self.check_options = check_options

    # If you update this, you must also update traced_apply_function
    # (that's in the same file TraceBuiltins is)
    def apply_function(
        self, expression: BaseElement, vars: dict, options: dict, evaluation: Evaluation
    ):
        if options and self.check_options:
            if not self.check_options(options, evaluation):
                return None
        # The Python function implementing this builtin expects
        # argument names corresponding to the symbol names without
        # context marks.
        vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
        if options:
            return (
                self.function(evaluation=evaluation, options=options, **vars_noctx)
                or expression
            )
        else:
            return self.function(evaluation=evaluation, **vars_noctx) or expression

    def __repr__(self) -> str:
        # Cython doesn't allow f-string below and reports:
        #  Cannot convert Unicode string to 'str' implicitly. This is not portable and requires explicit encoding.
        return "<FunctionApplyRule: %s -> %s>" % (self.pattern, self.function)

    def __getstate__(self):
        odict = self.__dict__.copy()
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)  # update attributes
