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


class NValues(Builtin):
    """
    <dl>
       <dt>'NValues[$symbol$]'
       <dd>gives the list of numerical values associated with $symbol$.

       <i>Note: this function is in Mathematica 5 but has been removed from current Mathematica.</i>
    </dl>

    >> NValues[a]
     = {}
    >> N[a] = 3;
    >> NValues[a]
     = {HoldPattern[N[a, MachinePrecision]] :> 3}

    You can assign values to 'NValues':
    >> NValues[b] := {N[b, MachinePrecision] :> 2}
    >> N[b]
     = 2.
    Be sure to use 'SetDelayed', otherwise the left-hand side of the transformation rule will be evaluated immediately,
    causing the head of 'N' to get lost. Furthermore, you have to include the precision in the rules; 'MachinePrecision'
    will not be inserted automatically:
    >> NValues[c] := {N[c] :> 3}
    >> N[c]
     = c

    Mathics will gracefully assign any list of rules to 'NValues'; however, inappropriate rules will never be used:
    >> NValues[d] = {foo -> bar};
    >> NValues[d]
     = {HoldPattern[foo] :> bar}
    >> N[d]
     = d
    """

    attributes = ("HoldAll",)
    summary_text = "gives the list of numerical values associated with a symbol"

    def apply(self, symbol, evaluation):
        "NValues[symbol_]"

        return get_symbol_values(symbol, "NValues", "n", evaluation)


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
