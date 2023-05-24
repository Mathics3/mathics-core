# -*- coding: utf-8 -*-

"""
Procedural Programming

Procedural programming is a programming paradigm, derived from imperative \
programming, based on the concept of the procedure call. This term is \
sometimes compared and contrasted with Functional Programming.

Procedures (a type of routine or subroutine) simply contain a series of \
computational steps to be carried out. Any given procedure might be called \
at any point during a program's execution, including by other procedures \
or itself.

Procedural functions are integrated into \Mathics symbolic programming \
environment.
"""


from mathics.builtin.base import BinaryOperator, Builtin, IterationFunction
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_HOLD_REST,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.expression import Expression
from mathics.core.interrupt import (
    AbortInterrupt,
    BreakInterrupt,
    ContinueInterrupt,
    ReturnInterrupt,
    WLThrowInterrupt,
)
from mathics.core.symbols import Symbol, SymbolFalse, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import SymbolMatchQ
from mathics.eval.patterns import match

SymbolWhich = Symbol("Which")


class Abort(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Abort.html</url>

    <dl>
      <dt>'Abort[]'
      <dd>aborts an evaluation completely and returns '$Aborted'.
    </dl>
    >> Print["a"]; Abort[]; Print["b"]
     | a
     = $Aborted
    """

    summary_text = "generate an abort"

    def eval(self, evaluation):
        "Abort[]"

        raise AbortInterrupt


class Break(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Break.html</url>

    <dl>
      <dt>'Break[]'
      <dd>exits a 'For', 'While', or 'Do' loop.
    </dl>
    >> n = 0;
    >> While[True, If[n>10, Break[]]; n=n+1]
    >> n
     = 11
    """

    messages = {
        "nofwd": "No enclosing For, While, or Do found for Break[].",
    }

    summary_text = "exit a 'For', 'While', or 'Do' loop"

    def eval(self, evaluation):
        "Break[]"

        raise BreakInterrupt


class Catch(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Catch.html</url>

    <dl>
      <dt>'Catch[$expr$]'
      <dd> returns the argument of the first 'Throw' generated in the evaluation of $expr$.

      <dt>'Catch[$expr$, $form$]'
      <dd> returns value from the first 'Throw[$value$, $tag$]' for which $form$ matches $tag$.

      <dt>'Catch[$expr$, $form$, $f$]'
      <dd> returns $f$[$value$, $tag$].
    </dl>

    Exit to the enclosing 'Catch' as soon as 'Throw' is evaluated:
    >> Catch[r; s; Throw[t]; u; v]
     = t

    Define a function that can "throw an exception":
    >> f[x_] := If[x > 12, Throw[overflow], x!]

    The result of 'Catch' is just what is thrown by 'Throw':
    >> Catch[f[1] + f[15]]
     = overflow
    >> Catch[f[1] + f[4]]
     = 25

    #> Clear[f]
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    summary_text = "handle an exception raised by a 'Throw'"

    def eval_expr(self, expr, evaluation):
        "Catch[expr_]"
        try:
            ret = expr.evaluate(evaluation)
        except WLThrowInterrupt as e:
            return e.value
        return ret

    def eval_with_form_and_fn(self, expr, form, f, evaluation):
        "Catch[expr_, form_, f__:Identity]"
        try:
            ret = expr.evaluate(evaluation)
        except WLThrowInterrupt as e:
            # TODO: check that form match tag.
            # otherwise, re-raise the exception
            match = Expression(SymbolMatchQ, e.tag, form).evaluate(evaluation)
            if match is SymbolTrue:
                return Expression(f, e.value)
            else:
                # A plain raise hide, this path and preserves the traceback
                # of the call that was originally given.
                raise
        return ret


class CompoundExpression(BinaryOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/CompoundExpression.html</url>

    <dl>
      <dt>'CompoundExpression[$e1$, $e2$, ...]'
      <dt>'$e1$; $e2$; ...'
        <dd>evaluates its arguments in turn, returning the last result.
    </dl>

    >> a; b; c; d
     = d
    If the last argument is omitted, 'Null' is taken:
    >> a;

    ## Parser Tests
    #> FullForm[Hold[; a]]
     : "FullForm[Hold[" cannot be followed by "; a]]" (line 1 of "<test>").
    #> FullForm[Hold[; a ;]]
     : "FullForm[Hold[" cannot be followed by "; a ;]]" (line 1 of "<test>").

    ## Issue331
    #> CompoundExpression[x, y, z]
     = z
    #> %
     = z

    #> CompoundExpression[x, y, Null]
    #> %
     = y

    #> CompoundExpression[CompoundExpression[x, y, Null], Null]
    #> %
     = y

    #> CompoundExpression[x, Null, Null]
    #> %
     = x

    #> CompoundExpression[]
    #> %

    ## Issue 531
    #> z = Max[1, 1 + x]; x = 2; z
     = 3

    #> Clear[x]; Clear[z]
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_READ_PROTECTED
    operator = ";"
    precedence = 10

    summary_text = "execute expressions in sequence"

    def eval(self, expr, evaluation):
        "CompoundExpression[expr___]"

        items = expr.get_sequence()
        result = SymbolNull

        for expr in items:
            prev_result = result
            result = expr.evaluate(evaluation)

            # `expr1; expr2;` returns `Null` but assigns `expr2` to `Out[n]`.
            # even stranger `CompoundExpression[expr1, Null, Null]` assigns `expr1` to `Out[n]`.
            if result is SymbolNull and prev_result != SymbolNull:
                evaluation.predetermined_out = prev_result

        return result


class Continue(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Continue.html</url>

    <dl>
      <dt>'Continue[]'
      <dd>continues with the next iteration in a 'For', 'While', or 'Do' loop.
    </dl>

    >> For[i=1, i<=8, i=i+1, If[Mod[i,2] == 0, Continue[]]; Print[i]]
     | 1
     | 3
     | 5
     | 7
    """

    messages = {
        "nofwd": "No enclosing For, While, or Do found for Continue[].",
    }

    summary_text = "continue with the next iteration in a 'For', 'While' or 'Do' loop"

    def eval(self, evaluation):
        "Continue[]"

        raise ContinueInterrupt


class Do(IterationFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Do.html</url>

    <dl>
      <dt>'Do[$expr$, {$max$}]'
      <dd>evaluates $expr$ $max$ times.

      <dt>'Do[$expr$, {$i$, $max$}]'
      <dd>evaluates $expr$ $max$ times, substituting $i$ in $expr$ with values from 1 to $max$.

      <dt>'Do[$expr$, {$i$, $min$, $max$}]'
      <dd>starts with '$i$ = $max$'.

      <dt>'Do[$expr$, {$i$, $min$, $max$, $step$}]'
      <dd>uses a step size of $step$.

      <dt>'Do[$expr$, {$i$, {$i1$, $i2$, ...}}]'
      <dd>uses values $i1$, $i2$, ... for $i$.

      <dt>'Do[$expr$, {$i$, $imin$, $imax$}, {$j$, $jmin$, $jmax$}, ...]'
      <dd>evaluates $expr$ for each $j$ from $jmin$ to $jmax$, for each $i$ from $imin$ to $imax$, etc.
    </dl>
    >> Do[Print[i], {i, 2, 4}]
     | 2
     | 3
     | 4
    >> Do[Print[{i, j}], {i,1,2}, {j,3,5}]
     | {1, 3}
     | {1, 4}
     | {1, 5}
     | {2, 3}
     | {2, 4}
     | {2, 5}
    You can use 'Break[]' and 'Continue[]' inside 'Do':
    >> Do[If[i > 10, Break[], If[Mod[i, 2] == 0, Continue[]]; Print[i]], {i, 5, 20}]
     | 5
     | 7
     | 9

    #> Do[Print["hi"],{1+1}]
     | hi
     | hi
    """

    allow_loopcontrol = True
    summary_text = "evaluate an expression looping over a variable"

    def get_result(self, items):
        return SymbolNull


class For(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/For.html</url>

    <dl>
      <dt>'For[$start$, $test$, $incr$, $body$]'
      <dd>evaluates $start$, and then iteratively $body$ and $incr$ as long as $test$ evaluates to 'True'.

      <dt>'For[$start$, $test$, $incr$]'
      <dd>evaluates only $incr$ and no $body$.

      <dt>'For[$start$, $test$]'
      <dd>runs the loop without any body.
    </dl>

    Compute the factorial of 10 using 'For':
    >> n := 1
    >> For[i=1, i<=10, i=i+1, n = n * i]
    >> n
     = 3628800
    >> n == 10!
     = True

    #> n := 1
    #> For[i=1, i<=10, i=i+1, If[i > 5, Return[i]]; n = n * i]
     = 6
    #> n
     = 120
    """

    attributes = A_HOLD_REST | A_PROTECTED
    rules = {
        "For[start_, test_, incr_]": "For[start, test, incr, Null]",
    }
    summary_text = "a 'For' loop"

    def eval(self, start, test, incr, body, evaluation):
        "For[start_, test_, incr_, body_]"
        while test.evaluate(evaluation) is SymbolTrue:
            evaluation.check_stopped()
            try:
                try:
                    body.evaluate(evaluation)
                except ContinueInterrupt:
                    pass
                try:
                    incr.evaluate(evaluation)
                except ContinueInterrupt:
                    # Critical, most likely leads to an infinite loop
                    pass
            except BreakInterrupt:
                break
            except ReturnInterrupt as e:
                return e.expr
        return SymbolNull


class If(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/If.html</url>

    <dl>
      <dt>'If[$cond$, $pos$, $neg$]'
      <dd>returns $pos$ if $cond$ evaluates to 'True', and $neg$ if it evaluates to 'False'.

      <dt>'If[$cond$, $pos$, $neg$, $other$]'
      <dd>returns $other$ if $cond$ evaluates to neither 'True' nor 'False'.

      <dt>'If[$cond$, $pos$]'
      <dd>returns 'Null' if $cond$ evaluates to 'False'.
    </dl>

    >> If[1<2, a, b]
     = a
    If the second branch is not specified, 'Null' is taken:
    >> If[1<2, a]
     = a
    >> If[False, a] //FullForm
     = Null

    You might use comments (inside '(*' and '*)') to make the branches of 'If' more readable:
    >> If[a, (*then*) b, (*else*) c];
    """

    summary_text = "if-then-else conditional expression"
    # this is the WR summary: "test if a condition is true, false, or of unknown truth value"
    attributes = A_HOLD_REST | A_PROTECTED
    summary_text = "test if a condition is true, false, or of unknown truth value"

    def eval(self, condition, t, evaluation):
        "If[condition_, t_]"

        if condition is SymbolTrue:
            return t.evaluate(evaluation)
        elif condition is SymbolFalse:
            return SymbolNull

    def eval_with_false(self, condition, t, f, evaluation):
        "If[condition_, t_, f_]"

        if condition is SymbolTrue:
            return t.evaluate(evaluation)
        elif condition is SymbolFalse:
            return f.evaluate(evaluation)

    def eval_with_false_and_other(self, condition, t, f, u, evaluation):
        "If[condition_, t_, f_, u_]"

        if condition is SymbolTrue:
            return t.evaluate(evaluation)
        elif condition is SymbolFalse:
            return f.evaluate(evaluation)
        else:
            return u.evaluate(evaluation)


class Interrupt(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Interrupt.html</url>

    <dl>
      <dt>'Interrupt[]'
      <dd>Interrupt an evaluation and returns '$Aborted'.
    </dl>
    >> Print["a"]; Interrupt[]; Print["b"]
     | a
     = $Aborted
    """

    summary_text = "interrupt evaluation and return '$Aborted'"

    def eval(self, evaluation):
        "Interrupt[]"

        raise AbortInterrupt


class Return(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Return.html</url>

    <dl>
      <dt>'Return[$expr$]'
      <dd>aborts a function call and returns $expr$.
    </dl>

    >> f[x_] := (If[x < 0, Return[0]]; x)
    >> f[-1]
     = 0

    #> Clear[f]

    >> Do[If[i > 3, Return[]]; Print[i], {i, 10}]
     | 1
     | 2
     | 3

    'Return' only exits from the innermost control flow construct.
    >> g[x_] := (Do[If[x < 0, Return[0]], {i, {2, 1, 0, -1}}]; x)
    >> g[-1]
     = -1

    #> h[x_] := (If[x < 0, Return[]]; x)
    #> h[1]
     = 1
    #> h[-1]

    ## Issue 513
    #> f[x_] := Return[x];
    #> g[y_] := Module[{}, z = f[y]; 2]
    #> g[1]
     = 2
    """

    rules = {
        "Return[]": "Return[Null]",
    }

    summary_text = "return from a function"

    def eval(self, expr, evaluation):
        "Return[expr_]"

        raise ReturnInterrupt(expr)


class Switch(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Switch.html</url>

    <dl>
      <dt>'Switch[$expr$, $pattern1$, $value1$, $pattern2$, $value2$, ...]'
      <dd>yields the first $value$ for which $expr$ matches the corresponding \
          $pattern$.
    </dl>

    >> Switch[2, 1, x, 2, y, 3, z]
     = y
    >> Switch[5, 1, x, 2, y]
     = Switch[5, 1, x, 2, y]
    >> Switch[5, 1, x, 2, a, _, b]
     = b
    >> Switch[2, 1]
     : Switch called with 2 arguments. Switch must be called with an odd number of arguments.
     = Switch[2, 1]

    #> a; Switch[b, b]
     : Switch called with 2 arguments. Switch must be called with an odd number of arguments.
     = Switch[b, b]

    ## Issue 531
    #> z = Switch[b, b];
     : Switch called with 2 arguments. Switch must be called with an odd number of arguments.
    #> z
     = Switch[b, b]
    """

    summary_text = "switch based on a value, with patterns allowed"
    attributes = A_HOLD_REST | A_PROTECTED

    messages = {
        "argct": (
            "Switch called with `2` arguments. "
            "Switch must be called with an odd number of arguments."
        ),
    }

    summary_text = "switch based on a value, with patterns allowed"

    def eval(self, expr, rules, evaluation):
        "Switch[expr_, rules___]"

        rules = rules.get_sequence()
        if len(rules) % 2 != 0:
            evaluation.message("Switch", "argct", "Switch", len(rules) + 1)
            return
        for pattern, value in zip(rules[::2], rules[1::2]):
            if match(expr, pattern, evaluation):
                return value.evaluate(evaluation)
        # return unevaluated Switch when no pattern matches


class Which(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Which.html</url>

    <dl>
      <dt>'Which[$cond1$, $expr1$, $cond2$, $expr2$, ...]'
      <dd>yields $expr1$ if $cond1$ evaluates to 'True', $expr2$ if $cond2$ \
          evaluates to 'True', etc.
    </dl>

    >> n = 5;
    >> Which[n == 3, x, n == 5, y]
     = y
    >> f[x_] := Which[x < 0, -x, x == 0, 0, x > 0, x]
    >> f[-3]
     = 3

    #> Clear[f]

    If no test yields 'True', 'Which' returns 'Null':
    >> Which[False, a]

    If a test does not evaluate to 'True' or 'False', evaluation stops
    and a 'Which' expression containing the remaining cases is
    returned:
    >> Which[False, a, x, b, True, c]
     = Which[x, b, True, c]

    'Which' must be called with an even number of arguments:
    >> Which[a, b, c]
     : Which called with 3 arguments.
     = Which[a, b, c]
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "test which of a sequence of conditions are true"

    def eval(self, items, evaluation):
        "Which[items___]"

        items = items.get_sequence()
        nr_items = len(items)
        if len(items) == 1:
            evaluation.message("Which", "argctu", "Which")
            return
        elif len(items) % 2 == 1:
            evaluation.message("Which", "argct", "Which", len(items))
            return
        while items:
            test, item = items[0], items[1]
            test_result = test.evaluate(evaluation)
            if test_result is SymbolTrue:
                return item.evaluate(evaluation)
            elif test_result != SymbolFalse:
                if len(items) == nr_items:
                    return None
                return Expression(SymbolWhich, *items)
            items = items[2:]
        return SymbolNull


class While(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/While.html</url>

    <dl>
      <dt>'While[$test$, $body$]'
      <dd>evaluates $body$ as long as $test$ evaluates to 'True'.

      <dt>'While[$test$]'
      <dd>runs the loop without any body.
    </dl>

    Compute the GCD of two numbers:
    >> {a, b} = {27, 6};
    >> While[b != 0, {a, b} = {b, Mod[a, b]}];
    >> a
     = 3

    #> i = 1; While[True, If[i^2 > 100, Return[i + 1], i++]]
     = 12
    """

    summary_text = "evaluate an expression while a criterion is true"
    attributes = A_HOLD_ALL | A_PROTECTED
    rules = {
        "While[test_]": "While[test, Null]",
    }

    def eval(self, test, body, evaluation):
        "While[test_, body_]"

        while test.evaluate(evaluation) is SymbolTrue:
            try:
                evaluation.check_stopped()
                body.evaluate(evaluation)
            except ContinueInterrupt:
                pass
            except BreakInterrupt:
                break
            except ReturnInterrupt as e:
                return e.expr
        return SymbolNull


class Throw(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Throw.html</url>

    <dl>
      <dt>'Throw[`value`]'
      <dd> stops evaluation and returns `value` as the value of the nearest \
           enclosing 'Catch'.

      <dt>'Catch[`value`, `tag`]'
      <dd> is caught only by `Catch[expr,form]`, where tag matches form.
    </dl>

    Using Throw can affect the structure of what is returned by a function:

    >> NestList[#^2 + 1 &, 1, 7]
     = ...
    >> Catch[NestList[If[# > 1000, Throw[#], #^2 + 1] &, 1, 7]]
     = 458330

    X> Throw[1]
      = Null
    """

    messages = {
        "nocatch": "Uncaught `1` returned to top level.",
    }

    summary_text = "throw an expression to be caught by a surrounding 'Catch'"

    def eval1(self, value, evaluation):
        "Throw[value_]"
        raise WLThrowInterrupt(value)

    def eval_with_tag(self, value, tag, evaluation):
        "Throw[value_, tag_]"
        raise WLThrowInterrupt(value, tag)
