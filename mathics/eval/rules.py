from typing import List, Optional as OptionalType, Tuple, Union

from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Rule
from mathics.core.symbols import Atom, Symbol, SymbolList
from mathics.core.systemsymbols import SymbolDispatch, SymbolRule, SymbolRuleDelayed
from mathics.eval.parts import python_levelspec


# TODO: disentangle me
def create_rules(
    rules_expr: Expression,
    expr: Expression,
    name: str,
    evaluation: Evaluation,
    extra_args: OptionalType[List] = None,
) -> Union[Tuple[Union[List[Rule], BaseElement, None], bool], "Dispatch"]:
    """
    This function implements  `Replace`, `ReplaceAll`, `ReplaceRepeated`
    and `ReplaceList` eval methods.
    `name` controls which of these methods is implemented. These methods
    applies the rule / list of rules
    `rules_expr` over the expression `expr`, using the evaluation context
    `evaluation`.

    The result is a tuple of two elements. If the second element is `True`,
    then the first element is the result of the method.
    If `False`, the first element of the tuple is a list of rules.

    """
    if isinstance(rules_expr, Dispatch):
        return rules_expr.rules, False
    if rules_expr.has_form("Dispatch", None):
        if rules_expr.get_head() is SymbolList:
            return Dispatch(rules_expr.elements, evaluation)
        return Dispatch((rules_expr,), evaluation)

    if rules_expr.has_form("List", None):
        rules = rules_expr.elements
    else:
        rules = [rules_expr]
    any_lists = False
    for item in rules:
        if item.get_head() in (SymbolList, SymbolDispatch):
            any_lists = True
            break

    if any_lists:
        all_lists = True
        for item in rules:
            if item.get_head() is not SymbolList:
                all_lists = False
                break

        if all_lists:
            if extra_args is None:
                extra_args = []
            return (
                ListExpression(
                    *[
                        Expression(Symbol(name), expr, item, *extra_args)
                        for item in rules
                    ]
                ),
                True,
            )

        evaluation.message(name, "rmix", rules_expr)
        return None, True

    result = []
    for rule in rules:
        if not isinstance(rule, Expression):
            evaluation.message(name, "reps", rule)
            return None, True
        if rule.head not in (SymbolRule, SymbolRuleDelayed):
            evaluation.message(name, "reps", rule)
            return None, True
        if len(rule.elements) != 2:
            evaluation.message(
                # TODO: shorten names here
                rule.get_head_name(),
                "argrx",
                rule.get_head_name(),
                3,
                2,
            )
            return None, True

        result.append(Rule(rule.elements[0], rule.elements[1]))
    return result, False


def eval_dispatch_atom(
    rules: tuple, evaluation: Evaluation
) -> OptionalType[BaseElement]:
    """Dispatch[rules_List]"""
    # TODO:
    # The next step would be to enlarge this method, in order to
    # check that all the elements in x are rules, eliminate redundancies
    # in the list, and sort the list in a way that increases efficiency.
    # A second step would be to implement an ``Atom`` class containing the
    # compiled patterns, and modify Replace and ReplaceAll to handle this
    # kind of objects.
    #

    all_list = all(rule.has_form("List", None) for rule in rules)
    if all_list:
        elements = [eval_dispatch_atom(rule, evaluation) for rule in rules]
        return ListExpression(*elements)
    flatten_list = []
    for rule in rules:
        if isinstance(rule, Symbol):
            rule = rule.evaluate(evaluation)
        if rule.has_form("List", None):
            flatten_list.extend(rule.elements)
        elif rule.has_form(("Rule", "RuleDelayed"), 2):
            flatten_list.append(rule)
        elif isinstance(rule, Dispatch):
            flatten_list.extend(rule.src.elements)
        else:
            # WMA does not raise this message: just leave it unevaluated,
            # and raise an error when the dispatch rule is used.
            evaluation.message("Dispatch", "invrpl", rule)
            return None

    return Dispatch(tuple(flatten_list), evaluation)


def eval_replace_with_levelspec(expr, rules, ls, heads, evaluation, options):
    """eval Replace with a levelspec parameter"""
    rules, ret = create_rules(rules, expr, "Replace", evaluation)
    if ret:
        return rules

    result, _ = expr.do_apply_rules(
        rules,
        evaluation,
        level=0,
        options={"levelspec": python_levelspec(ls), "heads": heads},
    )
    return result


class Dispatch(Atom):
    class_head_name = "System`Dispatch"

    src: ListExpression
    rules: List[Rule]

    def __init__(
        self, rule_tuple: Tuple[Expression, ...], evaluation: Evaluation
    ) -> None:
        assert isinstance(rule_tuple, tuple)
        self.src = ListExpression(*rule_tuple)
        try:
            self.rules = [
                Rule(rule.elements[0], rule.elements[1]) for rule in rule_tuple
            ]
        except:
            raise
        self._elements = None
        self._head = SymbolDispatch

    @property
    def element_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.src.element_precedence

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return self.src.pattern_precedence

    def get_sort_key(self, pattern_sort: bool = False) -> tuple:
        return self.src.element_precedence

    def get_atom_name(self):
        return "System`Dispatch"

    def __repr__(self):
        return "dispatch"

    def atom_to_boxes(self, f: Symbol, evaluation: Evaluation):
        from mathics.builtin.box.layout import RowBox
        from mathics.eval.makeboxes import format_element

        # box_element = format_element(self.src, evaluation, f)
        box_element = String(f"<{len(self.rules)}>")
        return RowBox(String("Dispatch"), String("["), box_element, String("]"))
