# -*- coding: utf-8 -*-
"""
UpValue-related assignments

An <i>UpValue<i> is a definition associated with a symbols that does not appear directly its head.

See <url>
:Associating Definitions with Different Symbols:
https://reference.wolfram.com/language/tutorial/TransformationRulesAndDefinitions.html#6972</url>.
"""

from mathics.builtin.assignments.assignment import _SetOperator
from mathics.builtin.base import BinaryOperator, Builtin
from mathics.core.assignment import get_symbol_values
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_HOLD_FIRST,
    A_PROTECTED,
    A_SEQUENCE_HOLD,
)
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed


class UpSet(BinaryOperator, _SetOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/UpSet.html</url>

    <dl>
      <dt>$f$[$x$] ^= $expression$
      <dd>evaluates $expression$ and assigns it to the value of $f$[$x$], \
         associating the value with $x$.
    </dl>

    'UpSet' creates an upvalue:
    >> a[b] ^= 3;
    >> DownValues[a]
     = {}
    >> UpValues[b]
     = {HoldPattern[a[b]] :> 3}

    >> a ^= 3
     : Nonatomic expression expected.
     = 3

    You can use 'UpSet' to specify special values like format values.
    However, these values will not be saved in 'UpValues':
    >> Format[r] ^= "custom";
    >> r
     = custom
    >> UpValues[r]
     = {}

    #> f[g, a + b, h] ^= 2
     : Tag Plus in f[g, a + b, h] is Protected.
     = 2
    #> UpValues[h]
     = {HoldPattern[f[g, a + b, h]] :> 2}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_SEQUENCE_HOLD
    grouping = "Right"
    operator = "^="
    precedence = 40

    summary_text = (
        "set value and associate the assignment with symbols that occur at level one"
    )

    def apply(self, lhs, rhs, evaluation):
        "lhs_ ^= rhs_"

        self.assign(lhs, rhs, evaluation, upset=True)
        return rhs


class UpSetDelayed(UpSet):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/UpSetDelayed.html</url>

    <dl>
       <dt>'UpSetDelayed[$expression$, $value$]'

       <dt>'$expression$ ^:= $value$'
       <dd>assigns $expression$ to the value of $f$[$x$] (without evaluating $expression$), associating the value with $x$.
    </dl>

    >> a[b] ^:= x
    >> x = 2;
    >> a[b]
     = 2
    >> UpValues[b]
     = {HoldPattern[a[b]] :> x}

    #> f[g, a + b, h] ^:= 2
     : Tag Plus in f[g, a + b, h] is Protected.
    #> f[a+b] ^:= 2
     : Tag Plus in f[a + b] is Protected.
     = $Failed
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_SEQUENCE_HOLD
    operator = "^:="
    summary_text = "set a delayed value and associate the assignment with symbols that occur at level one"

    def eval(self, lhs, rhs, evaluation):
        "lhs_ ^:= rhs_"

        if self.assign(lhs, rhs, evaluation, upset=True):
            return SymbolNull
        else:
            return SymbolFailed


# In Mathematica 5, this appears under "Types of Values".
class UpValues(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/UpValues.html</url>
    <dl>
      <dt>'UpValues[$symbol$]'
      <dd>gives the list of transformation rules corresponding to upvalues \
          define with $symbol$.
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

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "give a list of transformation rules corresponding to upvalues defined for a symbol"

    def eval(self, symbol, evaluation):
        "UpValues[symbol_]"

        return get_symbol_values(symbol, "UpValues", "up", evaluation)
