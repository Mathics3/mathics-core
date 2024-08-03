"""
This module contains the basic functions used in Expression for the rewrite_apply_eval_step method.
"""

import time
from typing import Optional, Tuple, Type

from mathics.core.attributes import (
    A_FLAT,
    A_HOLD_ALL,
    A_HOLD_ALL_COMPLETE,
    A_HOLD_FIRST,
    A_HOLD_REST,
    A_LISTABLE,
    A_ORDERLESS,
    A_SEQUENCE_HOLD,
)
from mathics.core.element import BaseElement, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.interrupt import ReturnInterrupt
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import SymbolAborted, SymbolOverflow, SymbolUnevaluated

###  These are the functions used in rewrite_apply_eval_step. By now, I leave this
###  in the order of occurrence inside that function.


def apply_associated_rules(new, elements, attributes, evaluation):
    """
    Look for the associated upvalues, downvalues and subvalues rules to `new`,
    and apply them to the expression until one of them matches. Then apply it.
    Depending on the result of the application, returns the resulting value and
    a flag that indicates if the evaluation loop should continue.
    """

    # Step 5: Must we need to thread-rewrite the expression?
    #
    # Threading is needed when head has the ``Listable``
    # Attribute (or flag ``A_LISTABLE``).
    # ``Expression.thread`` rewrites the expression:
    #  ``F[{a,b,c,...}]`` as:
    #  ``{F[a], F[b], F[c], ...}``.

    # Note: Threading here is different from Python or OS threads,
    # even though the intent of this attribute was to allow for
    # hardware threading to make use of more cores.
    #
    # Right now, we do not make use of Python thread or hardware
    # threading.  Still, we need to perform this rewrite to
    # maintain correct semantic behavior.

    if A_LISTABLE & attributes:
        done, threaded = new.thread(evaluation)
        if done:
            if threaded.sameQ(new):
                new._timestamp_cache(evaluation)
                return new, False
            else:
                return threaded, True

    # Step 6:
    # Look at the rules associated with:
    #   1. the upvalues of each element
    #   2. the downvalues / subvalues associated with the lookup_name
    #      when the lookup values matches or is not the head.
    #
    # For example, consider expression: F[a, 1, b, a]
    #
    # First look for upvalue rules associated with "a".
    #   If a rule is found, try to apply the corresponding rule.
    #      If that succeeds, (the result is not None) then
    #      return the result. It will be reevaluated when "reevaluate" is True and
    #      the result changes from the input, and is an EvalMixin type.
    #
    # If the rule fails, continue with the next element.
    #
    # The next element, "1", is a number; it does not have upvalues. So skip
    # that and looking at upvalues of "b".
    # If rule matching does not succeed for "b", then look at the next element,
    # "a". However element "a" has been already seen. So, skip it.
    # Finally, because "F" is a symbol,
    # new.head_name() == new.get_lookup_name(); look at downvalue rules.

    # If instead of "F[a, 1, a, c]" we had  "Q[s][a, 1, a, c]",
    # the routine would look for the subvalues of "Q".
    #
    # For "Plus" and "Times", WMA behaves slightly different for numbers.
    # For example consider:
    # ```
    # Unprotect[Plus];
    # Plus[2,3]:=fish;
    # Plus[2,3]
    # ```
    # In Mathics3, the result in  "fish", but WL gives "5".
    # This shows that WMA evaluates certain symbols differently.

    def rules():
        rules_names = set()
        if not A_HOLD_ALL_COMPLETE & attributes:
            for element in elements:
                if not isinstance(element, EvalMixin):
                    continue
                name = element.get_lookup_name()
                if len(name) > 0:  # only lookup rules if this is a symbol
                    if name not in rules_names:
                        rules_names.add(name)
                        for rule in evaluation.definitions.get_upvalues(name):
                            yield rule
        lookup_name = new.get_lookup_name()
        if lookup_name == new.get_head_name():
            for rule in evaluation.definitions.get_downvalues(lookup_name):
                yield rule
        else:
            # Subvalues applies for expressions of the form `D[1][f][x]`
            # For this expression, the `head` would be `D[1][f]`
            # while its `lookup_name` would be `D`.
            for rule in evaluation.definitions.get_subvalues(lookup_name):
                yield rule

    for rule in rules():
        try:
            result = rule.apply(new, evaluation, fully=False)
        except OverflowError:
            evaluation.message("General", "ovfl")
            return Expression(SymbolOverflow), False
        if result is not None:
            if not isinstance(result, EvalMixin):
                return result, False
            if result.sameQ(new):
                new._timestamp_cache(evaluation)
                return new, False
            else:
                return result, True
    return None, False


def eval_elements(expr, head, attributes, evaluation):
    """
    This function evaluates the elements of the expression,
    taking into account the attributes.

    TODO: check if we can DRY Expression.evaluate_elements
    using this.
    """
    # @timeit
    def inner_eval_elements():
        nonlocal recompute_properties

        # @timeit
        def eval_range(indices):
            nonlocal recompute_properties
            recompute_properties = False
            for index in indices:
                element = elements[index]
                if not element.has_form("Unevaluated", 1):
                    if isinstance(element, EvalMixin):
                        new_value = element.evaluate(evaluation)
                        # We need id() because != by itself is too permissive
                        if id(element) != id(new_value):
                            recompute_properties = True
                            elements[index] = new_value

        # @timeit
        def rest_range(indices):
            nonlocal recompute_properties
            if not A_HOLD_ALL_COMPLETE & attributes:
                if expr._does_not_contain_symbol("System`Evaluate"):
                    return
                for index in indices:
                    element = elements[index]
                    if element.has_form("Evaluate", 1):
                        if isinstance(element, EvalMixin):
                            new_value = element.evaluate(evaluation)
                            # We need id() because != by itself is too permissive
                            if id(new_value) != id(element):
                                elements[index] = new_value
                                recompute_properties = True

        if (A_HOLD_ALL | A_HOLD_ALL_COMPLETE) & attributes:
            # eval_range(range(0, 0))
            rest_range(range(len(elements)))
        elif A_HOLD_FIRST & attributes:
            rest_range(range(0, min(1, len(elements))))
            eval_range(range(1, len(elements)))
        elif A_HOLD_REST & attributes:
            eval_range(range(0, min(1, len(elements))))
            rest_range(range(1, len(elements)))
        else:
            eval_range(range(len(elements)))
            # rest_range(range(0, 0))

    recompute_properties = False
    if expr.elements_properties.elements_fully_evaluated:
        elements = expr._elements
    else:
        elements = expr.get_mutable_elements()
        # FIXME: see if we can preserve elements properties in inner_eval_elements()
        inner_eval_elements()

    if recompute_properties:
        new = Expression(head, *elements, elements_properties=None)
        new._build_elements_properties()
    else:
        new = Expression(head, *elements, elements_properties=expr.elements_properties)
    return new, elements


def pre_process_unevaluated_elements(new, head, elements, attributes):
    """
    Process the "Unevaluate" wrapper.
    TODO: FIXME
    """

    # comment @mmatera: I think this is wrong now, because alters
    # singletons... (see PR #58) The idea is to mark which elements was
    # marked as "Unevaluated" Also, this consumes time for long lists, and
    # is useful just for a very unfrequent expressions, involving
    # `Unevaluated` elements.  Notice also that this behaviour is broken
    # when the argument of "Unevaluated" is a symbol (see comment and tests
    # in test/test_unevaluate.py)

    for element in elements:
        element.unevaluated = False

    # If HoldAllComplete Attribute (flag ``A_HOLD_ALL_COMPLETE``) is not set,
    # and the expression has elements of the form  `Unevaluated[element]`
    # change them to `element` and set a flag `unevaluated=True`
    # If the evaluation fails, use this flag to restore back the initial form
    # Unevaluated[element]

    # comment @mmatera:
    # what we need here is some way to track which elements are marked as
    # Unevaluated, that propagates by flatten, and at the end,
    # to recover a list of positions that (eventually)
    # must be marked again as Unevaluated.

    if not A_HOLD_ALL_COMPLETE & attributes:
        dirty_elements = None

        for index, element in enumerate(elements):
            if element.has_form("Unevaluated", 1):
                if dirty_elements is None:
                    dirty_elements = list(elements)
                dirty_elements[index] = element._elements[0]
                dirty_elements[index].unevaluated = True

        if dirty_elements:
            new = Expression(head, *dirty_elements)
            elements = dirty_elements
            new._build_elements_properties()

    return new


def post_process_dirty_elements(new, head, evaluation):
    """
    Restores the "Unevaluated" wrapper.
    TODO: FIXME
    """

    dirty_elements = None

    # Expression did not change, re-apply Unevaluated
    for index, element in enumerate(new._elements):
        if element.unevaluated:
            if dirty_elements is None:
                dirty_elements = list(new._elements)
            dirty_elements[index] = Expression(SymbolUnevaluated, element)

    if dirty_elements:
        new = Expression(head)
        new.elements = dirty_elements

    new._timestamp_cache(evaluation)
    return new


def rewrite_apply_eval_step(self, evaluation) -> Tuple["Expression", bool]:
    """Perform a single rewrite/apply/eval step of the bigger
    Expression.evaluate() process.

    We return the Expression as well as a Boolean which indicates
    whether the caller `evaluate()` should consider reevaluating
    the expression.

    Note that this is a recursive process: we may call something
    that may call our parent: evaluate() which calls us again.

    Also note that this step is time consuming, complicated, and involved.

    Therefore, subclasses of the BaseEvaluation class may decide
    to specialize this code so that it is simpler and faster. In
    particular, a specialization for a particular kind of object
    like a particular kind of Atom, may decide it does not need to
    do the rule rewriting step. Or that it knows that after
    performing this step no further transformation is needed.

    See also https://mathics-development-guide.readthedocs.io/en/latest/extending/code-overview/evaluation.html#detailed-rewrite-apply-eval-process
    """

    if hasattr(self, "rewrite_apply_eval_step"):
        return self.rewrite_apply_eval_step(evaluation)

    if not isinstance(self, Expression):
        # Remove True when ready...
        if True or isinstance(self, EvalMixin):
            return evaluate(self, evaluation), False
        return self, False

    if isinstance(self, ListExpression):
        if self.elements_properties is None:
            self._build_elements_properties()
        if not self.elements_properties.elements_fully_evaluated:
            new = self.shallow_copy()
            new = new.evaluate_elements(evaluation)
            return new, False
        return self, False

    # Step 1 : evaluate the Head and get its Attributes. These attributes,
    # used later, include: HoldFirst / HoldAll / HoldRest / HoldAllComplete.

    # Note: self._head can be not just a symbol, but some arbitrary expression.
    # This is what makes expressions in Mathics be M-expressions rather than
    # S-expressions.

    head = self._head.evaluate(evaluation)

    attributes = head.get_attributes(evaluation.definitions)

    if self.elements_properties is None:
        self._build_elements_properties()

    # Step 2: Build a new expression. If it can be avoided, we take care not
    # to:
    # * evaluate elements,
    # * run to_python() on them in Expression construction, or
    # * convert Expression elements from a tuple to a list and back

    new, elements = eval_elements(self, head, attributes, evaluation)

    # Step 3: Now, process the attributes of head
    # If there are sequence, flatten them if the attributes allow it.
    if (
        not new.elements_properties.is_flat
        and not (A_SEQUENCE_HOLD | A_HOLD_ALL_COMPLETE) & attributes
    ):
        # This step is applied to most of the expressions
        # and could be heavy for expressions with many elements (like long lists)
        # however, most of the times, expressions does not have `Sequence` expressions
        # inside. Now this is handled by caching the sequences.
        new = new.flatten_sequence(evaluation)
        if new.elements_properties is None:
            new._build_elements_properties()
        elements = new._elements

    new = pre_process_unevaluated_elements(new, head, elements, attributes)

    # If the Attribute ``Flat`` (flag ``A_FLAT``) is set, calls
    # flatten with a callback that set elements as unevaluated
    # too.
    def flatten_callback(new_elements, old):
        for element in new_elements:
            element.unevaluated = old.unevaluated

    if A_FLAT & attributes:
        new = new.flatten_with_respect_to_head(new._head, callback=flatten_callback)
        if new.elements_properties is None:
            new._build_elements_properties()

    # If the attribute ``Orderless`` is set, sort the elements, according to the
    # element's ``get_sort_key()`` method.
    # Sorting can be time consuming which is why we note this in ``elements_properties``.
    # Checking for sortedness takes O(n) while sorting take O(n log n).
    if not new.elements_properties.is_ordered and (A_ORDERLESS & attributes):
        new.sort()

    # Step 4:  Rebuild the ExpressionCache, which tracks which symbols
    # where involved, the Sequence`s present, and the last time they have changed.

    new._timestamp_cache(evaluation)

    # Steps 5 and 6:
    # First look if the function is "Listable" and act in consequence. Then,
    # look at the rules associated with:
    #   1. the upvalues of each element
    #   2. the downvalues / subvalues associated with the lookup_name
    #      when the lookup values matches or is not the head.
    result, iterate = apply_associated_rules(new, elements, attributes, evaluation)
    if result is not None:
        return result, iterate

    # Step 7: If we are here, is because we didn't find any rule that
    # matches the expression.
    new = post_process_dirty_elements(new, head, evaluation)

    return new, False


#  Now, let's see how much take each step for certain typical expressions:
#  (assuming that "F" and "a1", ... "a100" are undefined symbols, and
#  n0->0, n1->1,..., n99->99)
#
#  Expr1: to_expression("F", 1)                       (trivial evaluation to a short expression)
#  Expr2: to_expression("F", 0, 1, 2, .... 99)        (trivial evaluation to a long expression, with just numbers)
#  Expr3: to_expression("F", a0, a2, ...., a99)       (trivial evaluation to a long expression, with just undefined symbols)
#  Expr4: to_expresion("F", n0, n2, ...., n99)       (trivial evaluation to a long expression, with just undefined symbols)
#  Expr5: to_expression("Plus", 99,..., 0)            (nontrivial evaluation to a long expression, with just undefined symbols)
#  Expr6: to_expression("Plus", a99,..., a0)          (nontrivial evaluation to a long expression, with just undefined symbols)
#  Expr7: to_expression("Plus", n99,..., n0)          (nontrivial evaluation to a long expression, with just undefined symbols)
#  Expr8: to_expression("Plus", n1,..., n1)           (nontrivial evaluation to a long expression, with just undefined symbols)
#


def evaluate(element: BaseElement, evaluation: Evaluation) -> Optional[BaseElement]:
    """Implementation of `evaluate`"""
    if isinstance(element, Expression):
        return evaluate_expression(element, evaluation)
    if isinstance(element, Symbol):
        return evaluate_symbol(element, evaluation)

    raise ValueError("Element of {type(element)} not supported")


def evaluate_expression(
    self,
    evaluation: Evaluation,
) -> Optional[Type["BaseElement"]]:
    """
    Apply transformation rules and expression evaluation to ``evaluation`` via
    ``rewrite_apply_eval_step()`` until that method tells us to stop,
    or until we hit an $IterationLimit or TimeConstrained limit.

    Evaluation is recursive:``rewrite_apply_eval_step()`` may call us.
    """
    assert isinstance(self, Expression)
    if evaluation.timeout:
        return

    expr = self
    reevaluate = True
    limit = None
    iteration = 1
    names = set()
    definitions = evaluation.definitions

    old_options = evaluation.options
    evaluation.inc_recursion_depth()
    if evaluation.definitions.trace_evaluation:
        if evaluation.definitions.timing_trace_evaluation:
            evaluation.print_out(time.time() - evaluation.start_time)
        evaluation.print_out(
            "  " * evaluation.recursion_depth + "Evaluating: %s" % expr
        )
    try:
        # Evaluation loop:
        while reevaluate:
            # If definitions have not changed in the last evaluation,
            # then evaluating again will produce the same result
            if not expr.is_uncertain_final_definitions(definitions):
                break
            # Here the names of the lookupname of the expression
            # are stored. This is necesary for the implementation
            # of the builtin `Return[]`
            names.add(expr.get_lookup_name())

            # This loads the default options associated
            # to the expression
            if hasattr(expr, "options") and expr.options:
                evaluation.options = expr.options

            # ``rewrite_apply_eval_step()`` makes a pass at
            # evaluating the expression. If we know that a further
            # evaluation will not be needed, ``reevaluate`` is set
            # False.  Note that ``rewrite_apply_eval_step()`` can
            # perform further ``evaluate`` and we will recurse
            # back into this routine.
            expr, reevaluate = rewrite_apply_eval_step(expr, evaluation)

            if not reevaluate:
                break

            # TraceEvaluation[] logging.
            if evaluation.definitions.trace_evaluation:
                evaluation.print_out("  " * evaluation.recursion_depth + "-> %s" % expr)
            iteration += 1
            # Check whether we have hit $Iterationlimit: is the number of times
            # ``reevaluate`` came back False in this loop.
            if limit is None:
                limit = definitions.get_config_value("$IterationLimit")
                if limit is None:
                    limit = "inf"
            if limit != "inf" and iteration > limit:
                evaluation.error("$IterationLimit", "itlim", limit)
                return SymbolAborted

    # "Return gets discarded only if it was called from within the r.h.s.
    # of a user-defined rule."
    # http://mathematica.stackexchange.com/questions/29353/how-does-return-work
    # Otherwise it propogates up.
    #
    except ReturnInterrupt as ret:
        if names.intersection(definitions.user.keys()):
            return ret.expr
        else:
            raise ret
    finally:
        # Restores the state
        evaluation.options = old_options
        evaluation.dec_recursion_depth()

    return expr


def evaluate_symbol(self, evaluation):
    """
    Evaluates the symbol by applying the rules (ownvalues) in its definition,
    recursively.
    """
    assert isinstance(self, Symbol)
    if evaluation.definitions.trace_evaluation:
        if evaluation.definitions.timing_trace_evaluation:
            evaluation.print_out(time.time() - evaluation.start_time)
        evaluation.print_out(
            "  " * evaluation.recursion_depth + "  Evaluating: %s" % self
        )

    rules = evaluation.definitions.get_ownvalues(self.name)
    for rule in rules:
        result = rule.apply(self, evaluation, fully=True)
        if result is not None and not result.sameQ(self):
            if evaluation.definitions.trace_evaluation:
                evaluation.print_out(
                    "  " * evaluation.recursion_depth + "  -> %s" % result
                )
            return result.evaluate(evaluation)
    return self
