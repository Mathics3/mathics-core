# -*- coding: utf-8 -*-
"""
Forms of Assignment
"""


from mathics.builtin.assignments.internals import _SetOperator
from mathics.builtin.base import BinaryOperator, Builtin
from mathics.core.attributes import hold_all, hold_first, protected, sequence_hold
from mathics.core.definitions import PyMathicsLoadException
from mathics.core.evaluators import eval_load_module
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed


class Set(BinaryOperator, _SetOperator):
    """
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

    attributes = hold_first | protected | sequence_hold
    grouping = "Right"

    messages = {
        "setraw": "Cannot assign to raw object `1`.",
        "shape": "Lists `1` and `2` are not the same shape.",
    }

    operator = "="
    precedence = 40

    summary_text = "assign a value"

    def apply(self, lhs, rhs, evaluation):
        "lhs_ = rhs_"

        self.assign(lhs, rhs, evaluation)
        return rhs


class SetDelayed(Set):
    """
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
    """

    operator = ":="
    attributes = hold_all | protected | sequence_hold

    summary_text = "test a delayed value; used in defining functions"

    def apply(self, lhs, rhs, evaluation):
        "lhs_ := rhs_"

        if self.assign(lhs, rhs, evaluation):
            return SymbolNull
        else:
            return SymbolFailed


class TagSet(Builtin, _SetOperator):
    """
    <dl>
      <dt>'TagSet[$f$, $expr$, $value$]'

      <dt>'$f$ /: $expr$ = $value$'
      <dd>assigns $value$ to $expr$, associating the corresponding assignment with the symbol $f$.
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

    attributes = hold_all | protected | sequence_hold

    messages = {
        "tagnfd": "Tag `1` not found or too deep for an assigned rule.",
    }
    summary_text = "assign a value to an expression, associating the corresponding assignment with the a symbol"

    def apply(self, f, lhs, rhs, evaluation):
        "f_ /: lhs_ = rhs_"

        name = f.get_name()
        if not name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return

        rhs = rhs.evaluate(evaluation)
        self.assign_elementary(lhs, rhs, evaluation, tags=[name])
        return rhs


class TagSetDelayed(TagSet):
    """
    <dl>
      <dt>'TagSetDelayed[$f$, $expr$, $value$]'

      <dt>'$f$ /: $expr$ := $value$'
      <dd>is the delayed version of 'TagSet'.
    </dl>
    """

    attributes = hold_all | protected | sequence_hold
    summary_text = "assign a delayed value to an expression, associating the corresponding assignment with the a symbol"

    def apply(self, f, lhs, rhs, evaluation):
        "f_ /: lhs_ := rhs_"

        name = f.get_name()
        if not name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return

        if self.assign_elementary(lhs, rhs, evaluation, tags=[name]):
            return SymbolNull
        else:
            return SymbolFailed


# Placing this here is a bit weird, but it is not clear where else is better suited for this right now.
class LoadModule(Builtin):
    """
    <dl>
      <dt>'LoadModule[$module$]'
      <dd>'Load Mathics definitions from the python module $module$
    </dl>
    >> LoadModule["nomodule"]
     : Python module nomodule does not exist.
     = $Failed
    >> LoadModule["sys"]
     : Python module sys is not a pymathics module.
     = $Failed
    """

    name = "LoadModule"
    messages = {
        "notfound": "Python module `1` does not exist.",
        "notmathicslib": "Python module `1` is not a pymathics module.",
    }
    summary_text = "load a pymathics module"

    def apply(self, module, evaluation):
        "LoadModule[module_String]"
        try:
            eval_load_module(module.value, evaluation)
        except PyMathicsLoadException:
            evaluation.message(self.name, "notmathicslib", module)
            return SymbolFailed
        except ImportError:
            evaluation.message(self.get_name(), "notfound", module)
            return SymbolFailed
        return module
