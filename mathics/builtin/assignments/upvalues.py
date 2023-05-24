# -*- coding: utf-8 -*-
"""
UpValue-related assignments

An <i>UpValue<i> is a definition associated with a symbols that does not appear directly its head.

See <url>
:Associating Definitions with Different Symbols:
https://reference.wolfram.com/language/tutorial/TransformationRulesAndDefinitions.html#6972</url>.
"""

from mathics.builtin.base import Builtin
from mathics.core.assignment import get_symbol_values
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED


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
