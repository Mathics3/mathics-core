# -*- coding: utf-8 -*-
"""
Symbolic Handling

Symbolic data. Every symbol has a unique name, exists in a certain context or namespace, and can have a variety of type of values and attributes.
"""

import re

from mathics.builtin.assignments.internals import get_symbol_values
from mathics.builtin.base import (
    Builtin,
    PrefixOperator,
    Test,
)

from mathics.builtin.atomic.strings import to_regex

from mathics.core.atoms import (
    String,
)

from mathics.core.attributes import (
    attributes_bitset_to_list,
    hold_all,
    hold_first,
    locked,
    protected,
    read_protected,
    sequence_hold,
)

from mathics.core.expression import Expression
from mathics.core.convert.expression import to_mathics_list
from mathics.core.list import ListExpression
from mathics.core.rules import Rule

from mathics.core.symbols import (
    Symbol,
    SymbolHoldForm,
    SymbolFalse,
    SymbolNull,
    SymbolTrue,
    SymbolUpSet,
    strip_context,
)
from mathics.core.systemsymbols import (
    SymbolAttributes,
    SymbolDefinition,
    SymbolFormat,
    SymbolGrid,
    SymbolInfix,
    SymbolInputForm,
    SymbolOptions,
    SymbolRule,
    SymbolSet,
)


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
        if rulemsg.pattern.expr.elements[1].__str__() == '"usage"':
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


class Context(Builtin):
    r"""
    <dl>
      <dt>'Context[$symbol$]'
      <dd>yields the name of the context where $symbol$ is defined in.

      <dt>'Context[]'
      <dd>returns the value of '$Context'.
    </dl>

    >> Context[a]
     = Global`
    >> Context[b`c]
     = b`

    >> InputForm[Context[]]
     = "Global`"

    ## placeholder for general context-related tests
    #> x === Global`x
     = True
    #> `x === Global`x
     = True
    #> a`x === Global`x
     = False
    #> a`x === a`x
     = True
    #> a`x === b`x
     = False
    ## awkward parser cases
    #> FullForm[a`b_]
     = Pattern[a`b, Blank[]]
    """

    attributes = hold_first | protected

    rules = {"Context[]": "$Context"}

    summary_text = "give the name of the context of a symbol"

    def apply(self, symbol, evaluation):
        "Context[symbol_]"

        name = symbol.get_name()
        if not name:
            evaluation.message("Context", "normal")
            return
        assert "`" in name
        context = name[: name.rindex("`") + 1]
        return String(context)


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

    attributes = hold_all | protected
    precedence = 670
    summary_text = "give values of a symbol in a form that can be stored in a package"

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
                                SymbolHoldForm, SymbolDefinition
                            )
                        },
                        evaluation,
                    )
                )
                lines.append(
                    Expression(
                        SymbolHoldForm,
                        Expression(
                            SymbolUpSet if up else SymbolSet, lhs(rule.pattern.expr), r
                        ),
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
            attributes_list = attributes_bitset_to_list(attributes)
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolSet,
                        Expression(SymbolAttributes, symbol),
                        to_mathics_list(
                            *attributes_list, elements_conversion_fn=Symbol
                        ),
                    ),
                )
            )

        if definition is not None and not read_protected & attributes:
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
                        return Expression(SymbolFormat, expr, Symbol(format))

                    def rhs(expr):
                        if expr.has_form("Infix", None):
                            expr = Expression(
                                Expression(SymbolHoldForm, expr.head), *expr.elements
                            )
                        return Expression(SymbolInputForm, expr)

                    print_rule(rule, lhs=lhs, rhs=rhs)
        for rule in all.defaultvalues:
            print_rule(rule)
        if all.options:
            options = sorted(all.options.items())
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolSet,
                        Expression(SymbolOptions, symbol),
                        ListExpression(
                            *(
                                Expression(SymbolRule, Symbol(name), value)
                                for name, value in options
                            )
                        ),
                    ),
                )
            )
        if grid:
            if lines:
                return Expression(
                    SymbolGrid,
                    ListExpression(*(ListExpression(line) for line in lines)),
                    Expression(SymbolRule, Symbol("ColumnAlignments"), Symbol("Left")),
                )
            else:
                return SymbolNull
        else:
            for line in lines:
                evaluation.print_out(Expression(SymbolInputForm, line))
            return SymbolNull

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

    attributes = hold_all | protected
    summary_text = "give a list of transformation rules corresponding to all downvalues defined for a symbol"

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

    attributes = hold_all | sequence_hold | protected | read_protected
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
                    SymbolGrid,
                    ListExpression(*(to_mathics_list(line) for line in lines)),
                    Expression(SymbolRule, Symbol("ColumnAlignments"), Symbol("Left")),
                )
                evaluation.print_out(infoshow)
        else:
            for line in lines:
                evaluation.print_out(Expression(SymbolInputForm, line))
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
                                SymbolHoldForm, SymbolDefinition
                            )
                        }
                    )
                )
                lines.append(
                    Expression(
                        SymbolHoldForm,
                        Expression(
                            up and SymbolUpSet or SymbolSet, lhs(rule.pattern.expr), r
                        ),
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
            attributes_list = attributes_bitset_to_list(attributes)
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolSet,
                        Expression(SymbolAttributes, symbol),
                        ListExpression(
                            *(Symbol(attribute) for attribute in attributes_list)
                        ),
                    ),
                )
            )

        if definition is not None and not read_protected & attributes:
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
                        return Expression(SymbolFormat, expr, Symbol(format))

                    def rhs(expr):
                        if expr.has_formf(SymbolInfix, None):
                            expr = Expression(
                                Expression(SymbolHoldForm, expr.head), *expr.elements
                            )
                        return Expression(SymbolInputForm, expr)

                    print_rule(rule, lhs=lhs, rhs=rhs)
        for rule in all.defaultvalues:
            print_rule(rule)
        if all.options:
            options = sorted(all.options.items())
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolSet,
                        Expression(SymbolOptions, symbol),
                        ListExpression(
                            *(
                                Expression(SymbolRule, Symbol(name), value)
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


class Names(Builtin):
    """
    <dl>
      <dt>'Names["$pattern$"]'
      <dd>returns the list of names matching $pattern$.
    </dl>

    >> Names["List"]
     = {List}

    The wildcard '*' matches any character:
    >> Names["List*"]
     = {List, ListLinePlot, ListPlot, ListQ, Listable}

    The wildcard '@' matches only lowercase characters:
    >> Names["List@"]
     = {Listable}

    >> x = 5;
    >> Names["Global`*"]
     = {x}

    The number of built-in symbols:
    >> Length[Names["System`*"]]
     = ...

    #> Length[Names["System`*"]] > 350
     = True
    """

    summary_text = "find a list of symbols with names matching a pattern"

    def apply(self, pattern, evaluation):
        "Names[pattern_]"
        headname = pattern.get_head_name()
        if headname == "System`StringExpression":
            pattern = re.compile(to_regex(pattern, evaluation))
        else:
            pattern = pattern.get_string_value()

        if pattern is None:
            return

        names = set()
        for full_name in evaluation.definitions.get_matching_names(pattern):
            short_name = strip_context(full_name)
            names.add(short_name if short_name not in names else full_name)

        # TODO: Mathematica ignores contexts when it sorts the list of
        # names.
        return to_mathics_list(*sorted(names), elements_conversion_fn=String)


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

    attributes = hold_all | protected
    summary_text = "give the rule corresponding to any ownvalue defined for a symbol"

    def apply(self, symbol, evaluation):
        "OwnValues[symbol_]"

        return get_symbol_values(symbol, "OwnValues", "own", evaluation)


class Symbol_(Builtin):
    """
    <dl>
    <dt>'Symbol'
        <dd>is the head of symbols.
    </dl>

    >> Head[x]
     = Symbol
    You can use 'Symbol' to create symbols from strings:
    >> Symbol["x"] + Symbol["x"]
     = 2 x

    #> {\\[Eta], \\[CapitalGamma]\\[Beta], Z\\[Infinity], \\[Angle]XYZ, \\[FilledSquare]r, i\\[Ellipsis]j}
     = {\u03b7, \u0393\u03b2, Z\u221e, \u2220XYZ, \u25a0r, i\u2026j}
    """

    attributes = locked | protected

    messages = {
        "symname": (
            "The string `1` cannot be used for a symbol name. "
            "A symbol name must start with a letter "
            "followed by letters and numbers."
        ),
    }

    name = "Symbol"

    summary_text = "the head of a symbol; create a symbol from a name"

    def apply(self, string, evaluation):
        "Symbol[string_String]"

        from mathics.core.parser import is_symbol_name

        text = string.get_string_value()
        if is_symbol_name(text):
            return Symbol(evaluation.definitions.lookup_name(string.value))
        else:
            evaluation.message("Symbol", "symname", string)


class SymbolName(Builtin):
    """
    <dl>
    <dt>'SymbolName[$s$]'
        <dd>returns the name of the symbol $s$ (without any leading
        context name).
    </dl>

    >> SymbolName[x] // InputForm
     = "x"

    #> SymbolName[a`b`x] // InputForm
     = "x"
    """

    summary_text = "give the name of a symbol as a string"

    def apply(self, symbol, evaluation):
        "SymbolName[symbol_Symbol]"

        # MMA docs say "SymbolName always give the short name,
        # without any context"
        return String(strip_context(symbol.get_name()))


class SymbolQ(Test):
    """
    <dl>
    <dt>'SymbolQ[$x$]'
        <dd>is 'True' if $x$ is a symbol, or 'False' otherwise.
    </dl>

    >> SymbolQ[a]
     = True
    >> SymbolQ[1]
     = False
    >> SymbolQ[a + b]
     = False
    """

    summary_text = "test whether is a symbol"

    def test(self, expr):
        return isinstance(expr, Symbol)


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

    attributes = hold_all | protected
    summary_text = "give a list of transformation rules corresponding to upvalues defined for a symbol"

    def apply(self, symbol, evaluation):
        "UpValues[symbol_]"

        return get_symbol_values(symbol, "UpValues", "up", evaluation)


class ValueQ(Builtin):
    """
    <dl>
    <dt>'ValueQ[$expr$]'
        <dd>returns 'True' if and only if $expr$ is defined.
    </dl>

    >> ValueQ[x]
     = False
    >> x = 1;
    >> ValueQ[x]
     = True

    #> ValueQ[True]
     = False
    """

    attributes = hold_first | protected
    summary_text = "test whether a symbol can be considered to have a value"

    def apply(self, expr, evaluation):
        "ValueQ[expr_]"
        evaluated_expr = expr.evaluate(evaluation)
        if expr.sameQ(evaluated_expr):
            return SymbolFalse
        return SymbolTrue
