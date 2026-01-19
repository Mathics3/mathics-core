# -*- coding: utf-8 -*-
"""
Symbol Handling

Symbolic data. Every symbol has a unique name, exists in a certain context \
or namespace, and can have a variety of type of values and attributes.
"""
import re
from typing import Callable, List, Optional

from mathics_scanner.tokeniser import is_symbol_name

from mathics.core.assignment import get_symbol_values
from mathics.core.atoms import Integer1, String
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_HOLD_FIRST,
    A_LOCKED,
    A_PROTECTED,
    A_READ_PROTECTED,
    A_SEQUENCE_HOLD,
    attributes_bitset_to_list,
)
from mathics.core.builtin import Builtin, PrefixOperator, Test
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.regex import to_regex
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Rule
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolHoldForm,
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
    SymbolInputForm,
    SymbolLeft,
    SymbolOptions,
    SymbolRule,
    SymbolSet,
)
from mathics.doc.online import online_doc_string
from mathics.eval.stackframe import get_eval_Expression

SymbolMissing = Symbol("System`Missing")
SymbolUnknownSymbol = Symbol("System`UnknownSymbol")


def gather_and_format_definition_rules(
    symbol: Symbol, evaluation: Evaluation
) -> Optional[List[Expression]]:
    """Return a list of lines describing the definition of `symbol`"""
    lines = []

    def format_rule(
        rule: Rule,
        up: bool = False,
        lhs: Callable = lambda k: k,
        rhs: Callable = lambda r: r,
    ):
        """
        Add a line showing `rule`
        """
        evaluation.check_stopped()
        if isinstance(rule, Rule):
            r = rhs(
                rule.replace.replace_vars(
                    {"System`Definition": Expression(SymbolHoldForm, SymbolDefinition)}
                )
            )
            r = Expression(SymbolInputForm, r)
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(
                        up and SymbolUpSet or SymbolSet, lhs(rule.pattern.expr), r
                    ),
                )
            )

    def gather_rules(definition: Definition):
        """
        Add to the description all the rules associated
        to a definition object
        """
        for rule in definition.ownvalues:
            format_rule(rule)
        for rule in definition.downvalues:
            format_rule(rule)
        for rule in definition.subvalues:
            format_rule(rule)
        for rule in definition.upvalues:
            format_rule(rule, up=True)
        for rule in definition.nvalues:
            format_rule(rule)
        formats = sorted(definition.formatvalues.items())
        for format, rules in formats:
            for rule in rules:

                def lhs(expr):
                    return Expression(
                        SymbolInputForm, Expression(SymbolFormat, expr, Symbol(format))
                    )

                def rhs(expr):
                    if expr.has_form("Infix", None):
                        expr = Expression(
                            Expression(SymbolHoldForm, expr.head), *expr.elements
                        )
                    return Expression(SymbolInputForm, expr)

                format_rule(rule, lhs=lhs, rhs=rhs)

    name = symbol.get_name()
    if not name:
        evaluation.message("Definition", "sym", symbol, 1)
        return

    try:
        all = evaluation.definitions.get_definition(name)
        attributes = all.attributes
        all_options = all.options
        all_defaultvalues = all.defaultvalues

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
    except KeyError:
        attributes = 0
        all_options = {}
        all_defaultvalues = []

    if not A_READ_PROTECTED & attributes:
        try:
            gather_rules(evaluation.definitions.get_user_definition(name, create=False))
        except KeyError:
            pass

    for rule in all_defaultvalues:
        format_rule(rule)
    if all_options:
        options = sorted(all_options.items())
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
    return lines


class Context(Builtin):
    r"""
    <url>:WMA link:
       https://reference.wolfram.com/language/ref/Context.html</url>
    <dl>
      <dt>'Context'[$symbol$]
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
    """

    attributes = A_HOLD_FIRST | A_PROTECTED

    rules = {"Context[]": "$Context"}

    summary_text = "give the name of the context of a symbol"

    def eval(self, symbol, evaluation):
        "Context[symbol_]"

        name = symbol.get_name()
        if not name:
            evaluation.message("Context", "normal", Integer1, get_eval_Expression())
            return
        assert "`" in name
        context = name[: name.rindex("`") + 1]
        return String(context)


class Definition(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Definition.html</url>
    <dl>
      <dt>'Definition'[$symbol$]
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
     = f[x_] = x^2
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
     . Format[r[args___], MathMLForm] = Infix[{args}, "~"]
     .
     . Format[r[args___], OutputForm] = Infix[{args}, "~"]
     .
     . Format[r[args___], StandardForm] = Infix[{args}, "~"]
     .
     . Format[r[args___], TeXForm] = Infix[{args}, "~"]
     .
     . Format[r[args___], TraditionalForm] = Infix[{args}, "~"]
     .
     . Default[r, 1] = 2
     .
     .Options[r] = {Opt -> 3}
     .

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

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give values of a symbol in a form that can be stored in a package"

    def format_definition(
        self, symbol: Symbol, evaluation: Evaluation, grid: bool = True
    ) -> Symbol:
        "(StandardForm,TraditionalForm,OutputForm,): Definition[symbol_]"

        lines = gather_and_format_definition_rules(symbol, evaluation)
        if lines:
            if grid:
                return Expression(
                    SymbolGrid,
                    ListExpression(*(ListExpression(line) for line in lines)),
                    Expression(SymbolRule, Symbol("ColumnAlignments"), SymbolLeft),
                )
            else:
                for line in lines:
                    evaluation.print_out(Expression(SymbolInputForm, line))

        return SymbolNull

    def format_definition_input(self, symbol: Symbol, evaluation: Evaluation) -> Symbol:
        "(InputForm,): Definition[symbol_]"
        return self.format_definition(symbol, evaluation, grid=False)


# In Mathematica 5, this appears under "Types of Values".
class DownValues(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/DownValues.html</url>
    <dl>
      <dt>'DownValues'[$symbol$]
      <dd>gives the list of downvalues associated with $symbol$.
    </dl>

    'DownValues' uses 'HoldPattern' and 'RuleDelayed' to protect the \
    downvalues from being evaluated, and it has attribute \
    'HoldAll' to get the specified symbol instead of its value.

    >> f[x_] := x ^ 2
    >> DownValues[f]
     = {HoldPattern[f[x_]] :> x ^ 2}

    Mathics will sort the rules you assign to a symbol according to \
    their specificity. If it cannot decide which rule is more special, \
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

    The default order of patterns can be computed using 'Sort' with \
    'PatternsOrderedQ':
    >> Sort[{x_, x_Integer}, PatternsOrderedQ]
     = {x_Integer, x_}

    By assigning values to 'DownValues', you can override the default \
    ordering:
    >> DownValues[g] := {g[x_] :> x ^ 2, g[x_Integer] :> x}
    >> g[2]
     = 4

    Fibonacci numbers:
    >> DownValues[fib] := {fib[0] -> 0, fib[1] -> 1, fib[n_] :> fib[n - 1] + fib[n - 2]}
    >> fib[5]
     = 5
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give a list of transformation rules corresponding to all downvalues defined for a symbol"

    def eval(self, symbol, evaluation):
        "DownValues[symbol_]"

        return get_symbol_values(symbol, "DownValues", "downvalues", evaluation)


# In Mathematica 5, this appears under "Types of Values".
class FormatValues(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/tutorial/PatternsAndTransformationRules.html#6025</url>
    <dl>
      <dt>'FormatValues'[$symbol$]
      <dd>gives the list of formatvalues associated with $symbol$.
    </dl>

    >> Format[F[x_], OutputForm]:= Subscript[x, F]
    >> FormatValues[F]
     = {HoldPattern[Format[Subscript[x_, F], OutputForm]] :> Subscript[x, F]}
    """

    summary_text = (
        "give a list of formatting transformation rules associated with a symbol."
    )

    def eval(self, symbol, evaluation):
        """FormatValues[symbol_]"""
        return get_symbol_values(symbol, "FormatValues", "formatvalues", evaluation)


class Information(PrefixOperator):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Information.html</url>
    <dl>
      <dt>'Information'[$symbol$]
      <dd>Prints information about a $symbol$
    </dl>

    'Information' does not print information for 'ReadProtected' symbols.

    'Information' uses 'InputForm' to format values.
    """

    attributes = A_HOLD_ALL | A_SEQUENCE_HOLD | A_PROTECTED | A_READ_PROTECTED
    messages = {"notfound": "Expression `1` is not a symbol"}
    options = {
        "LongForm": "True",
    }
    summary_text = "get information about all assignments for a symbol"

    def build_missing(self, expression: BaseElement) -> Expression:
        """Evaluate ?? F[x][y].. as -> Missing[UnknownSymbol, F][x][y]"""
        if isinstance(expression, Expression):
            return Expression(self.build_missing(expression.head), *expression.elements)
        return Expression(SymbolMissing, SymbolUnknownSymbol, expression)

    def build_list_of_matching_symbols(
        self, symbol_pat: str, evaluation: Evaluation, options: dict, grid: bool = True
    ):
        """Return a list of symbols compatible with symbol_pat"""
        definitions = evaluation.definitions
        names = definitions.get_matching_names(symbol_pat)
        rows = []
        curr_row = []
        for name in names:
            curr_row.append(String(definitions.shorten_name(name)))
            if len(curr_row) == 3:
                rows.append(ListExpression(*curr_row))
                curr_row = []
        if curr_row:
            curr_row = curr_row + (3 - len(curr_row)) * [String("")]
            rows.append(ListExpression(*curr_row))

        # TODO: Format using Grid?
        result = Expression(Symbol("System`TableForm"), ListExpression(*rows))
        return result

    # This implementation mixes the current behavior of WMA >=12.0 with the old behavior
    # (WMA 4.0).
    # TODO: the formatting part of this must be moved to `InformationData`
    # and `Information` should build this kind of expressions.

    def format_information_generic(
        self,
        expr: BaseElement,
        evaluation: Evaluation,
        options: dict,
        grid: bool = True,
    ) -> Symbol:
        "(StandardForm,TraditionalForm,InputForm,OutputForm,): Information[expr_, OptionsPattern[Information]]"
        evaluation.message("Information", "notfound", expr)
        return self.build_missing(expr)

    def format_information_string(
        self, strpat: String, evaluation: Evaluation, options: dict, grid: bool = True
    ) -> Symbol:
        "(StandardForm,TraditionalForm,InputForm,OutputForm,): Information[strpat_String, OptionsPattern[Information]]"
        definitions = evaluation.definitions
        string_str = strpat.value

        if "*" in string_str:
            return self.build_list_of_matching_symbols(
                string_str, evaluation, options, grid
            )
        return self.eval_information_symbol(
            Symbol(definitions.lookup_name(string_str)), evaluation, options
        )

    def format_information_symbol(
        self, symbol: Symbol, evaluation: Evaluation, options: dict, grid: bool = True
    ) -> Symbol:
        "(StandardForm,TraditionalForm,InputForm,OutputForm,): Information[symbol_Symbol, OptionsPattern[Information]]"
        definitions = evaluation.definitions
        try:
            definitions.get_definition(symbol.name, True)
        except KeyError:
            return self.build_missing(symbol)

        lines = []
        # Print the "usage" message if available.
        # is_long_form = self.get_option(options, "LongForm", evaluation).to_python()
        is_long_form = True  # In WMA >=12.0 this option does not make much difference--
        usagetext = online_doc_string(symbol, evaluation, is_long_form)
        if usagetext:
            lines.append(usagetext)
        else:
            lines.append(symbol.get_name())

        if is_long_form:
            lines.extend(gather_and_format_definition_rules(symbol, evaluation))

        infoshow = Expression(
            SymbolGrid,
            ListExpression(*(to_mathics_list(line) for line in lines)),
            Expression(SymbolRule, Symbol("ColumnAlignments"), SymbolLeft),
        )
        return infoshow


class Names(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Names.html</url>
    <dl>
      <dt>'Names'["$pattern$"]
      <dd>returns the list of names matching $pattern$.
    </dl>

    >> Names["List"]
     = {List}

    The wildcard '*' matches any character:
    >> Names["List*"]
     = {List, ListLinePlot, ListLogPlot, ListPlot, ListQ, ListStepPlot, Listable}

    The wildcard '@' matches only lowercase characters:
    >> Names["List@"]
     = {Listable}

    >> x = 5;
    >> Names["Global`*"]
     = {x}

    The number of built-in symbols:
    >> Length[Names["System`*"]]
     = ...
    """

    summary_text = "find a list of symbols with names matching a pattern"

    def eval(self, pattern, evaluation: Evaluation):
        "Names[pattern_]"
        headname = pattern.get_head_name()
        if headname == "System`StringExpression":
            pattern = re.compile(to_regex(pattern, show_message=evaluation.message))
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
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/OwnValues.html</url>
    <dl>
      <dt>'OwnValues'[$symbol$]
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

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give the rule corresponding to any ownvalue defined for a symbol"

    def eval(self, symbol, evaluation):
        "OwnValues[symbol_]"

        return get_symbol_values(symbol, "OwnValues", "ownvalues", evaluation)


class Symbol_(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Symbol.html</url>
    <dl>
      <dt>'Symbol'
      <dd>is the head of symbols.
    </dl>

    >> Head[x]
     = Symbol
    You can use 'Symbol' to create symbols from strings:
    >> Symbol["x"] + Symbol["x"]
     = 2 x
    """

    attributes = A_LOCKED | A_PROTECTED

    messages = {
        "symname": (
            "The string `1` cannot be used for a symbol name. "
            "A symbol name must start with a letter "
            "followed by letters and numbers."
        ),
    }

    name = "Symbol"

    summary_text = "the head of a symbol; create a symbol from a name"

    def eval(self, string, evaluation):
        "Symbol[string_String]"

        text = string.value
        if is_symbol_name(text):
            return Symbol(evaluation.definitions.lookup_name(string.value))
        else:
            evaluation.message("Symbol", "symname", string)


class SymbolName(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/SymbolName.html</url>
    <dl>
      <dt>'SymbolName'[$s$]
      <dd>returns the name of the symbol $s$ (without any leading \
        context name).
    </dl>

    >> SymbolName[x] // InputForm
     = "x"
    """

    summary_text = "give the name of a symbol as a string"

    def eval(self, symbol, evaluation):
        "SymbolName[symbol_Symbol]"

        # MMA docs say "SymbolName always give the short name,
        # without any context"
        return String(strip_context(symbol.get_name()))


class SymbolQ(Test):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/SymbolName.html</url>
    <dl>
      <dt>'SymbolQ'[$x$]
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

    def test(self, expr) -> bool:
        return isinstance(expr, Symbol)


class ValueQ(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/ValueQ.html</url>
    <dl>
      <dt>'ValueQ'[$expr$]
      <dd>returns 'True' if and only if $expr$ is defined.
    </dl>

    >> ValueQ[x]
     = False
    >> x = 1;
    >> ValueQ[x]
     = True
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    summary_text = "test whether a symbol can be considered to have a value"

    def eval(self, expr, evaluation):
        "ValueQ[expr_]"
        evaluated_expr = expr.evaluate(evaluation)
        if expr.sameQ(evaluated_expr):
            return SymbolFalse
        return SymbolTrue
