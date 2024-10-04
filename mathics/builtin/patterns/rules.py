# -*- coding: utf-8 -*-
"""
Define, apply and compiling rules.
"""

from typing import List, Optional as OptionalType, Tuple, Union

from mathics.core.atoms import Integer, Integer2, Number, String
from mathics.core.attributes import A_HOLD_REST, A_PROTECTED, A_SEQUENCE_HOLD
from mathics.core.builtin import AtomBuiltin, BinaryOperator, Builtin, PatternError
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import InvalidLevelspecError
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Rule
from mathics.core.symbols import Atom, Symbol, SymbolList, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolDispatch,
    SymbolInfinity,
    SymbolRule,
    SymbolRuleDelayed,
)
from mathics.eval.parts import python_levelspec

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.rules"


class Rule_(BinaryOperator):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Rule_.html</url>

    <dl>
      <dt>'Rule[$x$, $y$]'
      <dt>'$x$ -> $y$'
      <dd>represents a rule replacing $x$ with $y$.
    </dl>

    >> a+b+c /. c->d
    = a + b + d
    >> {x,x^2,y} /. x->3
     = {3, 9, y}
    >> a /. Rule[1, 2, 3] -> t
     : Rule called with 3 arguments; 2 arguments are expected.
     = a
    """

    name = "Rule"
    operator = "->"
    attributes = A_SEQUENCE_HOLD | A_PROTECTED
    grouping = "Right"
    needs_verbatim = True
    summary_text = "a replacement rule"

    def eval_rule(self, elems, evaluation):
        """Rule[elems___]"""
        num_parms = len(elems.get_sequence())
        if num_parms != 2:
            evaluation.message("Rule", "argrx", "Rule", Integer(num_parms), Integer2)
        return None


class RuleDelayed(BinaryOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RuleDelayed.html</url>

    <dl>
      <dt>'RuleDelayed[$x$, $y$]'
      <dt>'$x$ :> $y$'
      <dd>represents a rule replacing $x$ with $y$, with $y$ held
        unevaluated.
    </dl>

    >> Attributes[RuleDelayed]
     = {HoldRest, Protected, SequenceHold}
    """

    attributes = A_SEQUENCE_HOLD | A_HOLD_REST | A_PROTECTED
    needs_verbatim = True
    operator = ":>"
    summary_text = "a rule that keeps the replacement unevaluated"

    def eval_rule_delayed(self, elems, evaluation):
        """RuleDelayed[elems___]"""
        num_parms = len(elems.get_sequence())
        if num_parms != 2:
            evaluation.message(
                "RuleDelayed", "argrx", "RuleDelayed", Integer(num_parms), Integer2
            )
        return None


# TODO: disentangle me
def create_rules(
    rules_expr: BaseElement,
    expr: Expression,
    name: str,
    evaluation: Evaluation,
    extra_args: OptionalType[List] = None,
) -> Tuple[Union[List[Rule], BaseElement], bool]:
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
        return Dispatch(rules_expr.elements, evaluation)

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


class Replace(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Replace.html</url>

    <dl>
      <dt>'Replace[$expr$, $x$ -> $y$]'
      <dd>yields the result of replacing $expr$ with $y$ if it
        matches the pattern $x$.
      <dt>'Replace[$expr$, $x$ -> $y$, $levelspec$]'
      <dd>replaces only subexpressions at levels specified through
        $levelspec$.
      <dt>'Replace[$expr$, {$x$ -> $y$, ...}]'
      <dd>performs replacement with multiple rules, yielding a
        single result expression.
      <dt>'Replace[$expr$, {{$a$ -> $b$, ...}, {$c$ -> $d$, ...}, ...}]'
      <dd>returns a list containing the result of performing each
        set of replacements.
    </dl>

    >> Replace[x, {x -> 2}]
     = 2

    By default, only the top level is searched for matches
    >> Replace[1 + x, {x -> 2}]
     = 1 + x

    >> Replace[x, {{x -> 1}, {x -> 2}}]
     = {1, 2}

    Replace stops after the first replacement
    >> Replace[x, {x -> {}, _List -> y}]
     = {}

    Replace replaces the deepest levels first
    >> Replace[x[1], {x[1] -> y, 1 -> 2}, All]
     = x[2]

    By default, heads are not replaced
    >> Replace[x[x[y]], x -> z, All]
     = x[x[y]]

    Heads can be replaced using the Heads option
    >> Replace[x[x[y]], x -> z, All, Heads -> True]
     = z[z[y]]

    Note that heads are handled at the level of elements
    >> Replace[x[x[y]], x -> z, {1}, Heads -> True]
     = z[x[y]]

    You can use Replace as an operator
    >> Replace[{x_ -> x + 1}][10]
     = 11
    """

    messages = {
        "reps": "`1` is not a valid replacement rule.",
        "rmix": "Elements of `1` are a mixture of lists and nonlists.",
    }

    options = {"Heads": "False"}
    rules = {"Replace[rules_][expr_]": "Replace[expr, rules]"}
    summary_text = "apply a replacement rule"

    def eval_levelspec(self, expr, rules, ls, evaluation, options):
        "Replace[expr_, rules_, Optional[Pattern[ls, _?LevelQ], {0}], OptionsPattern[Replace]]"
        try:
            rules, ret = create_rules(rules, expr, "Replace", evaluation)
            if ret:
                return rules

            heads = self.get_option(options, "Heads", evaluation) is SymbolTrue

            result, _ = expr.do_apply_rules(
                rules,
                evaluation,
                level=0,
                options={"levelspec": python_levelspec(ls), "heads": heads},
            )
            return result
        except InvalidLevelspecError:
            evaluation.message("General", "level", ls)

        except PatternError:
            evaluation.message("Replace", "reps", rules)

        return None


class ReplaceAll(BinaryOperator):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ReplaceAll.html</url>

    <dl>
      <dt>'ReplaceAll[$expr$, $x$ -> $y$]'
      <dt>'$expr$ /. $x$ -> $y$'
      <dd>yields the result of replacing all subexpressions of
        $expr$ matching the pattern $x$ with $y$.
      <dt>'$expr$ /. {$x$ -> $y$, ...}'
      <dd>performs replacement with multiple rules, yielding a
        single result expression.
      <dt>'$expr$ /. {{$a$ -> $b$, ...}, {$c$ -> $d$, ...}, ...}'
      <dd>returns a list containing the result of performing each
        set of replacements.
    </dl>

    >> a+b+c /. c->d
     = a + b + d
    >> g[a+b+c,a]/.g[x_+y_,x_]->{x,y}
     = {a, b + c}

    If $rules$ is a list of lists, a list of all possible respective
    replacements is returned:
    >> {a, b} /. {{a->x, b->y}, {a->u, b->v}}
     = {{x, y}, {u, v}}
    The list can be arbitrarily nested:
    >> {a, b} /. {{{a->x, b->y}, {a->w, b->z}}, {a->u, b->v}}
     = {{{x, y}, {w, z}}, {u, v}}
    >> {a, b} /. {{{a->x, b->y}, a->w, b->z}, {a->u, b->v}}
     : Elements of {{a -> x, b -> y}, a -> w, b -> z} are a mixture of lists and nonlists.
     = {{a, b} /. {{a -> x, b -> y}, a -> w, b -> z}, {u, v}}

    ReplaceAll also can be used as an operator:
    >> ReplaceAll[{a -> 1}][{a, b}]
     = {1, b}

    ReplaceAll replaces the shallowest levels first:
    >> ReplaceAll[x[1], {x[1] -> y, 1 -> 2}]
     = y
    """

    grouping = "Left"
    needs_verbatim = True
    operator = "/."

    messages = {
        "reps": "`1` is not a valid replacement rule.",
        "rmix": "Elements of `1` are a mixture of lists and nonlists.",
    }

    rules = {"ReplaceAll[rules_][expr_]": "ReplaceAll[expr, rules]"}
    summary_text = "apply a replacement rule on each subexpression"

    def eval(self, expr, rules, evaluation: Evaluation):
        "ReplaceAll[expr_, rules_]"
        try:
            rules, ret = create_rules(rules, expr, "ReplaceAll", evaluation)
            if ret:
                return rules
            result, _ = expr.do_apply_rules(rules, evaluation)
            return result
        except PatternError:
            evaluation.message("Replace", "reps", rules)
            return None


class ReplaceRepeated(BinaryOperator):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ReplaceRepeated.html</url>

    <dl>
      <dt>'ReplaceRepeated[$expr$, $x$ -> $y$]'
      <dt>'$expr$ //. $x$ -> $y$'
      <dd>repeatedly applies the rule '$x$ -> $y$' to $expr$ until
        the result no longer changes.
    </dl>

    >> a+b+c //. c->d
     = a + b + d

    >> f = ReplaceRepeated[c->d];
    >> f[a+b+c]
     = a + b + d
    >> Clear[f];

    Simplification of logarithms:
    >> logrules = {Log[x_ * y_] :> Log[x] + Log[y], Log[x_ ^ y_] :> y * Log[x]};
    >> Log[a * (b * c) ^ d ^ e * f] //. logrules
     = Log[a] + Log[f] + (Log[b] + Log[c]) d ^ e
    'ReplaceAll' just performs a single replacement:
    >> Log[a * (b * c) ^ d ^ e * f] /. logrules
     = Log[a] + Log[f (b c) ^ d ^ e]
    """

    grouping = "Left"
    needs_verbatim = True
    operator = "//."

    messages = {
        "reps": "`1` is not a valid replacement rule.",
        "rmix": "Elements of `1` are a mixture of lists and nonlists.",
    }

    options = {
        "MaxIterations": "65535",
    }

    rules = {
        "ReplaceRepeated[rules_][expr_]": "ReplaceRepeated[expr, rules]",
    }
    summary_text = "iteratively replace until the expression does not change anymore"

    def eval_list(
        self,
        expr: BaseElement,
        rules: BaseElement,
        evaluation: Evaluation,
        options: dict,
    ) -> OptionalType[BaseElement]:
        "ReplaceRepeated[expr_, rules_, OptionsPattern[ReplaceRepeated]]"
        try:
            rules, ret = create_rules(rules, expr, "ReplaceRepeated", evaluation)
        except PatternError:
            evaluation.message("Replace", "reps", rules)
            return None

        if ret:
            return rules

        maxit = self.get_option(options, "MaxIterations", evaluation)
        if maxit.is_numeric(evaluation):
            maxit = maxit.get_int_value()
        else:
            maxit = -1

        while True:
            evaluation.check_stopped()
            if maxit == 0:
                break
            maxit -= 1
            result, applied = expr.do_apply_rules(rules, evaluation)
            if applied:
                result = result.evaluate(evaluation)
            if applied and not result.sameQ(expr):
                expr = result
            else:
                break

        return result


class ReplaceList(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ReplaceList.html</url>

    <dl>
      <dt>'ReplaceList[$expr$, $rules$]'
      <dd>returns a list of all possible results when applying $rules$ \
        to $expr$.
      <dt>'ReplaceList[$expr$, $rules$, $n$]'
      <dd>returns a list of at most $n$ results when applying $rules$ \
        to $expr$.
    </dl>

    Get all subsequences of a list:
    >> ReplaceList[{a, b, c}, {___, x__, ___} -> {x}]
     = {{a}, {a, b}, {a, b, c}, {b}, {b, c}, {c}}
    You can specify the maximum number of items:
    >> ReplaceList[{a, b, c}, {___, x__, ___} -> {x}, 3]
     = {{a}, {a, b}, {a, b, c}}
    >> ReplaceList[{a, b, c}, {___, x__, ___} -> {x}, 0]
     = {}
    If no rule matches, an empty list is returned:
    >> ReplaceList[a, b->x]
     = {}

    Like in 'ReplaceAll', $rules$ can be a nested list:
    >> ReplaceList[{a, b, c}, {{{___, x__, ___} -> {x}}, {{a, b, c} -> t}}, 2]
     = {{{a}, {a, b}}, {t}}
    >> ReplaceList[expr, {}, -1]
     : Non-negative integer or Infinity expected at position 3.
     = ReplaceList[expr, {}, -1]

    Possible matches for a sum:
    >> ReplaceList[a + b + c, x_ + y_ -> {x, y}]
     = {{a, b + c}, {b, a + c}, {c, a + b}, {a + b, c}, {a + c, b}, {b + c, a}}
    """

    messages = {
        "reps": "`1` is not a valid replacement rule.",
        "rmix": "Elements of `1` are a mixture of lists and nonlists.",
    }
    summary_text = "list of possible replacement results"

    def eval(
        self,
        expr: BaseElement,
        rules: BaseElement,
        maxidx: Number,
        evaluation: Evaluation,
    ) -> OptionalType[BaseElement]:
        "ReplaceList[expr_, rules_, maxidx_:Infinity]"

        # TODO: the below handles Infinity getting added as a
        # default argument, when it is passed explitly, e.g.
        # ReplaceList[expr, {}, Infinity], then Infinity
        # comes in as DirectedInfinity[1].
        if maxidx == SymbolInfinity:
            max_count = None
        else:
            max_count = maxidx.get_int_value()
            if max_count is None or max_count < 0:
                evaluation.message("ReplaceList", "innf", 3)
                return None
        try:
            rules, ret = create_rules(
                rules, expr, "ReplaceList", evaluation, extra_args=[maxidx]
            )
        except PatternError:
            evaluation.message("Replace", "reps", rules)
            return None

        if ret:
            return rules

        list_result = []
        for rule in rules:
            result = rule.apply(expr, evaluation, return_list=True, max_list=max_count)
            list_result.extend(result)

        return ListExpression(*list_result)


class Dispatch(Atom):
    class_head_name = "System`Dispatch"

    def __init__(self, rulelist: Expression, evaluation: Evaluation) -> None:
        self.src = ListExpression(*rulelist)
        self.rules = [Rule(rule.elements[0], rule.elements[1]) for rule in rulelist]
        self._elements = None
        self._head = SymbolDispatch

    def get_sort_key(self, pattern_sort: bool = False) -> tuple:
        return self.src.get_sort_key()

    def get_atom_name(self):
        return "System`Dispatch"

    def __repr__(self):
        return "dispatch"

    def atom_to_boxes(self, f: Symbol, evaluation: Evaluation):
        from mathics.builtin.box.layout import RowBox
        from mathics.eval.makeboxes import format_element

        box_element = format_element(self.src, evaluation, f)
        return RowBox(String("Dispatch"), String("["), box_element, String("]"))


class DispatchAtom(AtomBuiltin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/DispatchAtom.html</url>

    <dl>
      <dt>'Dispatch[$rulelist$]'
      <dd>Introduced for compatibility. Currently, it just return $rulelist$. \
          In the future, it should return an optimized DispatchRules atom, \
          containing an optimized set of rules.
    </dl>

    >> rules = {{a_,b_}->a^b, {1,2}->3., F[x_]->x^2};
    >> F[2] /. rules
     = 4
    >> dispatchrules = Dispatch[rules]
     =  Dispatch[{{a_, b_} -> a ^ b, {1, 2} -> 3., F[x_] -> x ^ 2}]
    >>  F[2] /. dispatchrules
     = 4
    """

    class_head_name = "System`DispatchAtom"
    messages = {
        "invrpl": "`1` is not a valid rule or list of rules.",
    }
    summary_text = "convert a list of rules in an optimized dispatch rules atom"

    def __repr__(self):
        return "dispatchatom"

    def eval_create(
        self, rules: ListExpression, evaluation: Evaluation
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
        if isinstance(rules, Dispatch):
            return rules
        if isinstance(rules, Symbol):
            rules = rules.evaluate(evaluation)

        if rules.has_form("List", None):
            rules = rules.elements
        else:
            rules = [rules]

        all_list = all(rule.has_form("List", None) for rule in rules)
        if all_list:
            elements = [self.eval_create(rule, evaluation) for rule in rules]
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
        try:
            return Dispatch(flatten_list, evaluation)
        except Exception:
            return None

    def eval_normal(self, dispatch: Dispatch, evaluation: Evaluation) -> ListExpression:
        """Normal[dispatch_Dispatch]"""
        if isinstance(dispatch, Dispatch):
            return dispatch.src
        return dispatch.elements[0]
