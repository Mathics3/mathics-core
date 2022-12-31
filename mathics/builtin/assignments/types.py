# -*- coding: utf-8 -*-
# This module follows Mathematica 5
# conventions. In current Mathematica a number of these functiions
# don't exist.  Some of the functions in Mathematica 5 appear now
# under Information.

# FIXME: put this inside a Pymathics module.
# We alos should have compatibility modes for for earlier Mathemathica versions.
"""
Types of Values
"""


from mathics.builtin.base import Builtin
from mathics.core.assignment import get_symbol_values
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED


class DefaultValues(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DefaultValues.html</url>

    <dl>
      <dt>'DefaultValues[$symbol$]'
      <dd>gives the list of default values associated with $symbol$.

      <i>Note: this function is in Mathematica 5 but has been removed from \
      current Mathematica.</i>
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

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = (
        "give default values for the arguments associated with a function symbol"
    )

    def eval(self, symbol, evaluation):
        "DefaultValues[symbol_]"

        return get_symbol_values(symbol, "System`DefaultValues", "default", evaluation)


class Messages(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Messages.html</url>

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

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give the list the messages associated with a particular symbol"

    def eval(self, symbol, evaluation):
        "Messages[symbol_]"

        return get_symbol_values(symbol, "Messages", "messages", evaluation)


class NValues(Builtin):
    """
    ## No longer in WMA
    ## <url>:WMA link:https://reference.wolfram.com/language/ref/NValues.html</url>

    <dl>
       <dt>'NValues[$symbol$]'
       <dd>gives the list of numerical values associated with $symbol$.

       <i>Note: this function is in Mathematica 5 but has been removed from \
          current Mathematica.</i>
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
    Be sure to use 'SetDelayed', otherwise the left-hand side of the \
    transformation rule will be evaluated immediately, \
    causing the head of 'N' to get lost. Furthermore, you have to \
    include the precision in the rules; 'MachinePrecision' \
    will not be inserted automatically:
    >> NValues[c] := {N[c] :> 3}
    >> N[c]
     = c

    Mathics will assign any list of rules to 'NValues'; however, \
    inappropriate rules will never be used:
    >> NValues[d] = {foo -> bar};
    >> NValues[d]
     = {HoldPattern[foo] :> bar}
    >> N[d]
     = d
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give the list of numerical values associated with a symbol"

    def eval(self, symbol, evaluation):
        "NValues[symbol_]"

        return get_symbol_values(symbol, "NValues", "n", evaluation)


class SubValues(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/SubValues.html</url>

    <dl>
      <dt>'SubValues[$symbol$]'
      <dd>gives the list of subvalues associated with $symbol$.

      <i>Note: this function is not in current Mathematica.</i>
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

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give the list of subvalues associated with a symbol"

    def eval(self, symbol, evaluation):
        "SubValues[symbol_]"

        return get_symbol_values(symbol, "SubValues", "sub", evaluation)
