# -*- coding: utf-8 -*-
"""
Forms of Assignment
"""


from mathics.builtin.base import BinaryOperator, Builtin
from mathics.core.assignment import (
    ASSIGNMENT_FUNCTION_MAP,
    AssignmentException,
    assign_store_rules_by_tag,
    normalize_lhs,
)
from mathics.core.atoms import String
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_HOLD_FIRST,
    A_PROTECTED,
    A_SEQUENCE_HOLD,
)
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed
from mathics.eval.pymathics import PyMathicsLoadException, eval_LoadModule


class _SetOperator:
    """

    This is the base class for assignment Builtin operators.

    Special cases are determined by the head of the expression. Then
    they are processed by specific routines, which are poke from
    the ``ASSIGNMENT_FUNCTION_MAP`` dict.
    """

    # FIXME:
    # Assigment is determined by the LHS.
    # Are there a larger patterns or natural groupings that we are missing?
    # For example, it might be that it
    # we can key off of some attributes or other properties of the
    # LHS of a builtin, instead of listing all of the builtins in that class
    # (which may miss some).
    # Below, we key on a string, but Symbol is more correct.

    def assign(self, lhs, rhs, evaluation, tags=None, upset=False):
        lhs, lookup_name = normalize_lhs(lhs, evaluation)
        try:
            # Using a builtin name, find which assignment procedure to perform,
            # and then call that function.
            assignment_func = ASSIGNMENT_FUNCTION_MAP.get(lookup_name, None)
            if assignment_func:
                return assignment_func(self, lhs, rhs, evaluation, tags, upset)

            return assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset)
        except AssignmentException:

            return False


# Placing this here is a bit weird, but it is not clear where else is better suited for this right now.
class LoadModule(Builtin):
    """
    ## <url>:mathics native for pymathics:</url>

    <dl>
      <dt>'LoadModule[$module$]'
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
        except Exception as e:
            evaluation.message(self.get_name(), "loaderror", String(str(e)))
            return SymbolFailed
        return module


class Set(BinaryOperator, _SetOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Set.html</url>

    <dl>
      <dt>'Set[$expr$, $value$]'

      <dt>$expr$ = $value$
      <dd>evaluates $value$ and assigns it to $expr$.

      <dt>{$s1$, $s2$, $s3$} = {$v1$, $v2$, $v3$}
      <dd>sets multiple symbols ($s1$, $s2$, ...) to the corresponding values ($v1$, $v2$, ...).
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

    #> x = Infinity;
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_SEQUENCE_HOLD
    grouping = "Right"

    messages = {
        "setraw": "Cannot assign to raw object `1`.",
        "shape": "Lists `1` and `2` are not the same shape.",
    }

    operator = "="
    precedence = 40

    summary_text = "assign a value"

    def eval(self, lhs, rhs, evaluation):
        "lhs_ = rhs_"

        self.assign(lhs, rhs, evaluation)
        return rhs


class SetDelayed(Set):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/SetDelayed.html</url>

    <dl>
      <dt>'SetDelayed[$expr$, $value$]'

      <dt>$expr$ := $value$
      <dd>assigns $value$ to $expr$, without evaluating $value$.
    </dl>

    'SetDelayed' is like 'Set', except it has attribute 'HoldAll', thus it does not evaluate the right-hand side immediately, but evaluates it when needed.

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

    operator = ":="
    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD

    summary_text = "test a delayed value; used in defining functions"

    def eval(self, lhs, rhs, evaluation):
        "lhs_ := rhs_"

        if self.assign(lhs, rhs, evaluation):
            return SymbolNull
        else:
            return SymbolFailed


class TagSet(Builtin, _SetOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TagSet.html</url>

    <dl>
      <dt>'TagSet[$f$, $expr$, $value$]'

      <dt>'$f$ /: $expr$ = $value$'
      <dd>assigns $value$ to $expr$, associating the corresponding assignment \
          with the symbol $f$.
    </dl>

    Create an upvalue without using 'UpSet':
    >> x /: f[x] = 2
     = 2
    >> f[x]
     = 2
    >> DownValues[f]
     = {}
    >> UpValues[x]
     = {HoldPattern[f[x]] :> 2}

    The symbol $f$ must appear as the ultimate head of $lhs$ or as the head of an element in $lhs$:
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
    summary_text = "assign a value to an expression, associating the corresponding assignment with the a symbol"

    def eval(self, f, lhs, rhs, evaluation):
        "f_ /: lhs_ = rhs_"

        name = f.get_name()
        if not name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return

        rhs = rhs.evaluate(evaluation)
        self.assign(lhs, rhs, evaluation, tags=[name])
        return rhs


class TagSetDelayed(TagSet):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/TagSetDelayed.html</url>

    <dl>
      <dt>'TagSetDelayed[$f$, $expr$, $value$]'

      <dt>'$f$ /: $expr$ := $value$'
      <dd>is the delayed version of 'TagSet'.
    </dl>
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD
    summary_text = "assign a delayed value to an expression, associating the corresponding assignment with the a symbol"

    def eval(self, f, lhs, rhs, evaluation):
        "f_ /: lhs_ := rhs_"

        name = f.get_name()
        if not name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return

        if self.assign(lhs, rhs, evaluation, tags=[name]):
            return SymbolNull
        else:
            return SymbolFailed


class UpSet(BinaryOperator, _SetOperator):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/UpSet.html</url>

    <dl>
      <dt>$f$[$x$] ^= $expression$
      <dd>evaluates $expression$ and assigns it to the value of $f$[$x$], associating the value with $x$.
    </dl>

    'UpSet' creates an upvalue:
    >> a[b] ^= 3;
    >> DownValues[a]
     = {}
    >> UpValues[b]
     = {HoldPattern[a[b]] :> 3}

    >> a ^= 3
     : Nonatomic expression expected.
     = 3

    You can use 'UpSet' to specify special values like format values.
    However, these values will not be saved in 'UpValues':
    >> Format[r] ^= "custom";
    >> r
     = custom
    >> UpValues[r]
     = {}

    #> f[g, a + b, h] ^= 2
     : Tag Plus in f[g, a + b, h] is Protected.
     = 2
    #> UpValues[h]
     = {HoldPattern[f[g, a + b, h]] :> 2}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_SEQUENCE_HOLD
    grouping = "Right"
    operator = "^="
    precedence = 40

    summary_text = (
        "set value and associate the assignment with symbols that occur at level one"
    )

    def eval(self, lhs, rhs, evaluation):
        "lhs_ ^= rhs_"

        self.assign(lhs, rhs, evaluation, upset=True)
        return rhs


class UpSetDelayed(UpSet):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/UpSetDelayed.html</url>

    <dl>
       <dt>'UpSetDelayed[$expression$, $value$]'

       <dt>'$expression$ ^:= $value$'
       <dd>assigns $expression$ to the value of $f$[$x$] (without evaluating $expression$), associating the value with $x$.
    </dl>

    >> a[b] ^:= x
    >> x = 2;
    >> a[b]
     = 2
    >> UpValues[b]
     = {HoldPattern[a[b]] :> x}

    #> f[g, a + b, h] ^:= 2
     : Tag Plus in f[g, a + b, h] is Protected.
    #> f[a+b] ^:= 2
     : Tag Plus in f[a + b] is Protected.
     = $Failed
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD
    operator = "^:="
    summary_text = "set a delayed value and associate the assignment with symbols that occur at level one"

    def eval(self, lhs, rhs, evaluation):
        "lhs_ ^:= rhs_"

        if self.assign(lhs, rhs, evaluation, upset=True):
            return SymbolNull
        else:
            return SymbolFailed
