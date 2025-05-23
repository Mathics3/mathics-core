# -*- coding: utf-8 -*-

"""
Options Management

A number of functions have various options which control the behavior or \
the default behavior that function. Default options can be queried or set.

<url>
:WMA link:
https://reference.wolfram.com/language/guide/OptionsManagement.html</url>
"""

from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer1, String
from mathics.core.builtin import Builtin, Predefined, Test, get_option
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList, ensure_context, strip_context
from mathics.core.systemsymbols import SymbolDefault, SymbolRule, SymbolRuleDelayed
from mathics.eval.patterns import Matcher, get_default_value


class All(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/All.html</url>

    <dl>
      <dt>'All'
      <dd>is an option value for a number of functions indicating to include everything.
    </dl>


    In list functions, it indicates all levels of the list.

    For example, in <url>
    :Part:
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/part</url>, \
    'All', extracts into a first column vector the first element of each of the \
    list elements:

    >> {{1, 3}, {5, 7}}[[All, 1]]
     = {1, 5}

    While in <url>
    :Take:
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/part</url>, \
    'All' extracts as a column matrix the first element as a list for each of the list \
    elements:

    >> Take[{{1, 3}, {5, 7}}, All, {1}]
     = {{1}, {5}}

    In <url>
    :Plot:
    /doc/reference-of-built-in-symbols/graphics-and-drawing/plotting-data/plot</url>, \
    setting the <url>
    :Mesh:
/doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values/mesh</url> \
    option to 'All' will show the specific plot points:

    >> Plot[x^2, {x, -1, 1}, MaxRecursion->5, Mesh->All]
     = -Graphics-

    """

    summary_text = "option value that specify using everything"


class Default(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/Default.html</url>

    <dl>
      <dt>'Default'[$f$]
      <dd>gives the default value for an omitted parameter of $f$.

      <dt>'Default'[$f$, $k$]
      <dd>gives the default value for a parameter on the $k$-th position.

      <dt>'Default'[$f$, $k$, $n$]
      <dd>gives the default value for the $k$-th parameter out of $n$.
    </dl>

    Assign values to 'Default' to specify default values.

    >> Default[f] = 1
     = 1
    >> f[x_.] := x ^ 2
    >> f[]
     = 1

    Default values are stored in 'DefaultValues':
    >> DefaultValues[f]
     = {HoldPattern[Default[f]] :> 1}

    You can use patterns for $k$ and $n$:
    >> Default[h, k_, n_] := {k, n}
    Note that the position of a parameter is relative to the pattern, not the matching expression:
    >> h[] /. h[___, ___, x_., y_., ___] -> {x, y}
     = {{3, 5}, {4, 5}}
    """

    summary_text = "predefined default arguments for a function"

    def eval(self, f, i, evaluation):
        "Default[f_, i___]"

        i = i.get_sequence()
        if len(i) > 2:
            evaluation.message(SymbolDefault, "argb", 1 + len(i), 1, 3)
            return
        i = [index.get_int_value() for index in i]
        for index in i:
            if index is None or index < 1:
                evaluation.message(SymbolDefault.name, "intp")
                return
        name = f.get_name()
        if not name:
            evaluation.message(SymbolDefault.name, "sym", f, 1)
            return
        result = get_default_value(name, evaluation, *i)
        return result


class FilterRules(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/FilterRules.html</url>

    <dl>
      <dt>'FilterRules'[$rules$, $pattern$]
      <dd>gives those $rules$ that have a left side that matches $pattern$.

      <dt>'FilterRules'[$rules$, {$pattern_1$, $pattern_2$, ...}]
      <dd>gives those $rules$ that have a left side that match at least one of $pattern_1$, $pattern_2$, ...
    </dl>

    >> FilterRules[{x -> 100, y -> 1000}, x]
     = {x -> 100}

    >> FilterRules[{x -> 100, y -> 1000, z -> 10000}, {a, b, x, z}]
     = {x -> 100, z -> 10000}
    """

    rules = {
        "FilterRules[rules_List, patterns_List]": "FilterRules[rules, Alternatives @@ patterns]",
    }
    summary_text = (
        "select rules such that the pattern matches some other given patterns"
    )

    def eval(self, rules, pattern, evaluation):
        "FilterRules[rules_List, pattern_]"

        match = Matcher(pattern, evaluation).match

        def matched():
            for rule in rules.elements:
                if rule.has_form("Rule", 2) and match(rule.elements[0], evaluation):
                    yield rule

        return ListExpression(*list(matched()))


class None_(Predefined):
    """
        <url>:WMA link:https://reference.wolfram.com/language/ref/None.html</url>

        <dl>
          <dt>'None'
          <dd>is a setting value for many options.
        </dl>

        Plot3D shows the mesh grid between computed points by default. This the <url>
        :Mesh:
/doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values/mesh</url> \

        However, you hide the mesh by setting the 'Mesh' option value to 'None':

        >> Plot3D[{x^2 + y^2, -x^2 - y^2}, {x, -2, 2}, {y, -2, 2}, BoxRatios-> Automatic, Mesh->None]
         = -Graphics3D-
    """

    name = "None"
    summary_text = "option value that disables the option"


# Has this been removed from WL? I cannot find a WMA link.
class NotOptionQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NotOptionQ.html</url>

    <dl>
      <dt>'NotOptionQ'[$expr$]
      <dd>returns 'True' if $expr$ does not have the form of a valid \
          option specification.
    </dl>

    >> NotOptionQ[x]
     = True
    >> NotOptionQ[2]
     = True
    >> NotOptionQ["abc"]
     = True

    >> NotOptionQ[a -> True]
     = False
    """

    summary_text = "test whether an expression does not match the form of a valid option specification"

    def test(self, expr) -> bool:
        if hasattr(expr, "flatten_with_respect_to_head"):
            expr = expr.flatten_with_respect_to_head(SymbolList)
        if not expr.has_form("List", None):
            expr = [expr]
        else:
            expr = expr.elements
        return not all(
            e.has_form("Rule", None) or e.has_form("RuleDelayed", 2) for e in expr
        )


# Has this been removed from WL? I cannot find a WMA link.
class OptionQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OptionQ.html</url>

    <dl>
      <dt>'OptionQ'[$expr$]
      <dd>returns 'True' if $expr$ has the form of a valid option \
         specification.
    </dl>

    Examples of option specifications:
    >> OptionQ[a -> True]
     = True
    >> OptionQ[a :> True]
     = True
    >> OptionQ[{a -> True}]
     = True
    >> OptionQ[{a :> True}]
     = True

    Options lists are flattened when are applied, so
    >> OptionQ[{a -> True, {b->1, "c"->2}}]
     = True
    >> OptionQ[{a -> True, {b->1, c}}]
     = False
    >> OptionQ[{a -> True, F[b->1,c->2]}]
     = False

    'OptionQ' returns 'False' if its argument is not a valid option
    specification:
    >> OptionQ[x]
     = False
    """

    summary_text = (
        "test whether an expression matches the form of a valid option specification"
    )

    def test(self, expr) -> bool:
        if hasattr(expr, "flatten_with_respect_to_head"):
            expr = expr.flatten_with_respect_to_head(SymbolList)
        if not expr.has_form("List", None):
            expr = [expr]
        else:
            expr = expr.elements
        return all(
            e.has_form("Rule", None) or e.has_form("RuleDelayed", 2) for e in expr
        )


class Options(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/Options.html</url>

    <dl>
      <dt>'Options'[$f$]
      <dd>gives a list of optional arguments to $f$ and their \
        default values.
    </dl>

    You can assign values to 'Options' to specify options.
    >> Options[f] = {n -> 2}
     = {n -> 2}
    >> Options[f]
     = {n :> 2}
    >> f[x_, OptionsPattern[f]] := x ^ OptionValue[n]
    >> f[x]
     = x ^ 2
    >> f[x, n -> 3]
     = x ^ 3

    Delayed option rules are evaluated just when the corresponding 'OptionValue' is called:
    >> f[a :> Print["value"]] /. f[OptionsPattern[{}]] :> (OptionValue[a]; Print["between"]; OptionValue[a]);
     | value
     | between
     | value
    In contrast to that, normal option rules are evaluated immediately:
    >> f[a -> Print["value"]] /. f[OptionsPattern[{}]] :> (OptionValue[a]; Print["between"]; OptionValue[a]);
     | value
     | between

    Options must be rules or delayed rules:
    >> Options[f] = {a}
     : {a} is not a valid list of option rules.
     = {a}
    A single rule need not be given inside a list:
    >> Options[f] = a -> b
     = a -> b
    >> Options[f]
     = {a :> b}
    Options can only be assigned to symbols:
    >> Options[a + b] = {a -> b}
     : Argument a + b at position 1 is expected to be a symbol.
     = {a -> b}

    See also <url>
    :'OptionValue':
    /doc/reference-of-built-in-symbols/options-management/optionsvalue/</url> and <url>
    :'OptionsPattern':
    /doc/reference-of-built-in-symbols/rules-and-patterns/composite-patterns/optionspattern/</url>.

    """

    summary_text = "the list of optional arguments and their default values"

    def eval(self, f, evaluation):
        "Options[f_]"

        name = f.get_name()
        if not name:
            if isinstance(f, Image):
                # FIXME ColorSpace, MetaInformation
                options = f.metadata
            else:
                evaluation.message("Options", "sym", f, Integer1)
                return
        else:
            options = evaluation.definitions.get_options(name)
        result = []
        for option, value in sorted(options.items(), key=lambda item: item[0]):
            # Don't use HoldPattern, since the returned List should be
            # assignable to Options again!
            result.append(Expression(SymbolRuleDelayed, Symbol(option), value))
        return ListExpression(*result)


class OptionValue(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OptionValue.html</url>

    <dl>
      <dt>'OptionValue'[$name$]
      <dd>gives the value of the option $name$ matched by 'OptionsPattern'.

      <dt>'OptionValue'[$f$, $name$]
      <dd>recover the value of the option $name$ associated with the head $f$.

      <dt>'OptionValue'[$f$, $opts$, $name$]
      <dd>recover the value of the option $name$ associated with the symbol $f$, extracting the values from $optvals$ if available.

      <dt>'OptionValue'[..., $list$]
      <dd>recover the value of the options in $list$ .
    </dl>

    First, set up a symbol with some options using 'Options':
    >> Options[MySetting] = {"foo" -> 5, "bar" -> 6}
     = {foo -> 5, bar -> 6}

    Now get a value previously set:

    >> OptionValue[MySetting, "bar"]
     = 6

    If the option does exist we get a message:
    >> OptionValue[MySetting, "baz"]
     : Option name baz not found in defaults for MySetting.
     = baz

    Use 'OptionValue' to get the value of option 'a' inside 'OptionsPattern' 'a->3'
    >> f[a->3] /. f[OptionsPattern[{}]] -> {OptionValue[a]}
     = {3}

    An unavailable option returns argument and does not generate a message:
    >> f[a->3] /. f[OptionsPattern[{}]] -> {OptionValue[b]}
     = {b}

    The argument of 'OptionValue' must be a symbol:
    >> f[a->3] /. f[OptionsPattern[{}]] -> {OptionValue[a+b]}
     : Argument a + b at position 1 is expected to be a symbol.
     = {OptionValue[a + b]}

    However, the symbol can be evaluated dynamically:
    >> f[a->5] /. f[OptionsPattern[{}]] -> {OptionValue[Symbol["a"]]}
     = {5}


    #> Clear[MySetting]

    See also <url>
    :'Options':
    /doc/reference-of-built-in-symbols/options-management/options/</url> and <url>
    :'OptionsPattern':
    /doc/reference-of-built-in-symbols/rules-and-patterns/composite-patterns/optionspattern/</url>.
    """

    messages = {
        "optnf": "Option name `1` not found in defaults for `2`.",
    }

    rules = {
        "OptionValue[optnames_List]": "OptionValue/@optnames",
        "OptionValue[f_, optnames_List]": "OptionValue[f,#1]&/@optnames",
        "OptionValue[f_, opts_, optnames_List]": "OptionValue[f,opts, #1]&/@optnames",
    }
    summary_text = "retrieve values of options while executing a function"

    def eval(self, optname, evaluation):
        "OptionValue[optname_]"
        if evaluation.options is None:
            return

        if type(optname) is String:
            name = optname.to_python()[1:-1]
        else:
            name = optname.get_name()

        name = optname.get_name()
        if not name:
            name = optname.get_string_value()
            if name:
                name = ensure_context(name)
        if not name:
            evaluation.message("OptionValue", "sym", optname, Integer1)
            return

        val = get_option(evaluation.options, name, evaluation)
        if val is None:
            return Symbol(name)
        return val

    def eval_with_f(self, f, optname, evaluation):
        "OptionValue[f_, optname_]"
        return self.eval_with_f_and_opts(f, None, optname, evaluation)

    def eval_with_f_and_opts(self, f, opts, optname, evaluation):
        "OptionValue[f_, opts_, optname_]"
        if type(optname) is String:
            name = optname.to_python()[1:-1]
        else:
            name = optname.get_name()

        if not name:
            name = optname.get_string_value()
            if name:
                name = ensure_context(name)
        if not name:
            evaluation.message("OptionValue", "sym", optname, 1)
            return
        # Look first in the explicit list
        if opts:
            if (options_values := opts.get_option_values(evaluation)) is None:
                evaluation.message("OptionValue", "optnf", optname, f)
                return
            val = get_option(options_values, name, evaluation)
        else:
            val = None
        # then, if not found, look at f. It could be a symbol, or a list of symbols, rules, and list of rules...
        if val is None:
            if isinstance(f, Symbol):
                val = get_option(
                    evaluation.definitions.get_options(f.get_name()), name, evaluation
                )
            else:
                if f.get_head_name() in ("System`Rule", "System`RuleDelayed"):
                    f = ListExpression(f)
                if f.get_head_name() == "System`List":
                    for element in f.elements:
                        if isinstance(element, Symbol):
                            val = get_option(
                                evaluation.definitions.get_options(element.get_name()),
                                name,
                                evaluation,
                            )
                            if val:
                                break
                        else:
                            values = element.get_option_values(evaluation)
                            if values:
                                val = get_option(values, name, evaluation)
                                if val:
                                    break

        if val is None and evaluation.options:
            val = get_option(evaluation.options, name, evaluation)
        if val is None:
            evaluation.message("OptionValue", "optnf", optname, f)
            return Symbol(name)
        return val


class SetOptions(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/SetOptions.html</url>

    <dl>
      <dt>'SetOptions'[$s$, name1 -> value1, name2 -> value2, ...]
      <dd>sets the specified default options for a symbol $s$. \
      The entire set of options for $s$ is returned.
    </dl>

    One way to find the default options for a symbol is to use \
    'SetOptions' passing no association pairs:

    >> SetOptions[Plot]
     = ...
    """

    summary_text = "set up default option values for a function"

    def eval(self, symbol: Symbol, options: Expression, evaluation: Evaluation):
        "SetOptions[symbol_Symbol, options___]"

        # Get the existing options for parameter ``symbol``.
        options_dict = evaluation.definitions.get_options(symbol.name)

        # Update symbol's options for each of the options passed
        # in ``_options``.
        if not hasattr(options, "elements"):
            evaluation.message("SetOptions", "rep", options)
            return None

        # For a single association, ``options`` is Symbol, replacement
        # For multiple associations, ``options`` is a list of Rules.
        options_pairs = iter(options.elements)
        for element in options_pairs:
            if isinstance(element, Symbol):
                option_symbol = element
                option_value = next(options_pairs)
            elif hasattr(element, "head") and element.head is SymbolRule:
                option_symbol, option_value = element.elements
            else:
                evaluation.message("SetOptions", "rep", element)
                return None
            options_dict[option_symbol.name] = option_value

        # Create and return a List with all of the options including
        # the new updated ones.
        options_list = options_to_rules(options_dict)
        return ListExpression(*options_list)


def options_to_rules(options, filter=None):
    items = sorted(options.items())
    if filter:
        items = [
            (name, value)
            for name, value in items
            if strip_context(name) in filter.keys()
        ]
    return [Expression(SymbolRule, Symbol(name), value) for name, value in items]
