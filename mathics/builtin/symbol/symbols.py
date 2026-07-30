# -*- coding: utf-8 -*-
"""
Basic Symbol components
"""
import re

from mathics_scanner.tokeniser import is_symbol_name

from mathics.core.assignment import get_symbol_values
from mathics.core.atoms import Integer1, String
from mathics.core.attributes import A_HOLD_ALL, A_HOLD_FIRST, A_LOCKED, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.regex import to_regex
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import Symbol, strip_context
from mathics.eval.stackframe import get_eval_Expression


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


# In Mathematica 5, this appears under "Types of Values".
class FormatValues(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/tutorial/PatternsAndTransformationRules.html#6025</url>
    <dl>
      <dt>'FormatValues'[$symbol$]
      <dd>gives the list of format rules associated with $symbol$.
    </dl>

    First, use 'Format' to set a formatting rule for a form:

    >> Format[F[x_], OutputForm]:= Subscript[x, F]

    Now, to see the rules, we can use 'FormatValues':

    >> FormatValues[F]
     = {HoldPattern[Subscript[x_, F]] ⧴ Subscript[x, F]}

    The replacement pattern on the right in the delayed rule is formatted according to the top-level form. To see the rule input, we can use 'InputForm':
    >> FormatValues[F]  //InputForm
     = {HoldPattern[Format[F[x_], OutputForm]] :> Subscript[x, F]}
    """

    summary_text = (
        "give a list of formatting transformation rules associated with a symbol."
    )

    def eval(self, symbol, evaluation):
        """FormatValues[symbol_]"""
        return get_symbol_values(symbol, "FormatValues", "formatvalues", evaluation)


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
     = {HoldPattern[x] ⧴ 2}
    >> x := y
    >> OwnValues[x]
     = {HoldPattern[x] ⧴ y}
    >> y = 5;
    >> OwnValues[x]
     = {HoldPattern[x] ⧴ y}
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
    eval_error = Builtin.generic_argument_error
    expected_args = 1

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

    eval_error = Builtin.generic_argument_error
    expected_args = 1
    summary_text = "give the name of a symbol as a string"

    def eval(self, symbol, evaluation):
        "SymbolName[symbol_Symbol]"

        # MMA docs say "SymbolName always give the short name,
        # without any context"
        return String(strip_context(symbol.get_name()))
