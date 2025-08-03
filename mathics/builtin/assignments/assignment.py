# -*- coding: utf-8 -*-
"""
Forms of Assignment
"""
from typing import Optional

from mathics.core.atoms import String
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_HOLD_FIRST,
    A_PROTECTED,
    A_SEQUENCE_HOLD,
)
from mathics.core.builtin import Builtin, InfixOperator
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Atom, Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolFailed
from mathics.eval.assignments import eval_assign
from mathics.eval.pymathics import PyMathicsLoadException, eval_LoadModule


# Placing this here is a bit weird, but it is not clear where else is better
# suited for this right now.
class LoadModule(Builtin):
    """
    ## <url>:mathics native for pymathics:</url>

    <dl>
      <dt>'LoadModule'[$module$]
      <dd>'Load Mathics definitions from the python module $module$
    </dl>

    >> LoadModule["nomodule"]
     : Python import errors with: No module named 'nomodule'.
     = $Failed
    >> LoadModule["sys"]
     : Python module "sys" is not a Mathics3 module.
     = $Failed
    """

    name = "LoadModule"
    messages = {
        "loaderror": """Python import errors with: `1`.""",
        "notmathicslib": """Python module "`1`" is not a Mathics3 module.""",
    }
    summary_text = "load a pymathics module"

    def eval(self, module, evaluation):
        "LoadModule[module_String]"
        try:
            eval_LoadModule(module.value, evaluation.definitions)
        except PyMathicsLoadException:
            evaluation.message(self.name, "notmathicslib", module)
            return SymbolFailed
        except ImportError as exception:
            evaluation.message(self.get_name(), "loaderror", String(str(exception)))
            return SymbolFailed
        return module


class Set(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Set.html</url>

    <dl>
      <dt>'Set'[$expr$, $value$]

      <dt>$expr$ = $value$
      <dd>evaluates $value$ and assigns it to $expr$.

      <dt>{$s_1$, $s_2$, $s_3$} = {$v_1$, $v_2$, $v_3$}
      <dd>sets multiple symbols ($s_1$, $s_2$, ...) to the corresponding \
          values ($v_1$, $v_2$, ...).
    </dl>

    'Set' can be used to give a symbol a value:
    >> a = 3
     = 3
    >> a
     = 3

    An assignment like this creates an ownvalue:
    >> OwnValues[a]
     = {HoldPattern[a] :> 3}

    You can set multiple values at once using lists:
    >> {a, b, c} = {10, 2, 3}
     = {10, 2, 3}
    >> {a, b, {c, {d}}} = {1, 2, {{c1, c2}, {a}}}
     = {1, 2, {{c1, c2}, {10}}}
    >> d
     = 10

    'Set' evaluates its right-hand side immediately and assigns it to
    the left-hand side:
    >> a
     = 1
    >> x = a
     = 1
    >> a = 2
     = 2
    >> x
     = 1

    'Set' always returns the right-hand side, which you can again use
    in an assignment:
    >> a = b = c = 2;
    >> a == b == c == 2
     = True

    'Set' supports assignments to parts:
    >> A = {{1, 2}, {3, 4}};
    >> A[[1, 2]] = 5
     = 5
    >> A
     = {{1, 5}, {3, 4}}
    >> A[[;;, 2]] = {6, 7}
     = {6, 7}
    >> A
     = {{1, 6}, {3, 7}}
    Set a submatrix:
    >> B = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    >> B[[1;;2, 2;;-1]] = {{t, u}, {y, z}};
    >> B
     = {{1, t, u}, {4, y, z}, {7, 8, 9}}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_SEQUENCE_HOLD
    grouping = "Right"

    messages = {
        "setraw": "Cannot assign to raw object `1`.",
        "shape": "Lists `1` and `2` are not the same shape.",
    }

    summary_text = "assign a value"

    def eval(self, lhs, rhs, evaluation):
        "lhs_ = rhs_"

        eval_assign(self, lhs, rhs, evaluation)
        return rhs


class SetDelayed(Set):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/SetDelayed.html</url>

    <dl>
      <dt>'SetDelayed'[$expr$, $value$]

      <dt>$expr$ := $value$
      <dd>assigns $value$ to $expr$, without evaluating $value$.
    </dl>

    'SetDelayed' is like 'Set', except it has attribute 'HoldAll', thus it \
        does not evaluate the right-hand side immediately, but evaluates \
            it when needed.

    >> Attributes[SetDelayed]
     = {HoldAll, Protected, SequenceHold}
    >> a = 1
     = 1
    >> x := a
    >> x
     = 1
    Changing the value of $a$ affects $x$:
    >> a = 2
     = 2
    >> x
     = 2

    'Condition' ('/;') can be used with 'SetDelayed' to make an
    assignment that only holds if a condition is satisfied:
    >> f[x_] := p[x] /; x>0
    >> f[3]
     = p[3]
    >> f[-3]
     = f[-3]
    It also works if the condition is set in the LHS:
    >> F[x_, y_] /; x < y /; x>0  := x / y;
    >> F[x_, y_] := y / x;
    >> F[2, 3]
     = 2 / 3
    >> F[3, 2]
     = 2 / 3
    >> F[-3, 2]
     = -2 / 3
    We can use conditional delayed assignments to define \
    symbols with values conditioned to the context. For example,
    >> ClearAll[a,b]; a/; b>0:= 3
    Set $a$ to have a value of $3$ if certain variable $b$ is positive.\
    So, if this variable is not set, $a$ stays unevaluated:
    >> a
     = a
    If now we assign a positive value to $b$, then $a$ is evaluated:
    >> b=2; a
     =  3
    """

    #  I WMA, if we assign a value without a condition on the LHS,
    # conditional values are never reached. So,
    #
    # Notice however that if we assign an unconditional value to $a$, \
    # this overrides the condition:
    # >> a:=0; a/; b>1:= 3
    # >> a
    # = 0
    #
    # In Mathics, this last line would return 3
    # """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD

    summary_text = "test a delayed value; used in defining functions"

    def eval(
        self, lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
    ) -> Symbol:
        "lhs_ := rhs_"

        if eval_assign(self, lhs, rhs, evaluation):
            return SymbolNull

        return SymbolFailed


class TagSet(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TagSet.html</url>

    <dl>
      <dt>'TagSet'[$f$, $expr$, $value$]

      <dt>$f$ '/:' $expr$ '=' $value$
      <dd>assigns $value$ to $expr$, associating the corresponding assignment \
          with the symbol $f$.
    </dl>

    Create an upvalue without using 'UpSet':
    >> square /: area[square[s_]] := s^2
    >> DownValues[square]
     = {}

    >> UpValues[square]
     = {HoldPattern[area[square[s_]]] :> s ^ 2}

    The symbol $f$ must appear as the ultimate head of $lhs$ or as the head \
        of an element in $lhs$:
    >> x /: f[g[x]] = 3;
     : Tag x not found or too deep for an assigned rule.
    >> g /: f[g[x]] = 3;
    >> f[g[x]]
     = 3
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD

    messages = {
        "tagnfd": "Tag `1` not found or too deep for an assigned rule.",
    }
    summary_text = (
        "assign a value to an expression, associating the "
        "corresponding assignment with the a symbol"
    )

    def eval(
        self,
        f: BaseElement,
        lhs: BaseElement,
        rhs,
        evaluation: Evaluation,
    ) -> Optional[BaseElement]:
        "f_ /: lhs_ = rhs_"

        tag_name = f.get_name()
        if not tag_name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return None

        rhs = rhs.evaluate(evaluation)
        eval_assign(self, lhs, rhs, evaluation, tags=[tag_name])
        return rhs


class TagSetDelayed(TagSet):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/TagSetDelayed.html</url>

    <dl>
      <dt>'TagSetDelayed'[$f$, $expr$, $value$]

      <dt>'$f$ /: $expr$ := $value$'
      <dd>is the delayed version of 'TagSet'.
    </dl>
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD
    summary_text = (
        "assign a delayed value to an expression, associating "
        "the corresponding assignment with the a symbol"
    )

    def eval(
        self,
        f: BaseElement,
        lhs: BaseElement,
        rhs: BaseElement,
        evaluation: Evaluation,
    ) -> Optional[Symbol]:
        "f_ /: lhs_ := rhs_"

        tag_name = f.get_name()
        if not tag_name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return None

        if eval_assign(self, lhs, rhs, evaluation, tags=[tag_name]):
            return SymbolNull

        return SymbolFailed


class UpSet(InfixOperator):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/UpSet.html</url>

    <dl>
      <dt>$f$[$x$] '^=' $expression$
      <dd>evaluates $expression$ and assigns it to the value of $f$[$x$], \
          associating the value with $x$.
    </dl>

    'UpSet' creates an upvalue:
    >> a[b] ^= 3;
    >> DownValues[a]
     = {}
    >> UpValues[b]
     = {HoldPattern[a[b]] :> 3}

    You can use 'UpSet' to specify special values like format values.
    However, these values will not be saved in 'UpValues':
    >> Format[r] ^= "custom";
    >> r
     = custom
    >> UpValues[r]
     = {}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_SEQUENCE_HOLD
    grouping = "Right"

    summary_text = (
        "set value and associate the assignment with symbols that occur at level one"
    )

    def eval(
        self, lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
    ) -> Optional[BaseElement]:
        "lhs_ ^= rhs_"
        if isinstance(lhs, Atom):
            evaluation.message("UpSet", "normal", 1, evaluation.current_expression)
            return None
        eval_assign(self, lhs, rhs, evaluation, upset=True)
        return rhs


class UpSetDelayed(UpSet):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/UpSetDelayed.html</url>

    <dl>
       <dt>'UpSetDelayed'[$expression$, $value$]

       <dt>$expression$ '^:=' $value$
       <dd>assigns $expression$ to the value of $f$[$x$] \
           (without evaluating $expression$), associating the value with $x$.
    </dl>

    >> a[b] ^:= x
    >> x = 2;
    >> a[b]
     = 2
    >> UpValues[b]
     = {HoldPattern[a[b]] :> x}
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD
    summary_text = (
        "set a delayed value and associate the assignment "
        "with symbols that occur at level one"
    )

    def eval(
        self, lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
    ) -> Symbol:
        "lhs_ ^:= rhs_"

        if isinstance(lhs, Atom):
            evaluation.message(
                "UpSetDelayed", "normal", 1, evaluation.current_expression
            )
            return None

        if eval_assign(self, lhs, rhs, evaluation, upset=True):
            return SymbolNull

        return SymbolFailed
