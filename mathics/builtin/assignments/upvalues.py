# -*- coding: utf-8 -*-


from mathics.builtin.base import BinaryOperator
from mathics.core.symbols import Symbol

from mathics.core.systemsymbols import SymbolFailed

from mathics.builtin.assignments.internals import _SetOperator


class UpSet(BinaryOperator, _SetOperator):
    """
    <dl>
      <dt>$f$[$x$] ^= $expression$
      <dd>evaluates $expression$ and assigns it to the value of $f$[$x$], associating the value with $x$.
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

    attributes = ("HoldFirst", "SequenceHold")
    grouping = "Right"
    operator = "^="
    precedence = 40

    summary_text = (
        "set value and associate the assignment with symbols that occur at level one"
    )

    def apply(self, lhs, rhs, evaluation):
        "lhs_ ^= rhs_"

        self.assign_elementary(lhs, rhs, evaluation, upset=True)
        return rhs


class UpSetDelayed(UpSet):
    """
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

    attributes = ("HoldAll", "SequenceHold")
    operator = "^:="
    summary_text = "set a delayed value and associate the assignment with symbols that occur at level one"

    def apply(self, lhs, rhs, evaluation):
        "lhs_ ^:= rhs_"

        if self.assign_elementary(lhs, rhs, evaluation, upset=True):
            return Symbol("Null")
        else:
            return SymbolFailed
