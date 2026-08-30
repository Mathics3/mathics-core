"""
Individual Options
"""

from mathics.core.atoms import Integer1, String
from mathics.core.builtin import Builtin, Predefined, Test, get_option
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList, ensure_context


class Automatic(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Automatic.html</url>

    <dl>
      <dt>'Automatic'
      <dd>is used to specify an automatically computed option value.
    </dl>

    'Automatic' is the default for 'PlotRange', 'ImageSize', and other
    graphical options:

    >> Cases[Options[Plot], HoldPattern[_ -> Automatic]]
     = {AxesOrigin ⇾ Automatic, Background ⇾ Automatic, BaselinePosition ⇾ Automatic, ContentSelectable ⇾ Automatic, CoordinatesToolOptions ⇾ Automatic, Exclusions ⇾ Automatic, FrameTicks ⇾ Automatic, ImageSize ⇾ Automatic, Method ⇾ Automatic, PlotRange ⇾ Automatic, PlotRangePadding ⇾ Automatic, PlotRegion ⇾ Automatic, PreserveImageOptions ⇾ Automatic, Ticks ⇾ Automatic}
    """

    summary_text = "option value to choose parameters automatically"


class None_(Predefined):
    """
        <url>:WMA link:https://reference.wolfram.com/language/ref/None.html</url>

        <dl>
          <dt>'None'
          <dd>is a setting value for many options.
        </dl>

        Plot3D shows the mesh grid between computed points by default. This the <url>
        :Mesh:
/doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/drawing-options-and-option-values/mesh</url> \

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
