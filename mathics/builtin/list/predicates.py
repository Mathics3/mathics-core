"""
Predicates on Lists
"""

from mathics.builtin.base import Builtin
from mathics.builtin.options import options_to_rules
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolContainsOnly


class ContainsOnly(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ContainsOnly.html</url>

    <dl>
      <dt>'ContainsOnly[$list1$, $list2$]'
      <dd>yields True if $list1$ contains only elements that appear in $list2$.
    </dl>

    >> ContainsOnly[{b, a, a}, {a, b, c}]
     = True

    The first list contains elements not present in the second list:
    >> ContainsOnly[{b, a, d}, {a, b, c}]
     = False

    >> ContainsOnly[{}, {a, b, c}]
     = True

    #> ContainsOnly[1, {1, 2, 3}]
     : List or association expected instead of 1.
     = ContainsOnly[1, {1, 2, 3}]

    #> ContainsOnly[{1, 2, 3}, 4]
     : List or association expected instead of 4.
     = ContainsOnly[{1, 2, 3}, 4]

    Use Equal as the comparison function to have numerical tolerance:
    >> ContainsOnly[{a, 1.0}, {1, a, b}, {SameTest -> Equal}]
     = True

    #> ContainsOnly[{c, a}, {a, b, c}, IgnoreCase -> True]
     : Unknown option IgnoreCase -> True in ContainsOnly.
     : Unknown option IgnoreCase in .
     = True
    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    messages = {
        "lsa": "List or association expected instead of `1`.",
        "nodef": "Unknown option `1` for ContainsOnly.",
        "optx": "Unknown option `1` in `2`.",
    }

    options = {
        "SameTest": "SameQ",
    }

    summary_text = "test if all the elements of a list appears into another list"

    def check_options(self, expr, evaluation, options):
        for key in options:
            if key != "System`SameTest":
                if expr is None:
                    evaluation.message("ContainsOnly", "optx", Symbol(key))
                else:
                    evaluation.message("ContainsOnly", "optx", Symbol(key), expr)

        return None

    def eval(self, list1, list2, evaluation, options={}):
        "ContainsOnly[list1_List, list2_List, OptionsPattern[ContainsOnly]]"

        same_test = self.get_option(options, "SameTest", evaluation)

        def sameQ(a, b) -> bool:
            """Mathics SameQ"""
            result = Expression(same_test, a, b).evaluate(evaluation)
            return result is SymbolTrue

        self.check_options(None, evaluation, options)
        for a in list1.elements:
            if not any(sameQ(a, b) for b in list2.elements):
                return SymbolFalse
        return SymbolTrue

    def eval_msg(self, e1, e2, evaluation, options={}):
        "ContainsOnly[e1_, e2_, OptionsPattern[ContainsOnly]]"

        opts = (
            options_to_rules(options)
            if len(options) <= 1
            else [ListExpression(*options_to_rules(options))]
        )
        expr = Expression(SymbolContainsOnly, e1, e2, *opts)

        if not isinstance(e1, Symbol) and not e1.has_form("List", None):
            evaluation.message("ContainsOnly", "lsa", e1)
            return self.check_options(expr, evaluation, options)

        if not isinstance(e2, Symbol) and not e2.has_form("List", None):
            evaluation.message("ContainsOnly", "lsa", e2)
            return self.check_options(expr, evaluation, options)

        return self.check_options(expr, evaluation, options)


# TODO: ContainsAll, ContainsNone ContainsAny ContainsExactly
