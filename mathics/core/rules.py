# -*- coding: utf-8 -*-
"""Rules are a core part of the way Mathematica and Mathics3 execute a
program.

Expressions which are transformed by rewrite rules (AKA transformation
rules) are handled by the `Rule` class.

There are also rules for how to match, assign function parameter
arguments, and then apply a Python "evaluation" function to a Mathics3 Expression.
These kinds of rules are handled by objects in the `FunctionApplyRule` class.

Finally, Rules are used as KeyValue pairs in an Association or an Options list.
Here, no pattern matching is applied to the left-hand side.

This module contains the classes for the first two non-KeyValue types of rules.

In a `FunctionApplyRule` rule, the match status of a rule depends on the evaluation return.

For example, suppose that we try to apply rule `F[x_]->x^2` to the expression `F[2]`. The pattern part of the rule,`F[x_]` matches
the expression, `Blank[x]` (or `x_`) is replaced by `2`, giving the substitution expression `2^2`. Evaluation then stops
looking for other rules to be applied to `F[2]`.

On the other hand, suppose that we define a `FunctionApplyRule` that associates `F[x_]` with the function:

.. code-block:: python

    class MyFunction(Builtin):
        ...
        def eval_f(self, x, evaluation) -> Optional[Expression]:
            "F[x_]"   # pattern part of FunctionApplyRule
            if x>3:
                return Expression(SymbolPower, x, Integer2)
            return None

Then, if we apply the rule to `F[2]`, the function is evaluated, returning `None`. Then, in the evaluation loop, we get the same
effect as if the pattern didn't match with the expression. The loop continues then with the next rule associated with `F`.

Why do things this way?

Sometimes, the cost of deciding if the rule match is similar to the cost of evaluating the function. Suppose for example a rule

   F[x_/;(G[x]>0)]:=G[x]

with G[x] a computationally expensive function. To decide if G[x] is larger than 0, we need to evaluate it,
and once we have evaluated it, we just need to return its value.

Also, this allows us to handle several rules in the same function, without relying on our very slow pattern-matching routines.
In particular, this is used for some critical low-level tasks like building lists in iterators, processing arithmetic expressions,
plotting functions, or evaluating derivatives and integrals.

"""

from abc import ABC
from inspect import signature
from itertools import chain
from typing import Any, Callable, Optional

from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.keycomparable import PATTERN_SORT_KEY_CONDITIONAL, KeyComparable
from mathics.core.pattern import BasePattern, StopGenerator
from mathics.core.symbols import Symbol, SymbolSequence, SymbolTrue, strip_context
from mathics.core.systemsymbols import (
    RULE_SYMBOL_HEADS,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolPattern,
)


def simple_pattern(pattern: BaseElement) -> Optional[tuple]:
    """
    For a pattern ``h[a_, b_k, ..., x___]``, with ``h`` a symbol, distinct
    names, blanks that are empty or name a symbol ``k``, and at most a final
    ``x___`` or ``x__``, return ``(h, singles, sequence)``: ``singles`` is a
    tuple of (name, ``k`` or None), ``sequence`` is (name, least count) or
    None. Otherwise return None.

    When each single element has its head ``k`` and the number of elements
    fits, the first match of such a pattern binds the names to the elements
    in order; see `simple_match`.
    """
    if not isinstance(pattern, Expression):
        return None
    head = pattern.head
    if not isinstance(head, Symbol):
        return None
    singles = []
    sequence = None
    names = set()
    for var in pattern.elements:
        if sequence is not None or not var.has_form(SymbolPattern, 2):
            return None
        name, blank = var.elements
        if not isinstance(name, Symbol) or not isinstance(blank, Expression):
            return None
        name = name.get_name()
        if name in names:
            return None
        names.add(name)
        blank_head = blank.head
        if blank_head is SymbolBlank:
            if not blank.elements:
                singles.append((name, None))
            elif len(blank.elements) == 1 and isinstance(blank.elements[0], Symbol):
                singles.append((name, blank.elements[0]))
            else:
                return None
        elif blank.elements:
            return None
        elif blank_head is SymbolBlankNullSequence:
            sequence = (name, 0)
        elif blank_head is SymbolBlankSequence:
            sequence = (name, 1)
        else:
            return None
    return head, tuple(singles), sequence


def simple_match(simple: tuple, expression: BaseElement) -> Optional[dict]:
    """
    The first match of a pattern described by `simple_pattern` on
    `expression`, when it is sure to be the binding of the names to the
    elements in order; None when the pattern matcher has to decide.
    """
    if not isinstance(expression, Expression):
        return None
    head, singles, sequence = simple
    if expression.head is not head:
        return None
    elements = expression.elements
    count = len(singles)
    if sequence is None:
        if len(elements) != count:
            return None
    elif len(elements) < count + sequence[1]:
        return None
    vars = {}
    for (name, blank_head), element in zip(singles, elements):
        if blank_head is not None and element.get_head() is not blank_head:
            return None
        vars[name] = element
    if sequence is not None:
        rest = elements[count:]
        if len(rest) == 1:
            vars[sequence[0]] = rest[0]
        else:
            value = Expression(SymbolSequence, *rest)
            value.pattern_sequence = True
            vars[sequence[0]] = value
    return vars


def _python_function_arguments(f):
    return signature(f).parameters.keys()


def function_arguments(f):
    return _python_function_arguments(f)


def is_option_rule(element: Any) -> bool:
    """
    Return True if element is an Option-like Rule.
    This is a rule of the form:
      key -> value
    or:
      key :> value
    """
    return isinstance(element, Expression) and element.has_form(RULE_SYMBOL_HEADS, 2)


def is_rule(element: Any, include_delayed: bool = True) -> bool:
    """
    Return True if element is a RewriteRule, typically called a "Rule" in WMA.
    In Mathics3, a hard-coded FunctionApplyRule can invoke a Python function.
    This kind of rule is not detected here.

    The parameter "included_delayed" indicates whether we allow Delayed Rules,
    the default is True.
    """
    return (
        isinstance(element, RewriteRule) or is_option_rule(element)
        if include_delayed
        else isinstance(element, RewriteRule)
    )


class StopGenerator_BaseRule(StopGenerator):
    """
    Signals that there are no more rules to check for pattern matching
    """

    pass


class RuleApplicationFailed(Exception):
    """
    Exception raised when a condition fails
    in the RHS, indicating that the match has failed.
    """

    pass


class BaseRule(KeyComparable, ABC):
    """This is the base class from which the FunctionApplyRule and
    RewriteRule classes are derived from.

    Rules are part of the rewriting system of Mathics3. See
    https://en.wikipedia.org/wiki/Rewriting

    This class is not complete in of itself; subclasses must adapt or
    fill in what is needed. In particular either ``apply_rule()`` or
    ``apply_function()`` needs to be implemented.

    Note: we want Rules to be serializable so that we can dump and
    restore Rules in order to make startup time faster.
    """

    # For a rule whose first match is final and whose pattern is plain,
    # such as head[x___] or head[a_, b_], what `simple_match` needs.
    simple: Optional[tuple] = None

    def __init__(
        self,
        pattern: BaseElement,
        system: bool = False,
        attributes: Optional[int] = None,
        evaluation: Optional[Evaluation] = None,
    ) -> None:
        self.location: Optional[Callable] = None
        self.pattern = BasePattern.create(
            pattern, attributes=attributes, evaluation=evaluation
        )

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

        # Most builtin functions are defined by rules such as h[x___] or
        # h[a_, b_]: when their first match is plain, the pattern matcher is
        # not needed (for Orderless h it would go through the subsets of the
        # elements).
        if self.simple is not None and not return_list:
            vars = simple_match(self.simple, expression)
        else:
            vars = None
        if vars is not None:
            try:
                yield_match(vars, None)
            except StopGenerator_BaseRule as exc:
                expr = exc.value
                if (
                    hasattr(expression, "location")
                    and hasattr(expr, "location")
                    and expression.location is not None
                ):
                    expr.location = expression.location
                return expr
            return None

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

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        # FIXME: check if this makes sense:
        # True used to be self.system. Can we remove True?
        return tuple((True, self.pattern.element_order))

    # The below routines might be needed in the future, if BaseRule becomes
    # more BaseElement-like. Right now that's not the situation, probably
    # due to the nature of the generality of Rule which causes
    # special casing lots of places in the Expression code.

    # def get_head_name(self, short=False) -> str:
    #     return "Rule" if short else "System`Rule"

    # def get_symbol_definition_name(self) -> str:
    #     return "System`Rule"

    def get_replace_value(self) -> BaseElement:
        raise ValueError

    @property
    def lhs(self) -> BasePattern | Expression:
        """
        Left-hand side of a rule. Also known, in this context, as its "pattern".
        """
        return self.pattern

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        # FIXME: check if this makes sense:
        # True used to be self.system. Can we remove True?
        return tuple((True, self.pattern.pattern_precedence))

    @property
    def rhs(self):
        """
        Right-hand side of a rule. Also known as its "replacement".
        """
        raise NotImplementedError


class RewriteRule(BaseRule):
    """A RewriteRule in WMA is called simply a "Rule".

    Rules that are user-visible. In Mathics3, we also have rules to
    perform function application, FunctionApplyRule.

    A RewriteRule transforms an Expression into another Expression
    based on the pattern and a replacement term; "pattern" and "
    replacement" are sometimes called the "lhs" and "rhs",
    respectively.

    In contrast to FunctionApplyRule[], rule application cannot force
    a reevaluation of the expression when the rewrite/apply/eval step
    finishes.

    Here is an example of a Rule::

        F[x_] -> x^2   (* The same thing as: Rule[x_, x^2] *)

    ``F[x_]`` is a pattern and ``x^2`` is the replacement term. When
    applied to the expression ``G[F[1.], F[a]]`` the result is
    ``G[1.^2, a^2]``

    Rewrite rules can also be mapping objects when the lhs is a
    constant. These are individual key-value pairs that form in
    Association-like data such as InformationData.

    Note: we want Rules to be serializable so that we can dump and
    restore Rules of classes of builtin function to be loaded via
    lazy loading.
    """

    def __init__(
        self,
        pattern: BaseElement,  # Note: a constant value is also a "pattern".
        replace: BaseElement,
        evaluation: Optional[Evaluation] = None,
        attributes: Optional[int] = None,
    ) -> None:
        super(RewriteRule, self).__init__(
            pattern, attributes=attributes, evaluation=evaluation
        )
        self.replace = replace

    def __repr__(self) -> str:
        return "<Rule: %s -> %s>" % (self.pattern, self.replace)

    def apply_rule(
        self, expression: BaseElement, vars: dict, options: dict, evaluation: Evaluation
    ):
        new = self.replace.replace_vars(vars)
        if new is self.replace and options and isinstance(new, Expression):
            # replace_vars hands back the rule's own right-hand side when no
            # variable occurs in it; the options belong to this application only.
            new = new.shallow_copy()
        new.options = options

        while new.has_form(SymbolCondition, 2):
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

    # # This might be needed in the future.
    # @property
    # def is_literal(self):
    #     """
    #     Mathics3 FunctionApply Rules are literal do not need to be revaluated.
    #     """
    #     print("ReplaceRule WOOT")
    #     return self.pattern.is_literal and self.replace.is_literal

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        sort_key = self.pattern.pattern_precedence
        if self.replace.has_form(SymbolCondition, 2):
            sort_key_list = list(sort_key)
            sort_key_list[0] = sort_key_list[0] & PATTERN_SORT_KEY_CONDITIONAL
            sort_key = tuple(sort_key_list)

        # True used to be self.system. Can we remove True?
        return tuple(
            (
                True,
                sort_key,
            )
        )

    @property
    def rhs(self):
        return self.replace


class FunctionApplyRule(BaseRule):
    """
    A FunctionApplyRule is a rule that has a replacement term that
    is associated a Python function rather than a Mathics3 Expression
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
        evaluation: Optional[Evaluation] = None,
        attributes: Optional[int] = None,
    ) -> None:
        super(FunctionApplyRule, self).__init__(pattern, attributes=attributes)
        # The first match is the only one used (see `apply`), so for a
        # plain pattern such as h[x___] it is known without matching.
        self.simple = simple_pattern(pattern)
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
        prev_expression = evaluation.current_expression
        evaluation.current_expression = expression
        vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
        # Now call the method. If the method returns `None`, then
        # the rule is considered to be applied, and that the return value
        # is the original expression.
        if options:
            result = (
                self.function(evaluation=evaluation, options=options, **vars_noctx)
                or expression
            )
        else:
            result = self.function(evaluation=evaluation, **vars_noctx) or expression
        evaluation.current_expression = prev_expression
        return result

    def __repr__(self) -> str:
        # Cython doesn't allow f-string below and reports:
        #  Cannot convert Unicode string to 'str' implicitly. This is not portable and requires explicit encoding.
        return "<FunctionApplyRule: %s -> %s>" % (self.pattern, self.function)

    def __getstate__(self):
        odict = self.__dict__.copy()
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)  # update attributes

    @property
    def rhs(self):
        return self.function
