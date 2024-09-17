# -*- coding: utf-8 -*-
"""Evaluation Control


Mathics3 takes an expression that it is given, and evaluates it. Built \
into the evaluation are primitives that allow finer control over the \
process of evaluation in cases where it is needed.
"""

from mathics.core.atoms import Integer
from mathics.core.attributes import A_HOLD_ALL, A_HOLD_ALL_COMPLETE, A_PROTECTED
from mathics.core.builtin import Builtin, Predefined
from mathics.core.evaluation import MAX_RECURSION_DEPTH, set_python_recursion_limit


class RecursionLimit(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$RecursionLimit.html</url>

    <dl>
      <dt>'$RecursionLimit'
      <dd>specifies the maximum allowable recursion depth after which a \
          calculation is terminated.
    </dl>

    Calculations terminated by '$RecursionLimit' return '$Aborted':
    >> a = a + a
     : Recursion depth of 200 exceeded.
     = $Aborted
    >> $RecursionLimit
     = 200

    >> $RecursionLimit = x;
     : Cannot set $RecursionLimit to x; value must be an integer between 20 and 512; use the MATHICS_MAX_RECURSION_DEPTH environment variable to allow higher limits.

    >> $RecursionLimit = 512
     = 512
    >> a = a + a
     : Recursion depth of 512 exceeded.
     = $Aborted
    """

    name = "$RecursionLimit"
    value = 200

    set_python_recursion_limit(value)

    rules = {
        "$RecursionLimit": str(value),
    }

    messages = {
        "reclim": "Recursion depth of `1` exceeded.",
        "limset": (
            "Cannot set $RecursionLimit to `1`; "
            "value must be an integer between 20 and %d; "
            "use the MATHICS_MAX_RECURSION_DEPTH environment variable to allow higher limits."
        )
        % (MAX_RECURSION_DEPTH),
    }

    rules = {
        "$RecursionLimit": str(value),
    }
    summary_text = "maximum recursion depth"

    def evaluate(self, evaluation) -> Integer:
        return Integer(self.value)


class IterationLimit(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/$IterationLimit.html</url>

    <dl>
        <dt>'$IterationLimit'

        <dd>specifies the maximum number of times a reevaluation of an expression may happen.

    </dl>

    Calculations terminated by '$IterationLimit' return '$Aborted':

    > $IterationLimit
     = 1000
    """

    name = "$IterationLimit"
    value = 1000

    rules = {
        "$IterationLimit": str(value),
    }

    messages = {
        "itlim": "Iteration limit of `1` exceeded.",
        "limset": (
            "Cannot set $IterationLimit to `1`; "
            "value must be an integer between 20 and Infinity."
        ),
    }

    rules = {
        "$IterationLimit": str(value),
    }
    summary_text = "maximum number of iterations"

    def evaluate(self, evaluation):
        return Integer(self.value)


class Hold(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Hold.html</url>

    <dl>
    <dt>'Hold[$expr$]'
        <dd>prevents $expr$ from being evaluated.
    </dl>

    >> Attributes[Hold]
     = {HoldAll, Protected}
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "prevent the evaluation"


class HoldComplete(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/HoldComplete.html</url>

    <dl>
    <dt>'HoldComplete[$expr$]'
        <dd>prevents $expr$ from being evaluated, and also prevents
        'Sequence' objects from being spliced into argument lists.
    </dl>

    >> Attributes[HoldComplete]
     = {HoldAllComplete, Protected}
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED
    summary_text = "prevents the evaluation, including the upvalues"


class HoldForm(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/HoldForm.html</url>

    <dl>
    <dt>'HoldForm[$expr$]'
        <dd>is equivalent to 'Hold[$expr$]', but prints as $expr$.
    </dl>

    >> HoldForm[1 + 2 + 3]
     = 1 + 2 + 3

    'HoldForm' has attribute 'HoldAll':
    >> Attributes[HoldForm]
     = {HoldAll, Protected}
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    rules = {
        "MakeBoxes[HoldForm[expr_], f_]": "MakeBoxes[expr, f]",
    }
    summary_text = "prevents the evaluation, prints just the expression"


class Evaluate(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Evaluate.html</url>

    <dl>
    <dt>'Evaluate[$expr$]'
        <dd>forces evaluation of $expr$, even if it occurs inside a
        held argument or a 'Hold' form.
    </dl>

    Create a function $f$ with a held argument:
    >> SetAttributes[f, HoldAll]
    >> f[1 + 2]
     = f[1 + 2]

    'Evaluate' forces evaluation of the argument, even though $f$ has
    the 'HoldAll' attribute:
    >> f[Evaluate[1 + 2]]
     = f[3]

    >> Hold[Evaluate[1 + 2]]
     = Hold[3]
    >> HoldComplete[Evaluate[1 + 2]]
     = HoldComplete[Evaluate[1 + 2]]
    >> Evaluate[Sequence[1, 2]]
     = Sequence[1, 2]
    """

    rules = {
        "Evaluate[Unevaluated[x_]]": "Unevaluated[x]",
        "Evaluate[x___]": "x",
    }
    summary_text = "evaluate the element, disregarding Hold attributes"


class Unevaluated(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Unevaluated.html</url>

    <dl>
    <dt>'Unevaluated[$expr$]'
        <dd>temporarily leaves $expr$ in an unevaluated form when it
        appears as a function argument.
    </dl>

    'Unevaluated' is automatically removed when function arguments are
    evaluated:
    >> Sqrt[Unevaluated[x]]
     = Sqrt[x]

    >> Length[Unevaluated[1+2+3+4]]
     = 4
    'Unevaluated' has attribute 'HoldAllComplete':
    >> Attributes[Unevaluated]
     = {HoldAllComplete, Protected}

    'Unevaluated' is maintained for arguments to non-executed functions:
    >> f[Unevaluated[x]]
     = f[Unevaluated[x]]
    Likewise, its kept in flattened arguments and sequences:
    >> Attributes[f] = {Flat};
    >> f[a, Unevaluated[f[b, c]]]
     = f[a, Unevaluated[b], Unevaluated[c]]
    >> g[a, Sequence[Unevaluated[b], Unevaluated[c]]]
     = g[a, Unevaluated[b], Unevaluated[c]]
    However, unevaluated sequences are kept:
    >> g[Unevaluated[Sequence[a, b, c]]]
     = g[Unevaluated[Sequence[a, b, c]]]

    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED
    summary_text = "keep the element unevaluated, disregarding Hold attributes"


class ReleaseHold(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ReleaseHold.html</url>

    <dl>
    <dt>'ReleaseHold[$expr$]'
        <dd>removes any 'Hold', 'HoldForm', 'HoldPattern' or
        'HoldComplete' head from $expr$.
    </dl>

    >> x = 3;
    >> Hold[x]
     = Hold[x]
    >> ReleaseHold[Hold[x]]
     = 3
    >> ReleaseHold[y]
     = y
    """

    rules = {
        "ReleaseHold[(Hold|HoldForm|HoldPattern|HoldComplete)[expr_]]": "expr",
        "ReleaseHold[other_]": "other",
    }
    summary_text = "replace a Hold expression by its argument"


class Sequence(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Sequence.html</url>

    <dl>
    <dt>'Sequence[$x1$, $x2$, ...]'
        <dd>represents a sequence of arguments to a function.
    </dl>

    'Sequence' is automatically spliced in, except when a function has attribute 'SequenceHold'
    (like assignment functions).
    >> f[x, Sequence[a, b], y]
     = f[x, a, b, y]
    >> Attributes[Set]
     = {HoldFirst, Protected, SequenceHold}
    >> a = Sequence[b, c];
    >> a
     = Sequence[b, c]

    Apply 'Sequence' to a list to splice in arguments:
    >> list = {1, 2, 3};
    >> f[Sequence @@ list]
     = f[1, 2, 3]

    Inside 'Hold' or a function with a held argument, 'Sequence' is
    spliced in at the first level of the argument:
    >> Hold[a, Sequence[b, c], d]
     = Hold[a, b, c, d]
    If 'Sequence' appears at a deeper level, it is left unevaluated:
    >> Hold[{a, Sequence[b, c], d}]
     = Hold[{a, Sequence[b, c], d}]
    """

    summary_text = (
        "a sequence of arguments that will automatically be spliced into any function"
    )
