"""
Math & Counting Operations on Lists
"""
import heapq

from mathics.builtin.base import Builtin, CountableInteger, NegativeIntegerException
from mathics.core.exceptions import MessageException
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import SymbolAlternatives, SymbolMatchQ


class _RankedTake(Builtin):
    messages = {
        "intpm": "Expected non-negative integer at position `1` in `2`.",
        "rank": "The specified rank `1` is not between 1 and `2`.",
    }

    options = {
        "ExcludedForms": "Automatic",
    }

    def _compute(self, t, n, evaluation, options, f=None):
        try:
            limit = CountableInteger.from_expression(n)
        except MessageException as e:
            e.message(evaluation)
            return
        except NegativeIntegerException:
            if f:
                args = (3, Expression(self.get_name(), t, f, n))
            else:
                args = (2, Expression(self.get_name(), t, n))
            evaluation.message(self.get_name(), "intpm", *args)
            return

        if limit is None:
            return

        if limit == 0:
            return ListExpression()
        else:
            excluded = self.get_option(options, "ExcludedForms", evaluation)
            if excluded:
                if (
                    isinstance(excluded, Symbol)
                    and excluded.get_name() == "System`Automatic"
                ):

                    def exclude(item):
                        if isinstance(item, Symbol) and item.get_name() in (
                            "System`None",
                            "System`Null",
                            "System`Indeterminate",
                        ):
                            return True
                        elif item.get_head_name() == "System`Missing":
                            return True
                        else:
                            return False

                else:
                    excluded = Expression(SymbolAlternatives, *excluded.elements)

                    def exclude(item):
                        return (
                            Expression(SymbolMatchQ, item, excluded).evaluate(
                                evaluation
                            )
                            is SymbolTrue
                        )

                filtered = [element for element in t.elements if not exclude(element)]
            else:
                filtered = t.elements

            if limit > len(filtered):
                if not limit.is_upper_limit():
                    evaluation.message(
                        self.get_name(), "rank", limit.get_int_value(), len(filtered)
                    )
                    return
                else:
                    py_n = len(filtered)
            else:
                py_n = limit.get_int_value()

            if py_n < 1:
                return ListExpression()

            if f:
                heap = [
                    (Expression(f, element).evaluate(evaluation), element, i)
                    for i, element in enumerate(filtered)
                ]
                element_pos = 1  # in tuple above
            else:
                heap = [(element, i) for i, element in enumerate(filtered)]
                element_pos = 0  # in tuple above

            if py_n == 1:
                result = [self._get_1(heap)]
            else:
                result = self._get_n(py_n, heap)

            return t.restructure("List", [x[element_pos] for x in result], evaluation)


class _RankedTakeSmallest(_RankedTake):
    def _get_1(self, a):
        return min(a)

    def _get_n(self, n, heap):
        return heapq.nsmallest(n, heap)


class _RankedTakeLargest(_RankedTake):
    def _get_1(self, a):
        return max(a)

    def _get_n(self, n, heap):
        return heapq.nlargest(n, heap)


class TakeLargestBy(_RankedTakeLargest):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TakeLargestBy.html</url>

    <dl>
      <dt>'TakeLargestBy[$list$, $f$, $n$]'
      <dd>returns the a sorted list of the $n$ largest items in $list$
        using $f$ to retrieve the items' keys to compare them.
    </dl>

    For details on how to use the ExcludedForms option, see TakeLargest[].

    >> TakeLargestBy[{{1, -1}, {10, 100}, {23, 7, 8}, {5, 1}}, Total, 2]
     = {{10, 100}, {23, 7, 8}}

    >> TakeLargestBy[{"abc", "ab", "x"}, StringLength, 1]
     = {abc}
    """

    summary_text = "sublist of n largest elements according to a given criteria"

    def eval(self, element, f, n, evaluation, options):
        "TakeLargestBy[element_List, f_, n_, OptionsPattern[TakeLargestBy]]"
        return self._compute(element, n, evaluation, options, f=f)


class TakeSmallestBy(_RankedTakeSmallest):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/TakeSmallestBy.html</url>

    <dl>
      <dt>'TakeSmallestBy[$list$, $f$, $n$]'
      <dd>returns the a sorted list of the $n$ smallest items in $list$
        using $f$ to retrieve the items' keys to compare them.
    </dl>

    For details on how to use the ExcludedForms option, see TakeLargest[].

    >> TakeSmallestBy[{{1, -1}, {10, 100}, {23, 7, 8}, {5, 1}}, Total, 2]
     = {{1, -1}, {5, 1}}

    >> TakeSmallestBy[{"abc", "ab", "x"}, StringLength, 1]
     = {x}
    """

    summary_text = "sublist of n largest elements according to a criteria"

    def eval(self, element, f, n, evaluation, options):
        "TakeSmallestBy[element_List, f_, n_, OptionsPattern[TakeSmallestBy]]"
        return self._compute(element, n, evaluation, options, f=f)
