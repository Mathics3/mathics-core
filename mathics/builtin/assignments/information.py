# -*- coding: utf-8 -*-
"""
Information about Assignments
"""

from mathics.version import __version__  # noqa used in loading to check consistency.

from mathics.builtin.base import Builtin, PrefixOperator

from mathics.core.rules import Rule
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolNull

from mathics.core.atoms import String

from mathics.builtin.assignments.internals import get_symbol_values


def _get_usage_string(symbol, evaluation, is_long_form: bool, htmlout=False):
    """
    Returns a python string with the documentation associated to a given symbol.
    """
    definition = evaluation.definitions.get_definition(symbol.name)
    ruleusage = definition.get_values_list("messages")
    usagetext = None
    import re

    # First look at user definitions:
    for rulemsg in ruleusage:
        if rulemsg.pattern.expr.leaves[1].__str__() == '"usage"':
            usagetext = rulemsg.replace.value
    if usagetext is not None:
        # Maybe, if htmltout is True, we should convert
        # the value to a HTML form...
        return usagetext
    # Otherwise, look at the pymathics, and builtin docstrings:
    builtins = evaluation.definitions.builtin
    pymathics = evaluation.definitions.pymathics
    bio = pymathics.get(definition.name)
    if bio is None:
        bio = builtins.get(definition.name)

    if bio is not None:
        if not is_long_form and hasattr(bio.builtin.__class__, "summary_text"):
            return bio.builtin.__class__.summary_text
        from mathics.doc.common_doc import XMLDoc

        docstr = bio.builtin.__class__.__doc__
        title = bio.builtin.__class__.__name__
        if docstr is None:
            return None
        if htmlout:
            usagetext = XMLDoc(docstr, title).html()
        else:
            usagetext = XMLDoc(docstr, title).text(0)
        usagetext = re.sub(r"\$([0-9a-zA-Z]*)\$", r"\1", usagetext)
        return usagetext
    return None


# This could go under Symbol Handling when we get a module for that.
# It is not strictly in Assignment Information, but on the other hand, this
# is a reasonable place for it.
class Definition(Builtin):
    """
    <dl>
      <dt>'Definition[$symbol$]'
      <dd>prints as the definitions given for $symbol$.
      This is in a form that can e stored in a package.
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
    summary_text = "gives values of a symbol in a form that can be stored in a package"

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


# In Mathematica 5, this appears under "Types of Values".
class DownValues(Builtin):
    """
    <dl>
    <dt>'DownValues[$symbol$]'
        <dd>gives the list of downvalues associated with $symbol$.
    </dl>

    'DownValues' uses 'HoldPattern' and 'RuleDelayed' to protect the
    downvalues from being evaluated. Moreover, it has attribute
    'HoldAll' to get the specified symbol instead of its value.

    >> f[x_] := x ^ 2
    >> DownValues[f]
     = {HoldPattern[f[x_]] :> x ^ 2}

    Mathics will sort the rules you assign to a symbol according to
    their specificity. If it cannot decide which rule is more special,
    the newer one will get higher precedence.
    >> f[x_Integer] := 2
    >> f[x_Real] := 3
    >> DownValues[f]
     = {HoldPattern[f[x_Real]] :> 3, HoldPattern[f[x_Integer]] :> 2, HoldPattern[f[x_]] :> x ^ 2}
    >> f[3]
     = 2
    >> f[3.]
     = 3
    >> f[a]
     = a ^ 2

    The default order of patterns can be computed using 'Sort' with
    'PatternsOrderedQ':
    >> Sort[{x_, x_Integer}, PatternsOrderedQ]
     = {x_Integer, x_}

    By assigning values to 'DownValues', you can override the default
    ordering:
    >> DownValues[g] := {g[x_] :> x ^ 2, g[x_Integer] :> x}
    >> g[2]
     = 4

    Fibonacci numbers:
    >> DownValues[fib] := {fib[0] -> 0, fib[1] -> 1, fib[n_] :> fib[n - 1] + fib[n - 2]}
    >> fib[5]
     = 5
    """

    attributes = ("HoldAll",)
    summary_text = "gives a list of transformation rules corresponding to all downvalues defined for a symbol"

    def apply(self, symbol, evaluation):
        "DownValues[symbol_]"

        return get_symbol_values(symbol, "DownValues", "down", evaluation)


class Information(PrefixOperator):
    """
    <dl>
      <dt>'Information[$symbol$]'
      <dd>Prints information about a $symbol$
    </dl>
    'Information' does not print information for 'ReadProtected' symbols.
    'Information' uses 'InputForm' to format values.

    #> a = 2;
    #> Information[a]
     | a = 2
     .
     = Null

    #> f[x_] := x ^ 2;
    #> g[f] ^:= 2;
    #> f::usage = "f[x] returns the square of x";
    #> Information[f]
     | f[x] returns the square of x
     .
     . f[x_] = x ^ 2
     .
     . g[f] ^= 2
     .
     = Null

    """

    attributes = ("HoldAll", "SequenceHold", "Protect", "ReadProtect")
    messages = {"notfound": "Expression `1` is not a symbol"}
    operator = "??"
    options = {
        "LongForm": "True",
    }
    precedence = 0
    summary_text = "get information about all assignments for a symbol"

    def format_definition(self, symbol, evaluation, options, grid=True):
        "StandardForm,TraditionalForm,OutputForm: Information[symbol_, OptionsPattern[Information]]"
        ret = SymbolNull
        lines = []
        if isinstance(symbol, String):
            evaluation.print_out(symbol)
            return ret
        if not isinstance(symbol, Symbol):
            evaluation.message("Information", "notfound", symbol)
            return ret
        # Print the "usage" message if available.
        is_long_form = self.get_option(options, "LongForm", evaluation).to_python()
        usagetext = _get_usage_string(symbol, evaluation, is_long_form)
        if usagetext is not None:
            lines.append(usagetext)

        if is_long_form:
            self.show_definitions(symbol, evaluation, lines)

        if grid:
            if lines:
                infoshow = Expression(
                    "Grid",
                    Expression("List", *(Expression("List", line) for line in lines)),
                    Expression("Rule", Symbol("ColumnAlignments"), Symbol("Left")),
                )
                evaluation.print_out(infoshow)
        else:
            for line in lines:
                evaluation.print_out(Expression("InputForm", line))
        return ret

        # It would be deserable to call here the routine inside Definition, but for some reason it fails...
        # Instead, I just copy the code from Definition

    def show_definitions(self, symbol, evaluation, lines):
        def print_rule(rule, up=False, lhs=lambda k: k, rhs=lambda r: r):
            evaluation.check_stopped()
            if isinstance(rule, Rule):
                r = rhs(
                    rule.replace.replace_vars(
                        {
                            "System`Definition": Expression(
                                "HoldForm", Symbol("Definition")
                            )
                        }
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
        return

    def format_definition_input(self, symbol, evaluation, options):
        "InputForm: Information[symbol_, OptionsPattern[Information]]"
        self.format_definition(symbol, evaluation, options, grid=False)
        ret = SymbolNull
        return ret


# In Mathematica 5, this appears under "Types of Values".
class OwnValues(Builtin):
    """
    <dl>
      <dt>'OwnValues[$symbol$]'
      <dd>gives the list of ownvalue associated with $symbol$.
    </dl>

    >> x = 3;
    >> x = 2;
    >> OwnValues[x]
     = {HoldPattern[x] :> 2}
    >> x := y
    >> OwnValues[x]
     = {HoldPattern[x] :> y}
    >> y = 5;
    >> OwnValues[x]
     = {HoldPattern[x] :> y}
    >> Hold[x] /. OwnValues[x]
     = Hold[y]
    >> Hold[x] /. OwnValues[x] // ReleaseHold
     = 5
    """

    attributes = ("HoldAll",)
    summary_text = "gives the rule corresponding to any ownvalue defined for a symbol"

    def apply(self, symbol, evaluation):
        "OwnValues[symbol_]"

        return get_symbol_values(symbol, "OwnValues", "own", evaluation)


# In Mathematica 5, this appears under "Types of Values".
class UpValues(Builtin):
    """
    <dl>
      <dt>'UpValues[$symbol$]'
      <dd>gives the list of transformation rules corresponding to upvalues define with $symbol$.
    </dl>

    >> a + b ^= 2
     = 2
    >> UpValues[a]
     = {HoldPattern[a + b] :> 2}
    >> UpValues[b]
     = {HoldPattern[a + b] :> 2}

    You can assign values to 'UpValues':
    >> UpValues[pi] := {Sin[pi] :> 0}
    >> Sin[pi]
     = 0
    """

    attributes = ("HoldAll",)
    summary_text = "gives list of transformation rules corresponding to upvalues defined for a symbol"

    def apply(self, symbol, evaluation):
        "UpValues[symbol_]"

        return get_symbol_values(symbol, "UpValues", "up", evaluation)
