# -*- coding: utf-8 -*-
"""
Forms of Assignment
"""

from mathics.version import __version__  # noqa used in loading to check consistency.

from mathics.builtin.base import (
    Builtin,
    BinaryOperator,
    PostfixOperator,
    PrefixOperator,
)
from mathics.core.rules import Rule
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol

from mathics.core.systemsymbols import (
    SymbolFailed,
)

from mathics.core.definitions import PyMathicsLoadException

from mathics.builtin.assignments.internals import _SetOperator, get_symbol_values


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

    attributes = ("HoldFirst", "SequenceHold")
    grouping = "Right"

    messages = {
        "setraw": "Cannot assign to raw object `1`.",
        "shape": "Lists `1` and `2` are not the same shape.",
    }

    operator = "="
    precedence = 40

    messages = {
        "setraw": "Cannot assign to raw object `1`.",
        "shape": "Lists `1` and `2` are not the same shape.",
    }

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
    attributes = ("HoldAll", "SequenceHold")

    summary_text = "test a delayed value; used in defining functions"

    def apply(self, lhs, rhs, evaluation):
        "lhs_ := rhs_"

        if self.assign(lhs, rhs, evaluation):
            return Symbol("Null")
        else:
            return SymbolFailed


class TagSet(Builtin, _SetOperator):
    """
    <dl>
    <dt>'TagSet[$f$, $expr$, $value$]'
    <dt>'$f$ /: $expr$ = $value$'
        <dd>assigns $value$ to $expr$, associating the corresponding
        rule with the symbol $f$.
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

    The symbol $f$ must appear as the ultimate head of $lhs$ or as the head of a leaf in $lhs$:
    >> x /: f[g[x]] = 3;
     : Tag x not found or too deep for an assigned rule.
    >> g /: f[g[x]] = 3;
    >> f[g[x]]
     = 3
    """

    attributes = ("HoldAll", "SequenceHold")

    messages = {
        "tagnfd": "Tag `1` not found or too deep for an assigned rule.",
    }

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

    attributes = ("HoldAll", "SequenceHold")

    def apply(self, f, lhs, rhs, evaluation):
        "f_ /: lhs_ := rhs_"

        name = f.get_name()
        if not name:
            evaluation.message(self.get_name(), "sym", f, 1)
            return

        if self.assign_elementary(lhs, rhs, evaluation, tags=[name]):
            return Symbol("Null")
        else:
            return SymbolFailed


class Definition(Builtin):
    """
    <dl>
    <dt>'Definition[$symbol$]'
        <dd>prints as the user-defined values and rules associated with $symbol$.
    </dl>

    'Definition' does not print information for 'ReadProtected' symbols.
    'Definition' uses 'InputForm' to format values.

    >> a = 2;
    >> Definition[a]
     = a = 2

    >> f[x_] := x ^ 2
    >> g[f] ^:= 2
    >> Definition[f]
     = f[x_] = x ^ 2
     .
     . g[f] ^= 2

    Definition of a rather evolved (though meaningless) symbol:
    >> Attributes[r] := {Orderless}
    >> Format[r[args___]] := Infix[{args}, "~"]
    >> N[r] := 3.5
    >> Default[r, 1] := 2
    >> r::msg := "My message"
    >> Options[r] := {Opt -> 3}
    >> r[arg_., OptionsPattern[r]] := {arg, OptionValue[Opt]}

    Some usage:
    >> r[z, x, y]
     = x ~ y ~ z
    >> N[r]
     = 3.5
    >> r[]
     = {2, 3}
    >> r[5, Opt->7]
     = {5, 7}

    Its definition:
    >> Definition[r]
     = Attributes[r] = {Orderless}
     .
     . arg_. ~ OptionsPattern[r] = {arg, OptionValue[Opt]}
     .
     . N[r, MachinePrecision] = 3.5
     .
     . Format[args___, MathMLForm] = Infix[{args}, "~"]
     .
     . Format[args___, OutputForm] = Infix[{args}, "~"]
     .
     . Format[args___, StandardForm] = Infix[{args}, "~"]
     .
     . Format[args___, TeXForm] = Infix[{args}, "~"]
     .
     . Format[args___, TraditionalForm] = Infix[{args}, "~"]
     .
     . Default[r, 1] = 2
     .
     . Options[r] = {Opt -> 3}

    For 'ReadProtected' symbols, 'Definition' just prints attributes, default values and options:
    >> SetAttributes[r, ReadProtected]
    >> Definition[r]
     = Attributes[r] = {Orderless, ReadProtected}
     .
     . Default[r, 1] = 2
     .
     . Options[r] = {Opt -> 3}
    This is the same for built-in symbols:
    >> Definition[Plus]
     = Attributes[Plus] = {Flat, Listable, NumericFunction, OneIdentity, Orderless, Protected}
     .
     . Default[Plus] = 0
    >> Definition[Level]
     = Attributes[Level] = {Protected}
     .
     . Options[Level] = {Heads -> False}

    'ReadProtected' can be removed, unless the symbol is locked:
    >> ClearAttributes[r, ReadProtected]
    'Clear' clears values:
    >> Clear[r]
    >> Definition[r]
     = Attributes[r] = {Orderless}
     .
     . Default[r, 1] = 2
     .
     . Options[r] = {Opt -> 3}
    'ClearAll' clears everything:
    >> ClearAll[r]
    >> Definition[r]
     = Null

    If a symbol is not defined at all, 'Null' is printed:
    >> Definition[x]
     = Null
    """

    attributes = ("HoldAll",)
    precedence = 670

    def format_definition(self, symbol, evaluation, grid=True):
        "StandardForm,TraditionalForm,OutputForm: Definition[symbol_]"

        lines = []

        def print_rule(rule, up=False, lhs=lambda k: k, rhs=lambda r: r):
            evaluation.check_stopped()
            if isinstance(rule, Rule):
                r = rhs(
                    rule.replace.replace_vars(
                        {
                            "System`Definition": Expression(
                                "HoldForm", Symbol("Definition")
                            )
                        },
                        evaluation,
                    )
                )
                lines.append(
                    Expression(
                        "HoldForm",
                        Expression(up and "UpSet" or "Set", lhs(rule.pattern.expr), r),
                    )
                )

        name = symbol.get_name()
        if not name:
            evaluation.message("Definition", "sym", symbol, 1)
            return
        attributes = evaluation.definitions.get_attributes(name)
        definition = evaluation.definitions.get_user_definition(name, create=False)
        all = evaluation.definitions.get_definition(name)
        if attributes:
            attributes = list(attributes)
            attributes.sort()
            lines.append(
                Expression(
                    "HoldForm",
                    Expression(
                        "Set",
                        Expression("Attributes", symbol),
                        Expression(
                            "List", *(Symbol(attribute) for attribute in attributes)
                        ),
                    ),
                )
            )

        if definition is not None and "System`ReadProtected" not in attributes:
            for rule in definition.ownvalues:
                print_rule(rule)
            for rule in definition.downvalues:
                print_rule(rule)
            for rule in definition.subvalues:
                print_rule(rule)
            for rule in definition.upvalues:
                print_rule(rule, up=True)
            for rule in definition.nvalues:
                print_rule(rule)
            formats = sorted(definition.formatvalues.items())
            for format, rules in formats:
                for rule in rules:

                    def lhs(expr):
                        return Expression("Format", expr, Symbol(format))

                    def rhs(expr):
                        if expr.has_form("Infix", None):
                            expr = Expression(
                                Expression("HoldForm", expr.head), *expr.leaves
                            )
                        return Expression("InputForm", expr)

                    print_rule(rule, lhs=lhs, rhs=rhs)
        for rule in all.defaultvalues:
            print_rule(rule)
        if all.options:
            options = sorted(all.options.items())
            lines.append(
                Expression(
                    "HoldForm",
                    Expression(
                        "Set",
                        Expression("Options", symbol),
                        Expression(
                            "List",
                            *(
                                Expression("Rule", Symbol(name), value)
                                for name, value in options
                            )
                        ),
                    ),
                )
            )
        if grid:
            if lines:
                return Expression(
                    "Grid",
                    Expression("List", *(Expression("List", line) for line in lines)),
                    Expression("Rule", Symbol("ColumnAlignments"), Symbol("Left")),
                )
            else:
                return Symbol("Null")
        else:
            for line in lines:
                evaluation.print_out(Expression("InputForm", line))
            return Symbol("Null")

    def format_definition_input(self, symbol, evaluation):
        "InputForm: Definition[symbol_]"
        return self.format_definition(symbol, evaluation, grid=False)


class SubValues(Builtin):
    """
    <dl>
    <dt>'SubValues[$symbol$]'
        <dd>gives the list of subvalues associated with $symbol$.
    </dl>

    >> f[1][x_] := x
    >> f[2][x_] := x ^ 2
    >> SubValues[f]
     = {HoldPattern[f[2][x_]] :> x ^ 2, HoldPattern[f[1][x_]] :> x}
    >> Definition[f]
     = f[2][x_] = x ^ 2
     .
     . f[1][x_] = x
    """

    attributes = ("HoldAll",)

    def apply(self, symbol, evaluation):
        "SubValues[symbol_]"

        return get_symbol_values(symbol, "SubValues", "sub", evaluation)


class Messages(Builtin):
    """
    <dl>
    <dt>'Messages[$symbol$]'
        <dd>gives the list of messages associated with $symbol$.
    </dl>

    >> a::b = "foo"
     = foo
    >> Messages[a]
     = {HoldPattern[a::b] :> foo}
    >> Messages[a] = {a::c :> "bar"};
    >> a::c // InputForm
     = "bar"
    >> Message[a::c]
     : bar
    """

    attributes = ("HoldAll",)

    def apply(self, symbol, evaluation):
        "Messages[symbol_]"

        return get_symbol_values(symbol, "Messages", "messages", evaluation)


class DefaultValues(Builtin):
    """
    <dl>
    <dt>'DefaultValues[$symbol$]'
        <dd>gives the list of default values associated with $symbol$.
    </dl>

    >> Default[f, 1] = 4
     = 4
    >> DefaultValues[f]
     = {HoldPattern[Default[f, 1]] :> 4}

    You can assign values to 'DefaultValues':
    >> DefaultValues[g] = {Default[g] -> 3};
    >> Default[g, 1]
     = 3
    >> g[x_.] := {x}
    >> g[a]
     = {a}
    >> g[]
     = {3}
    """

    attributes = ("HoldAll",)

    def apply(self, symbol, evaluation):
        "DefaultValues[symbol_]"

        return get_symbol_values(symbol, "System`DefaultValues", "default", evaluation)


class AddTo(BinaryOperator):
    """
    <dl>
    <dt>'AddTo[$x$, $dx$]'</dt>
    <dt>'$x$ += $dx$'</dt>
        <dd>is equivalent to '$x$ = $x$ + $dx$'.
    </dl>

    >> a = 10;
    >> a += 2
     = 12
    >> a
     = 12
    """

    operator = "+="
    precedence = 100
    attributes = ("HoldFirst",)
    grouping = "Right"

    rules = {
        "x_ += dx_": "x = x + dx",
    }


class SubtractFrom(BinaryOperator):
    """
    <dl>
    <dt>'SubtractFrom[$x$, $dx$]'</dt>
    <dt>'$x$ -= $dx$'</dt>
        <dd>is equivalent to '$x$ = $x$ - $dx$'.
    </dl>

    >> a = 10;
    >> a -= 2
     = 8
    >> a
     = 8
    """

    operator = "-="
    precedence = 100
    attributes = ("HoldFirst",)
    grouping = "Right"

    rules = {
        "x_ -= dx_": "x = x - dx",
    }


class TimesBy(BinaryOperator):
    """
    <dl>
    <dt>'TimesBy[$x$, $dx$]'</dt>
    <dt>'$x$ *= $dx$'</dt>
        <dd>is equivalent to '$x$ = $x$ * $dx$'.
    </dl>

    >> a = 10;
    >> a *= 2
     = 20
    >> a
     = 20
    """

    operator = "*="
    precedence = 100
    attributes = ("HoldFirst",)
    grouping = "Right"

    rules = {
        "x_ *= dx_": "x = x * dx",
    }


class DivideBy(BinaryOperator):
    """
    <dl>
    <dt>'DivideBy[$x$, $dx$]'</dt>
    <dt>'$x$ /= $dx$'</dt>
        <dd>is equivalent to '$x$ = $x$ / $dx$'.
    </dl>

    >> a = 10;
    >> a /= 2
     = 5
    >> a
     = 5
    """

    operator = "/="
    precedence = 100
    attributes = ("HoldFirst",)
    grouping = "Right"

    rules = {
        "x_ /= dx_": "x = x / dx",
    }


class Increment(PostfixOperator):
    """
    <dl>
    <dt>'Increment[$x$]'</dt>
    <dt>'$x$++'</dt>
        <dd>increments $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 2;
    >> a++
     = 2
    >> a
     = 3
    Grouping of 'Increment', 'PreIncrement' and 'Plus':
    >> ++++a+++++2//Hold//FullForm
     = Hold[Plus[PreIncrement[PreIncrement[Increment[Increment[a]]]], 2]]
    """

    operator = "++"
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

    rules = {
        "x_++": (
            "Module[{Internal`IncrementTemporary = x},"
            "       x = x + 1;"
            "       Internal`IncrementTemporary"
            "]"
        ),
    }


class PreIncrement(PrefixOperator):
    """
    <dl>
    <dt>'PreIncrement[$x$]'</dt>
    <dt>'++$x$'</dt>
        <dd>increments $x$ by 1, returning the new value of $x$.
    </dl>

    '++$a$' is equivalent to '$a$ = $a$ + 1':
    >> a = 2;
    >> ++a
     = 3
    >> a
     = 3
    """

    operator = "++"
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

    rules = {
        "++x_": "x = x + 1",
    }


class Decrement(PostfixOperator):
    """
    <dl>
    <dt>'Decrement[$x$]'</dt>
    <dt>'$x$--'</dt>
        <dd>decrements $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 5;
    X> a--
     = 5
    X> a
     = 4
    """

    operator = "--"
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

    rules = {
        "x_--": "Module[{t=x}, x = x - 1; t]",
    }


class PreDecrement(PrefixOperator):
    """
    <dl>
    <dt>'PreDecrement[$x$]'</dt>
    <dt>'--$x$'</dt>
        <dd>decrements $x$ by 1, returning the new value of $x$.
    </dl>

    '--$a$' is equivalent to '$a$ = $a$ - 1':
    >> a = 2;
    >> --a
     = 1
    >> a
     = 1
    """

    operator = "--"
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

    rules = {
        "--x_": "x = x - 1",
    }


class LoadModule(Builtin):
    """
    <dl>
    <dt>'LoadModule[$module$]'</dt>
    <dd>'Load Mathics definitions from the python module $module$</dd>
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

    def apply(self, module, evaluation):
        "LoadModule[module_String]"
        try:
            evaluation.definitions.load_pymathics_module(module.value)
        except PyMathicsLoadException:
            evaluation.message(self.name, "notmathicslib", module)
            return SymbolFailed
        except ImportError:
            evaluation.message(self.get_name(), "notfound", module)
            return SymbolFailed
        else:
            # Add Pymathics` to $ContextPath so that when user don't
            # have to qualify Pymathics variables and functions,
            # as the those in the module just loaded.
            # Following the example of $ContextPath in the WL
            # reference manual where PackletManager appears first in
            # the list, it seems to be preferable to add this PyMathics
            # at the beginning.
            context_path = evaluation.definitions.get_context_path()
            if "Pymathics`" not in context_path:
                context_path.insert(0, "Pymathics`")
                evaluation.definitions.set_context_path(context_path)
        return module
