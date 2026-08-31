"""
Setting Up Options for Functions
"""

from mathics.core.atoms import Integer1, String
from mathics.core.builtin import Builtin, get_option
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, ensure_context
from mathics.core.systemsymbols import SymbolRule
from mathics.eval.options.function import options_to_rules
from mathics.eval.options.options import eval_Option_with_names, eval_Options
from mathics.eval.patterns import Matcher


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
     = {x ⇾ 100}

    >> FilterRules[{x -> 100, y -> 1000, z -> 10000}, {a, b, x, z}]
     = {x ⇾ 100, z ⇾ 10000}
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


class Options(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/Options.html</url>

    <dl>
      <dt>'Options'[$symbol$]
      <dd>gives a list of optional arguments to $symbol$ and their \
        default values.
      <dt>'Options'[$symbol$, $name$]
      <dd>gives only the option value for $name$ in $symbol$.
    </dl>

    You can assign values to 'Options' to specify options.
    >> Options[f] = {n -> 2}
     = {n ⇾ 2}
    >> Options[f]
     = {n ⇾ 2}
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
     = a ⇾ b
    >> Options[f]
     = {a ⇾ b}
    Options can only be assigned to symbols:
    >> Options[a + b] = {a -> b}
     : Argument a + b at position 1 is expected to be a symbol.
     = {a ⇾ b}

    See also <url>
    :'OptionValue':
    /doc/reference-of-built-in-symbols/options-management/optionvalue/</url> and <url>
    :'OptionsPattern':
    /doc/reference-of-built-in-symbols/rules-and-patterns/composite-patterns/optionspattern/</url>.

    """

    # Set checking that the number of arguments required is one or two.
    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)
    summary_text = "the list of optional arguments and their default values"

    def eval(self, symbol, evaluation: Evaluation):
        "Options[symbol_]"
        if not isinstance(symbol, Symbol):
            # Docs say a string is allowed, but trying testing shows this is not true.
            return ListExpression()
        return eval_Options(symbol, evaluation)

    def eval_with_arg(self, symbol, name, evaluation: Evaluation):
        "Options[symbol_, name_]"
        if not isinstance(symbol, Symbol):
            # This is weird. We get a message like;
            #   *name* is not a known option for *symbol*
            # instead of a message about symbol not being a symbol.
            evaluation.message("Options", "optnf", name, symbol)
            return ListExpression()
        return eval_Option_with_names(symbol, name, evaluation)


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
     = {foo ⇾ 5, bar ⇾ 6}

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

    # Note: there is an optnf tag with a different message used in Option.
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


## FIXME add:
## AbsoluteOptions
## ArgumentOptions
