# -*- coding: utf-8 -*-
"""
Defining, applying and compiling rules.

<url>
:WMA link:
https://reference.wolfram.com/language/guide/Rules.html</url>


Rules are a basic element in the evaluation process. Every Definition in \
\\Mathics consists of a set of rules associated with a symbol. \
The evaluation process consists of the sequential application of rules \
associated with the symbols appearing in a given expression. \
The process iterates until no rules match the final expression.

In \\Mathics, rules consist of a Pattern object $pat$ and an \
Expression $repl$. When the Rule is applied to a symbolic \
Expression $expr$, the interpreter tries to match the pattern with \
subexpressions of $expr$ in a top-to-bottom way. If a match is found, the \
subexpression is then replaced by $repl$.

If the $pat$ includes named subpatterns, symbols in $repl$ associated with \
that name are replaced by the (sub) match in the final expression.

Let us consider, for example, the 'Rule':

    >> rule = F[u_]->g[u]
     = F[u_] -> g[u]

This rule associates the pattern 'F[u_]' with the expression 'g[u]'.

Then, using the 'Replace' operator '/.' we can apply the rule to an expression

    >> a + F[x ^ 2] /. rule
     = a + g[x ^ 2]


Notice that the rule is applied from top to bottom just once:

    >> a + F[F[x ^ 2]] /. rule
     = a + g[F[x ^ 2]]

Here, the subexpression 'F[F[x^2]]' matches with the pattern, and the named \
subpattern 'u_' matches with 'F[x^2]'. The original expression is then \
replaced by 'g[u]', and 'u' is replaced with the subexpression that \
matches the subpattern ('F[x ^ 2]').

Notice also that the rule is applied just once. We can apply it recursively \
until no further matches are found by using the 'ReplaceRepeated' operator '//.':

   >> a + F[F[x ^ 2]] //. rule
    = a + g[g[x ^ 2]]

Rules are kept as expressions until a 'Replace' expression is evaluated. \
At that moment, 'Pattern' objects are 'compiled', taking into account the \
attributes of the symbols involved. To make the repeated application of the \
same rule over different expressions faster, it is convenient to use \
'Dispatch' tables. These expressions store precompiled versions of \
a list of rules, avoiding repeating the 'compilation' step each time \
the rules are applied.

   >> dispatchrule = Dispatch[{rule}]
    = Dispatch[<1>]
   >> a + F[F[x ^ 2]] //. dispatchrule
    = a + g[g[x ^ 2]]


"""

from typing import Optional as OptionalType

from mathics.core.atoms import Integer, Integer0, Integer2, Integer3, Number
from mathics.core.attributes import A_HOLD_REST, A_PROTECTED, A_SEQUENCE_HOLD
from mathics.core.builtin import AtomBuiltin, Builtin, InfixOperator, PatternError
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import InvalidLevelspecError
from mathics.core.expression import Expression, ExpressionInfinity
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolTrue
from mathics.core.systemsymbols import (
    SymbolInfinity,
    SymbolReplaceList,
    SymbolRule,
    SymbolRuleDelayed,
)
from mathics.eval.rules import (
    Dispatch,
    create_rules,
    eval_dispatch_atom,
    eval_replace_with_levelspec,
)

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.defining-applying-and-compiling-rules"


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
     =  Dispatch[<3>]
    >>  F[2] /. dispatchrules
     = 4
    """

    class_head_name = "System`DispatchAtom"
    messages = {
        "argt": "Dispatch called with `1` arguments; 1 argument is expected.",
        "invrpl": "`1` is not a valid rule or list of rules.",
    }
    summary_text = "convert a list of rules in an optimized dispatch-rules atom"

    def __repr__(self):
        return "dispatchatom"

    def eval_empty(self, evaluation: Evaluation):
        "Dispatch[]"
        evaluation.message("Dispatch", "argt", Integer0)

    def eval_list(
        self, rules: ListExpression, evaluation: Evaluation
    ) -> OptionalType[BaseElement]:
        """Dispatch[rules_List]"""
        result = eval_dispatch_atom(rules, evaluation)
        return result

    def eval(
        self, rules: Expression, evaluation: Evaluation
    ) -> OptionalType[BaseElement]:
        """Dispatch[rules_]"""
        if not isinstance(rules, Expression):
            return None

        if isinstance(rules, Dispatch):
            return rules

        if isinstance(rules, ListExpression):
            rules_tuple = rules.elements
        elif rules.head in (SymbolRule, SymbolRuleDelayed) and len(rules.elements) == 2:
            rules_tuple = (rules,)
        else:
            return None

        assert isinstance(rules_tuple, tuple)
        result = eval_dispatch_atom(rules_tuple, evaluation)
        return result

    def eval_normal(self, dispatch: Dispatch, evaluation: Evaluation) -> ListExpression:
        """Normal[dispatch_Dispatch]"""
        if isinstance(dispatch, Dispatch):
            return dispatch.src
        return dispatch.elements[0]


class Replace(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Replace.html</url>

    <dl>
      <dt>'Replace[$expr$, $x$ -> $y$]'
      <dd>yields the result of replacing $expr$ with $y$ if it \
        matches the pattern $x$.
      <dt>'Replace[$expr$, $x$ -> $y$, $levelspec$]'
      <dd>replaces only subexpressions at levels specified through \
        $levelspec$.
      <dt>'Replace[$expr$, {$x$ -> $y$, ...}]'
      <dd>performs replacement with multiple rules, yielding a \
        single result expression.
      <dt>'Replace[$expr$, {{$a$ -> $b$, ...}, {$c$ -> $d$, ...}, ...}]'
      <dd>returns a list containing the result of performing each \
        set of replacements.
    </dl>

    >> Replace[x, {x -> 2}]
     = 2

    By default, only the top level is searched for matches:
    >> Replace[1 + x, {x -> 2}]
     = 1 + x

    >> Replace[x, {{x -> 1}, {x -> 2}}]
     = {1, 2}

    Replace stops after the first replacement:
    >> Replace[x, {x -> {}, _List -> y}]
     = {}

    Replace replaces the deepest levels first:
    >> Replace[x[1], {x[1] -> y, 1 -> 2}, All]
     = x[2]

    By default, heads are not replaced:
    >> Replace[x[x[y]], x -> z, All]
     = x[x[y]]

    Heads can be replaced using the 'Heads' option:
    >> Replace[x[x[y]], x -> z, All, Heads -> True]
     = z[z[y]]

    Note that heads are handled at the level of elements:
    >> Replace[x[x[y]], x -> z, {1}, Heads -> True]
     = z[x[y]]

    You can use Replace as an operator:
    >> Replace[{x_ -> x + 1}][10]
     = 11
    """

    messages = {
        "rmix": "Elements of `1` are a mixture of lists and nonlists.",
    }

    options = {"Heads": "False"}
    rules = {"Replace[rules_][expr_]": "Replace[expr, rules]"}
    summary_text = "apply a replacement rule"

    def eval_levelspec(self, expr, rules, ls, evaluation, options):
        "Replace[expr_, rules_, Optional[Pattern[ls, _?LevelQ], {0}], OptionsPattern[Replace]]"
        try:
            heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
            return eval_replace_with_levelspec(
                expr, rules, ls, heads, evaluation, options
            )
        except InvalidLevelspecError:
            evaluation.message("General", "level", ls)

        except PatternError:
            evaluation.message("Replace", "rep", rules)

        return None


class ReplaceAll(InfixOperator):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ReplaceAll.html</url>

    <dl>
      <dt>'ReplaceAll[$expr$, $x$ -> $y$]'
      <dt>'$expr$ /. $x$ -> $y$'
      <dd>yields the result of replacing all subexpressions of \
        $expr$ matching the pattern $x$ with $y$.
      <dt>'$expr$ /. {$x$ -> $y$, ...}'
      <dd>performs replacement with multiple rules, yielding a \
        single result expression.
      <dt>'$expr$ /. {{$a$ -> $b$, ...}, {$c$ -> $d$, ...}, ...}'
      <dd>returns a list containing the result of performing each \
        set of replacements.
    </dl>

    >> a+b+c /. c->d
     = a + b + d
    >> g[a+b+c,a]/.g[x_+y_,x_]->{x,y}
     = {a, b + c}

    If $rules$ is a list of lists, a list of all possible respective \
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

    Possible matches for a sum:
    >> ReplaceList[a + b + c, x_ + y_ -> {x, y}]
     = {{a, b + c}, {b, a + c}, {c, a + b}, {a + b, c}, {a + c, b}, {b + c, a}}
    """

    messages = {
        "reps": "`1` is not a valid replacement rule.",
        "rmix": "Elements of `1` are a mixture of lists and nonlists.",
    }
    summary_text = "list possible replacement results"

    def eval(
        self,
        expr: BaseElement,
        rules: BaseElement,
        maxidx: Number,
        evaluation: Evaluation,
    ) -> OptionalType[BaseElement]:
        "ReplaceList[expr_, rules_, maxidx_:Infinity]"

        # TODO: the below handles Infinity getting added as a
        # default argument, when it is passed explicitly, e.g.
        # ReplaceList[expr, {}, Infinity], then Infinity
        # comes in as DirectedInfinity[1].
        if maxidx == SymbolInfinity or ExpressionInfinity == maxidx:
            max_count = None
        else:
            max_count = maxidx.get_int_value()
            if max_count is None or max_count < 0:
                evaluation.message(
                    "ReplaceList",
                    "innf",
                    Integer3,
                    Expression(SymbolReplaceList, expr, rules, maxidx),
                )
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


class ReplaceRepeated(InfixOperator):
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
    summary_text = "replace until the expression does not change anymore"

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
        if maxit is not None and maxit.is_numeric(evaluation):
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


class Rule_(InfixOperator):
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

    attributes = A_SEQUENCE_HOLD | A_PROTECTED
    grouping = "Right"
    name = "Rule"
    needs_verbatim = True

    # FIXME: if we remove this we have problems.
    # We should be able to get this from JSON.
    operator = "->"
    summary_text = "a replacement rule"

    def eval_rule(self, elems, evaluation):
        """Rule[elems___]"""
        num_parms = len(elems.get_sequence())
        if num_parms != 2:
            evaluation.message("Rule", "argrx", "Rule", Integer(num_parms), Integer2)
        return None


class RuleDelayed(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RuleDelayed.html</url>

    <dl>
      <dt>'RuleDelayed[$x$, $y$]'
      <dt>'$x$ :> $y$'
      <dd>represents a rule replacing $x$ with $y$, with $y$ held \
        unevaluated.
    </dl>

    >> Attributes[RuleDelayed]
     = {HoldRest, Protected, SequenceHold}
    """

    attributes = A_SEQUENCE_HOLD | A_HOLD_REST | A_PROTECTED
    needs_verbatim = True
    summary_text = "a rule that keeps the replacement unevaluated"

    def eval_rule_delayed(self, elems, evaluation):
        """RuleDelayed[elems___]"""
        num_parms = len(elems.get_sequence())
        if num_parms != 2:
            evaluation.message(
                "RuleDelayed", "argrx", "RuleDelayed", Integer(num_parms), Integer2
            )
        return None
