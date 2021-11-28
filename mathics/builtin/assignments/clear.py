# -*- coding: utf-8 -*-
"""
Clearing Assignments
"""


from mathics.builtin.base import (
    Builtin,
    PostfixOperator,
)
from mathics.core.expression import Expression
from mathics.core.symbols import (
    Symbol,
    system_symbols,
)

from mathics.core.systemsymbols import (
    SymbolFailed,
)

from mathics.core.atoms import String

from mathics.builtin.assignments.internals import is_protected


class Clear(Builtin):
    """
    <dl>
      <dt>'Clear[$symb1$, $symb2$, ...]'
      <dd>clears all values of the given symbols. The arguments can also be given as strings containing symbol names.
    </dl>

    >> x = 2;
    >> Clear[x]
    >> x
     = x

    >> x = 2;
    >> y = 3;
    >> Clear["Global`*"]
    >> x
     = x
    >> y
     = y

    'ClearAll' may not be called for 'Protected' symbols.
    >> Clear[Sin]
     : Symbol Sin is Protected.
    The values and rules associated with built-in symbols will not get lost when applying 'Clear'
    (after unprotecting them):
    >> Unprotect[Sin]
    >> Clear[Sin]
    >> Sin[Pi]
     = 0

    'Clear' does not remove attributes, messages, options, and default values associated with the symbols. Use 'ClearAll' to do so.
    >> Attributes[r] = {Flat, Orderless};
    >> Clear["r"]
    >> Attributes[r]
     = {Flat, Orderless}
    """

    allow_locked = True
    attributes = ("HoldAll",)
    messages = {
        "ssym": "`1` is not a symbol or a string.",
    }
    summary_text = "clear all values associated with the LHS or symbol"

    def do_clear(self, definition):
        definition.ownvalues = []
        definition.downvalues = []
        definition.subvalues = []
        definition.upvalues = []
        definition.formatvalues = {}
        definition.nvalues = []

    def apply(self, symbols, evaluation):
        "%(name)s[symbols___]"
        if isinstance(symbols, Symbol):
            symbols = [symbols]
        elif isinstance(symbols, Expression):
            symbols = symbols.get_leaves()
        elif isinstance(symbols, String):
            symbols = [symbols]
        else:
            symbols = symbols.get_sequence()

        for symbol in symbols:
            if isinstance(symbol, Symbol):
                names = [symbol.get_name()]
            else:
                pattern = symbol.get_string_value()
                if not pattern:
                    evaluation.message("Clear", "ssym", symbol)
                    continue
                if pattern[0] == "`":
                    pattern = evaluation.definitions.get_current_context() + pattern[1:]

                names = evaluation.definitions.get_matching_names(pattern)
            for name in names:
                attributes = evaluation.definitions.get_attributes(name)
                if is_protected(name, evaluation.definitions):
                    evaluation.message("Clear", "wrsym", Symbol(name))
                    continue
                if not self.allow_locked and "System`Locked" in attributes:
                    evaluation.message("Clear", "locked", Symbol(name))
                    continue
                definition = evaluation.definitions.get_user_definition(name)
                self.do_clear(definition)

        return Symbol("Null")

    def apply_all(self, evaluation):
        "Clear[System`All]"
        evaluation.definitions.set_user_definitions({})
        evaluation.definitions.clear_pymathics_modules()
        return


class ClearAll(Clear):
    """
    <dl>
      <dt>'ClearAll[$symb1$, $symb2$, ...]'
      <dd>clears all values, attributes, messages and options associated with the given symbols.
      The arguments can also be given as strings containing symbol names.
    </dl>

    >> x = 2;
    >> ClearAll[x]
    >> x
     = x
    >> Attributes[r] = {Flat, Orderless};
    >> ClearAll[r]
    >> Attributes[r]
     = {}

    'ClearAll' may not be called for 'Protected' or 'Locked' symbols.
    >> Attributes[lock] = {Locked};
    >> ClearAll[lock]
     : Symbol lock is locked.
    """

    allow_locked = False
    summary_text = "clear all values, definitions, messages and defaults for symbols"

    def do_clear(self, definition):
        super(ClearAll, self).do_clear(definition)
        definition.attributes = set()
        definition.messages = []
        definition.options = []
        definition.defaultvalues = []

    def apply_all(self, evaluation):
        "ClearAll[System`All]"
        evaluation.definitions.set_user_definitions({})
        evaluation.definitions.clear_pymathics_modules()
        return


class Unset(PostfixOperator):
    """
    <dl>
    <dt>'Unset[$x$]'
    <dt>'$x$=.'
        <dd>removes any value belonging to $x$.
    </dl>
    >> a = 2
     = 2
    >> a =.
    >> a
     = a

    Unsetting an already unset or never defined variable will not change anything:
    >> a =.
    >> b =.

    'Unset' can unset particular function values. It will print a message if no corresponding rule is found.
    >> f[x_] =.
     : Assignment on f for f[x_] not found.
     = $Failed
    >> f[x_] := x ^ 2
    >> f[3]
     = 9
    >> f[x_] =.
    >> f[3]
     = f[3]

    You can also unset 'OwnValues', 'DownValues', 'SubValues', and 'UpValues' directly. This is equivalent to setting them to '{}'.
    >> f[x_] = x; f[0] = 1;
    >> DownValues[f] =.
    >> f[2]
     = f[2]

    'Unset' threads over lists:
    >> a = b = 3;
    >> {a, {b}} =.
     = {Null, {Null}}

    #> x = 2;
    #> OwnValues[x] =.
    #> x
     = x
    #> f[a][b] = 3;
    #> SubValues[f] =.
    #> f[a][b]
     = f[a][b]
    #> PrimeQ[p] ^= True
     = True
    #> PrimeQ[p]
     = True
    #> UpValues[p] =.
    #> PrimeQ[p]
     = False

    #> a + b ^= 5;
    #> a =.
    #> a + b
     = 5
    #> {UpValues[a], UpValues[b]} =.
     = {Null, Null}
    #> a + b
     = a + b

    #> Unset[Messages[1]]
     : First argument in Messages[1] is not a symbol or a string naming a symbol.
     = $Failed
    """

    attributes = ("HoldFirst", "Listable", "ReadProtected")
    operator = "=."

    messages = {
        "norep": "Assignment on `2` for `1` not found.",
        "usraw": "Cannot unset raw object `1`.",
    }
    precedence = 670
    summary_text = "unset a value of the LHS"

    def apply(self, expr, evaluation):
        "Unset[expr_]"

        head = expr.get_head()
        if head in SYSTEM_SYMBOL_VALUES:
            if len(expr.leaves) != 1:
                evaluation.message_args(expr.get_head_name(), len(expr.leaves), 1)
                return SymbolFailed
            symbol = expr.leaves[0].get_name()
            if not symbol:
                evaluation.message(expr.get_head_name(), "fnsym", expr)
                return SymbolFailed
            if head is Symbol("System`Options"):
                empty = {}
            else:
                empty = []
            evaluation.definitions.set_values(symbol, expr.get_head_name(), empty)
            return Symbol("Null")
        name = expr.get_lookup_name()
        if not name:
            evaluation.message("Unset", "usraw", expr)
            return SymbolFailed
        if not evaluation.definitions.unset(name, expr):
            if not expr.is_atom():
                evaluation.message("Unset", "norep", expr, Symbol(name))
                return SymbolFailed
        return Symbol("Null")


SYSTEM_SYMBOL_VALUES = system_symbols(
    "OwnValues",
    "DownValues",
    "SubValues",
    "UpValues",
    "NValues",
    "Options",
    "Messages",
)
