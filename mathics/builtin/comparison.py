# -*- coding: utf-8 -*-
"""
Testing Expressions

There are a number of functions for testing Expressions.

Functions that "ask a question" have names that end in "Q". They return 'True' for an explicit answer, and 'False' otherwise.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.testing-expressions"

from typing import Optional, Any

import sympy


from mathics.builtin.base import (
    BinaryOperator,
    Builtin,
    SympyFunction,
)

from mathics.builtin.numbers.constants import mp_convert_constant

from mathics.core.atoms import (
    COMPARE_PREC,
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    Number,
    String,
)
from mathics.core.attributes import (
    flat,
    listable,
    numeric_function,
    one_identity,
    orderless,
    protected,
)
from mathics.core.convert.expression import to_expression
from mathics.core.evaluators import eval_N
from mathics.core.expression import Expression
from mathics.core.number import dps
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolList, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolComplexInfinity,
    SymbolDirectedInfinity,
    SymbolInequality,
    SymbolInfinity,
    SymbolMaxPrecision,
    SymbolSign,
)


operators = {
    "System`Less": (-1,),
    "System`LessEqual": (-1, 0),
    "System`Equal": (0,),
    "System`GreaterEqual": (0, 1),
    "System`Greater": (1,),
    "System`Unequal": (-1, 1),
}

SymbolExactNumberQ = Symbol("ExactNumberQ")
SymbolMaxExtraPrecision = Symbol("$MaxExtraPrecision")


class _InequalityOperator(BinaryOperator):
    precedence = 290
    grouping = "NonAssociative"

    @staticmethod
    def numerify_args(items, evaluation) -> list:
        items_sequence = items.get_sequence()
        all_numeric = all(
            item.is_numeric(evaluation) and item.get_precision() is None
            for item in items_sequence
        )

        # All expressions are numeric but exact and they are not all numbers,
        if all_numeric and any(not isinstance(item, Number) for item in items_sequence):
            # so apply N and compare them.
            items = items_sequence
            n_items = []
            for item in items:
                if not isinstance(item, Number):
                    # TODO: use $MaxExtraPrecision insterad of hard-coded 50
                    item = eval_N(item, evaluation, SymbolMaxPrecision)
                n_items.append(item)
            items = n_items
        else:
            items = items.numerify(evaluation).get_sequence()
        return items


class _EqualityOperator(_InequalityOperator):
    "Compares all pairs e.g. a == b == c compares a == b, b == c, and a == c."

    @staticmethod
    def get_pairs(args):
        for i in range(len(args)):
            for j in range(i):
                yield (args[i], args[j])

    def expr_equal(self, lhs, rhs, max_extra_prec=None) -> Optional[bool]:
        if isinstance(rhs, Expression):
            lhs, rhs = rhs, lhs
        if not isinstance(lhs, Expression):
            return
        same_heads = lhs.get_head().sameQ(rhs.get_head())
        if not same_heads:
            return None
        if len(lhs.elements) != len(rhs.elements):
            return
        for l, r in zip(lhs.elements, rhs.elements):
            tst = self.equal2(l, r, max_extra_prec)
            # If the there are a pair of corresponding elements
            # that are not equals, then we are not able to decide
            # about the equality.
            if not tst:
                return None
        return True

    def infty_equal(self, lhs, rhs, max_extra_prec=None) -> Optional[bool]:
        if rhs.get_head().sameQ(SymbolDirectedInfinity):
            lhs, rhs = rhs, lhs
        if not lhs.get_head().sameQ(SymbolDirectedInfinity):
            return None
        if rhs.sameQ(SymbolInfinity) or rhs.sameQ(SymbolComplexInfinity):
            if len(lhs.elements) == 0:
                return True
            else:
                return self.equal2(
                    to_expression(SymbolSign, lhs.elements[0]), Integer1, max_extra_prec
                )
        if rhs.is_numeric():
            return False
        elif isinstance(rhs, Atom):
            return None
        if rhs.get_head().sameQ(lhs.get_head()):
            dir1 = dir2 = Integer1
            if len(lhs.elements) == 1:
                dir1 = lhs.elements[0]
            if len(rhs.elements) == 1:
                dir2 = rhs.elements[0]
            if self.equal2(dir1, dir2, max_extra_prec):
                return True
            # Now, compare the signs:
            dir1_sign = Expression(SymbolSign, dir1)
            dir2_sign = Expression(SymbolSign, dir2)
            return self.equal2(dir1_sign, dir2_sign, max_extra_prec)
        return

    def sympy_equal(self, lhs, rhs, max_extra_prec=None) -> Optional[bool]:
        try:
            lhs_sympy = lhs.to_sympy(evaluate=True, prec=COMPARE_PREC)
            rhs_sympy = rhs.to_sympy(evaluate=True, prec=COMPARE_PREC)
        except NotImplementedError:
            return None

        if lhs_sympy is None or rhs_sympy is None:
            return None

        if not is_number(lhs_sympy):
            lhs_sympy = mp_convert_constant(lhs_sympy, prec=COMPARE_PREC)
        if not is_number(rhs_sympy):
            rhs_sympy = mp_convert_constant(rhs_sympy, prec=COMPARE_PREC)

        # WL's interpretation of Equal[] which allows for slop in Reals
        # in the least significant digit of precision, while for Integers, comparison
        # has to be exact.

        if lhs_sympy.is_number and rhs_sympy.is_number:
            # assert min_prec(lhs, rhs) is None
            if max_extra_prec:
                prec = max_extra_prec
            else:
                prec = COMPARE_PREC
            lhs = lhs_sympy.n(dps(prec))
            rhs = rhs_sympy.n(dps(prec))
            if lhs == rhs:
                return True
            tol = 10 ** (-prec)
            diff = abs(lhs - rhs)
            if isinstance(diff, sympy.core.add.Add):
                return sympy.re(diff) < tol
            else:
                return diff < tol
        else:
            return None

    def equal2(self, lhs: Any, rhs: Any, max_extra_prec=None) -> Optional[bool]:
        """
        Two-argument Equal[]
        """
        if hasattr(lhs, "equal2"):
            result = lhs.equal2(rhs)
            if result is not None:
                return result
        elif lhs.sameQ(rhs):
            return True
        # TODO: Check $Assumptions
        # Still we didn't have a result. Try with the following
        # tests
        other_tests = (self.infty_equal, self.expr_equal, self.sympy_equal)
        for test in other_tests:
            c = test(lhs, rhs, max_extra_prec)
            if c is not None:
                return c
        return None

    def apply(self, items, evaluation):
        "%(name)s[items___]"
        items_sequence = items.get_sequence()
        n = len(items_sequence)
        if n <= 1:
            return SymbolTrue
        is_exact_vals = [
            Expression(SymbolExactNumberQ, arg).evaluate(evaluation)
            for arg in items_sequence
        ]
        if not all(val is SymbolTrue for val in is_exact_vals):
            return self.apply_other(items, evaluation)
        args = self.numerify_args(items, evaluation)
        for x, y in self.get_pairs(args):
            c = do_cplx_equal(x, y)
            if c is None:
                return
            if not self._op(c):
                return SymbolFalse
        return SymbolTrue

    def apply_other(self, args, evaluation):
        "%(name)s[args___?(!ExactNumberQ[#]&)]"
        args = args.get_sequence()
        max_extra_prec = SymbolMaxExtraPrecision.evaluate(evaluation).get_int_value()
        if type(max_extra_prec) is not int:
            max_extra_prec = COMPARE_PREC
        for x, y in self.get_pairs(args):
            c = self.equal2(x, y, max_extra_prec)
            if c is None:
                return
            if not self._op(c):
                return SymbolFalse
        return SymbolTrue


class _ComparisonOperator(_InequalityOperator):
    "Compares arguments in a chain e.g. a < b < c compares a < b and b < c."

    def apply(self, items, evaluation):
        "%(name)s[items___]"
        items_sequence = items.get_sequence()
        if len(items_sequence) <= 1:
            return SymbolTrue
        items = self.numerify_args(items, evaluation)
        wanted = operators[self.get_name()]
        if isinstance(items[-1], String):
            return None
        for i in range(len(items) - 1):
            x = items[i]
            if isinstance(x, String):
                return None
            y = items[i + 1]
            c = do_cmp(x, y)
            if c is None:
                return
            elif c not in wanted:
                return SymbolFalse
            assert c in wanted
        return SymbolTrue


def cmp(a, b) -> int:
    "Returns 0 if a == b, -1 if a < b and 1 if a > b"
    return (a > b) - (a < b)


def is_number(sympy_value) -> bool:
    return hasattr(sympy_value, "is_number") or isinstance(sympy_value, sympy.Float)


class SameQ(_ComparisonOperator):
    """
    <dl>
      <dt>'SameQ[$x$, $y$]'
      <dt>'$x$ === $y$'
      <dd>returns 'True' if $x$ and $y$ are structurally identical.
      Commutative properties apply, so if $x$ === $y$ then $y$ === $x$.

    </dl>

    <ul>
      <li>'SameQ' requires exact correspondence between expressions, expet that it still considers 'Real' numbers equal if they differ in their last binary digit.
      <li>$e1$ === $e2$ === $e3$ gives 'True' if all the $ei$'s are identical.
      <li>'SameQ[]' and 'SameQ[$expr$]' always yield 'True'.
    </ul>


    Any object is the same as itself:
    >> a === a
     = True

    Degenerate cases of 'SameQ' showing off how you can chain '===':
    >> SameQ[a] === SameQ[] === True
     = True

    Unlike 'Equal', 'SameQ' only yields 'True' if $x$ and $y$ have the same type:
    >> {1==1., 1===1.}
     = {True, False}


    >> 2./9. === .2222222222222222`15.9546
     = True
    The comparison consider just the lowest precision
    >> .2222222`6 === .2222`3
     = True
    Notice the extra decimal in the rhs. Because the internal representation,
    $0.222`3$ is not equivalent to $0.2222`3$:
    >> .2222222`6 === .222`3
     = False
    15.9546 is the value of '$MaxPrecision'
    """

    grouping = "None"  # Indeterminate grouping: Neither left nor right
    operator = "==="
    precedence = 290

    summary_text = "literal symbolic identity"

    def apply_list(self, items, evaluation):
        "%(name)s[items___]"
        items_sequence = items.get_sequence()
        if len(items_sequence) <= 1:
            return SymbolTrue

        first_item = items_sequence[0]
        for item in items_sequence[1:]:
            if not first_item.sameQ(item):
                return SymbolFalse
        return SymbolTrue


class UnsameQ(_ComparisonOperator):
    """
    <dl>
      <dt>'UnsameQ[$x$, $y$]'
      <dt>'$x$ =!= $y$'
      <dd>returns 'True' if $x$ and $y$ are not structurally identical.
      Commutative properties apply, so if $x$ =!= $y$, then $y$ =!= $x$.
    </dl>

    >> a =!= a
     = False
    >> 1 =!= 1.
     = True

    UnsameQ accepts any number of arguments and returns True if all expressions
    are structurally distinct:
    >> 1 =!= 2 =!= 3 =!= 4
     = True

    UnsameQ returns False if any expression is identical to another:
    >> 1 =!= 2 =!= 1 =!= 4
     = False

    UnsameQ[] and UnsameQ[expr] return True:
    >> UnsameQ[]
     = True
    >> UnsameQ[expr]
     = True
    """

    grouping = "None"  # Indeterminate grouping: Neither left nor right
    operator = "=!="
    precedence = 290

    summary_text = "not literal symbolic identity"

    def apply_list(self, items, evaluation):
        "%(name)s[items___]"
        items_sequence = items.get_sequence()
        if len(items_sequence) <= 1:
            return SymbolTrue

        for index, first_item in enumerate(items_sequence):
            for second_item in items_sequence[index + 1 :]:
                if first_item.sameQ(second_item):
                    return SymbolFalse
        return SymbolTrue


class TrueQ(Builtin):
    """
    <dl>
      <dt>'TrueQ[$expr$]'
      <dd>returns 'True' if and only if $expr$ is 'True'.
    </dl>

    >> TrueQ[True]
     = True

    >> TrueQ[False]
     = False

    >> TrueQ[a]
     = False
    """

    rules = {
        "TrueQ[expr_]": "If[expr, True, False, False]",
    }
    summary_text = "test whether the expression evaluates to True"


class BooleanQ(Builtin):
    """
    <dl>
      <dt>'BooleanQ[$expr$]'
      <dd>returns 'True' if $expr$ is either 'True' or 'False'.
    </dl>

    >> BooleanQ[True]
     = True

    >> BooleanQ[False]
     = True

    >> BooleanQ[a]
     = False

    >> BooleanQ[1 < 2]
     = True

    #> BooleanQ["string"]
     = False

    #> BooleanQ[Together[x/y + y/x]]
     = False
    """

    rules = {
        "BooleanQ[expr_]": "If[expr, True, True, False]",
    }
    summary_text = "test whether the expression evaluates to a boolean constant"


class Inequality(Builtin):
    """
    <dl>
    <dt>'Inequality'
        <dd>is the head of expressions involving different inequality
        operators (at least temporarily). Thus, it is possible to
        write chains of inequalities.
    </dl>

    >> a < b <= c
     = a < b && b <= c
    >> Inequality[a, Greater, b, LessEqual, c]
     = a > b && b <= c
    >> 1 < 2 <= 3
     = True
    >> 1 < 2 > 0
     = True
    >> 1 < 2 < -1
     = False
    """

    messages = {
        "ineq": (
            "Inequality called with `` arguments; the number of "
            "arguments is expected to be an odd number >= 3."
        ),
    }
    summary_text = "chain of inequalities"

    def apply(self, items, evaluation):
        "Inequality[items___]"

        elements = items.numerify(evaluation).get_sequence()
        count = len(elements)
        if count == 1:
            return SymbolTrue
        elif count % 2 == 0:
            evaluation.message("Inequality", "ineq", count)
        elif count == 3:
            name = elements[1].get_name()
            if name in operators:
                return Expression(Symbol(name), elements[0], elements[2])
        else:
            groups = [
                Expression(SymbolInequality, *elements[index - 1 : index + 2])
                for index in range(1, count - 1, 2)
            ]
            return Expression(SymbolAnd, *groups)


def do_cplx_equal(x, y) -> Optional[int]:
    if isinstance(y, Complex):
        x, y = y, x
    if isinstance(x, Complex):
        if isinstance(y, Complex):
            c = do_cmp(x.real, y.real)
            if c is None:
                return
            if c != 0:
                return False
            c = do_cmp(x.imag, y.imag)
            if c is None:
                return
            if c != 0:
                return False
            else:
                return True
        else:
            c = do_cmp(x.imag, Integer0)
            if c is None:
                return
            if c != 0:
                return False
            c = do_cmp(x.real, y.real)
            if c is None:
                return
            if c != 0:
                return False
            else:
                return True
    c = do_cmp(x, y)
    if c is None:
        return None
    return c == 0


def do_cmp(x1, x2) -> Optional[int]:

    # don't attempt to compare complex numbers
    for x in (x1, x2):
        # TODO: Send message General::nord
        if isinstance(x, Complex) or (
            x.has_form("DirectedInfinity", 1) and isinstance(x.elements[0], Complex)
        ):
            return None

    s1 = x1.to_sympy()
    s2 = x2.to_sympy()

    # Use internal comparisons only for Real which is uses
    # WL's interpretation of equal (which allows for slop
    # in the least significant digit of precision), and use
    # use sympy for everything else
    if s1.is_Float and s2.is_Float:
        if x1 == x2:
            return 0
        if x1 < x2:
            return -1
        return 1

    # we don't want to compare anything that
    # cannot be represented as a numeric value
    if s1.is_number and s2.is_number:
        if s1 == s2:
            return 0
        if s1 < s2:
            return -1
        return 1

    return None


class _SympyComparison(SympyFunction):
    def to_sympy(self, expr, **kwargs):
        to_sympy = super(_SympyComparison, self).to_sympy
        if len(expr.elements) > 2:

            def pairs(elements):
                yield Expression(Symbol(expr.get_head_name()), *elements[:2])
                elements = elements[1:]
                while len(elements) >= 2:
                    yield Expression(Symbol(expr.get_head_name()), *elements[:2])
                    elements = elements[1:]

            return sympy.And(*[to_sympy(p, **kwargs) for p in pairs(expr.elements)])
        return to_sympy(expr, **kwargs)


class Equal(_EqualityOperator, _SympyComparison):
    """
    <dl>
      <dt>'Equal[$x$, $y$]'
      <dt>'$x$ == $y$'
      <dd>is 'True' if $x$ and $y$ are known to be equal, or
        'False' if $x$ and $y$ are known to be unequal, in which case
        case, 'Not[$x$ == $y$]' will be 'True'.

        Commutative properties apply, so if $x$ == $y$ then $y$ == $x$.

        For any expression $x$ and $y$, Equal[$x$, $y$] == Not[Unequal[$x$, $y$]].

        For any expression 'SameQ[$x$, $y$]' implies Equal[$x$, $y$].
      <dt>'$x$ == $y$ == $z$ == ...'
      <dd> express a chain of equalities.
    </dl>

    Numerical Equalities:

    >> 1 == 1.
     = True

    >> 5/3 == 3/2
     = False

    Comparisons are done using the lower precision:
    >> N[E, 100] == N[E, 150]
     = True

    Compare an exact numeric expression and its corresponding approximate number:
    >> Pi == N[Pi, 20]
     = True

    Symbolic constants are compared numerically:
    >> Pi == 3.14
     = False

    Compare two exact numeric expressions; a numeric test may suffice to disprove equality:
    >> Pi ^ E == E ^ Pi
     = False

    ## TODO needs better precision tracking
    ## #> 2^^1.000000000000000000000000000000000000000000000000000000000000 ==  2^^1.000000000000000000000000000000000000000000000000000001111111
    ##  = True
    ## #> 2^^1.000000000000000000000000000000000000000000000000000000000000 ==  2^^1.000000000000000000000000000000000000000000000000000010000000
    ##  = False

    Real values are considered equal if they only differ in their last digits:
    >> 0.739085133215160642 == 0.739085133215160641
     = True
    >> 0.73908513321516064200000000 == 0.73908513321516064100000000
     = False

    ## TODO Needs power precision tracking
    ## >> 0.1 ^ 10000 == 0.1 ^ 10000 + 0.1 ^ 10012
    ##  = False

    Numeric evaluation using Equal:

    >> {Mod[6, 2] == 0, Mod[6, 4] == 0}
     = {True, False}

    String equalities:

    >> Equal["11", "11"]
     = True

    >> Equal["121", "11"]
     = False

    When we have symbols without values, the values are equal
    only if the symbols are equal:

    >> Clear[a, b]; a == b
     = a == b

    >> a == a
     = True

    >> a = b; a == b
     = True

    Comparision to mismatched types is False:

    >> Equal[11, "11"]
     = False

    Lists are compared based on their elements:
    >> {{1}, {2}} == {{1}, {2}}
     = True
    >> {1, 2} == {1, 2, 3}
     = False

    For chains of equalities, the comparison is done amongs all the pairs. The evaluation is successful
    only if the equality is satisfied over all the pairs:

    >> g[1] == g[1] == g[1]
     = True
    >> g[1] == g[1] == g[r]
     = g[1] == g[1] == g[r]

    Equality can also be combined with other inequality expressions, like:
    >> g[1] == g[2] != g[3]
     = g[1] == g[2] && g[2] != g[3]

    >> g[1] == g[2] <= g[3]
     = g[1] == g[2] && g[2] <= g[3]

    'Equal' with no parameter or an empty list is 'True':
    >> Equal[] == True
     = True

    'Equal' on one parameter or list element is also 'True'
    >> {Equal[x], Equal[1], Equal["a"]}
    = {True, True, True}

    This degenerate behavior is the same for 'Unequal';
    empty or single-element lists are both 'Equal' and 'Unequal'.
    """

    grouping = "None"
    operator = "=="
    summary_text = "numerical equality"
    sympy_name = "Eq"

    @staticmethod
    def get_pairs(args):
        for i in range(len(args) - 1):
            yield (args[i], args[i + 1])

    @staticmethod
    def _op(x):
        return x


class Unequal(_EqualityOperator, _SympyComparison):
    """
    <dl>
      <dt>'Unequal[$x$, $y$]' or $x$ != $y$ or $x$ \u2260 $y$
      <dd>is 'False' if $x$ and $y$ are known to be equal, or 'True' if $x$ and $y$ are known to be unequal.

        Commutative properties apply so if $x$ != $y$ then $y$ != $x$.

        For any expression $x$ and $y$, Unequal[$x$, $y$] == Not[Equal[$x$, $y$]].
    </dl>

    >> 1 != 1.
     = False

    Comparsion can be chained:
    >> 1 != 2 != 3
     = True

    >> 1 != 2 != x
     = 1 != 2 != x

    Strings are allowed:
    >> Unequal["11", "11"]
     = False

    Comparision to mismatched types is True:
    >> Unequal[11, "11"]
     = True

    Lists are compared based on their elements:
    >> {1} != {2}
     = True
    >> {1, 2} != {1, 2}
     = False
    >> {a} != {a}
     = False
    >> "a" != "b"
     = True
    >> "a" != "a"
     = False

    #> Pi != N[Pi]
     = False

    #> a_ != b_
     = a_ != b_

    #> Clear[a, b];
    #> a != a != a
     = False
    #> "abc" != "def" != "abc"
     = False

    ## Reproduce strange MMA behaviour
    #> a != b != a
     = a != b != a

    'Unequal' using an empty parameter or list, or a list with one element is True. This is the same as 'Equal".

    >> {Unequal[], Unequal[x], Unequal[1]}
     = {True, True, True}
    """

    operator = "!="
    summary_text = "numerical inequality"
    sympy_name = "Ne"

    @staticmethod
    def _op(x):
        return not x


class Less(_ComparisonOperator, _SympyComparison):
    """
    <dl>
      <dt>'Less[$x$, $y$]' or $x$ < $y$
      <dd>yields 'True' if $x$ is known to be less than $y$.
    </dl>

    >> 1 < 0
     = False

    LessEqual operator can be chained:
    >> 2/18 < 1/5 < Pi/10
     = True

    Using less on an undfined symbol value:
    >> 1 < 3 < x < 2
     = 1 < 3 < x < 2
    """

    operator = "<"
    summary_text = "less than"
    sympy_name = "StrictLessThan"


class LessEqual(_ComparisonOperator, _SympyComparison):
    """
     <dl>
       <dt>'LessEqual[$x$, $y$, ...]' or $x$ <= $y$ or $x$ \u2264 $y$
       <dd>yields 'True' if $x$ is known to be less than or equal to $y$.
     </dl>

    LessEqual operator can be chained:
    >> LessEqual[1, 3, 3, 2]
     = False

    >> 1 <= 3 <= 3
     = True

    """

    operator = "<="
    summary_text = "less than or equal to"
    sympy_name = "LessThan"  # in contrast to StrictLessThan


class Greater(_ComparisonOperator, _SympyComparison):
    """
    <dl>
      <dt>'Greater[$x$, $y$]' or '$x$ > $y$'
      <dd>yields 'True' if $x$ is known to be greater than $y$.
    </dl>

    Symbolic constants are compared numerically:
    >> E > 1
     = True

    Greater operator can be chained:
    >> a > b > c //FullForm
     = Greater[a, b, c]

    >> 3 > 2 > 1
     = True
    """

    operator = ">"
    summary_text = "greater than"
    sympy_name = "StrictGreaterThan"


class GreaterEqual(_ComparisonOperator, _SympyComparison):
    """
    <dl>
      <dt>'GreaterEqual[$x$, $y$]'
      <dt>$x$ \u2256 $y$ or '$x$ >= $y$'
      <dd>yields 'True' if $x$ is known to be greater than or equal
        to $y$.
    </dl>
    """

    operator = ">="
    summary_text = "greater than or equal to"
    sympy_name = "GreaterThan"


class Positive(Builtin):
    """
    <dl>
      <dt>'Positive[$x$]'
      <dd>returns 'True' if $x$ is a positive real number.
    </dl>

    >> Positive[1]
     = True

    'Positive' returns 'False' if $x$ is zero or a complex number:
    >> Positive[0]
     = False
    >> Positive[1 + 2 I]
     = False

    #> Positive[Pi]
     = True
    #> Positive[x]
     = Positive[x]
    #> Positive[Sin[{11, 14}]]
     = {False, True}
    """

    attributes = listable | protected

    rules = {
        "Positive[x_?NumericQ]": "If[x > 0, True, False, False]",
    }
    summary_text = "test whether an expression is a positive number"


class Negative(Builtin):
    """
    <dl>
    <dt>'Negative[$x$]'
        <dd>returns 'True' if $x$ is a negative real number.
    </dl>
    >> Negative[0]
     = False
    >> Negative[-3]
     = True
    >> Negative[10/7]
     = False
    >> Negative[1+2I]
     = False
    >> Negative[a + b]
     = Negative[a + b]
    #> Negative[-E]
     = True
    #> Negative[Sin[{11, 14}]]
     = {True, False}
    """

    attributes = listable | protected

    rules = {
        "Negative[x_?NumericQ]": "If[x < 0, True, False, False]",
    }
    summary_text = "test whether an expression is a negative number"


class NonNegative(Builtin):
    """
    <dl>
      <dt>'NonNegative[$x$]'
      <dd>returns 'True' if $x$ is a positive real number or zero.
    </dl>

    >> {Positive[0], NonNegative[0]}
     = {False, True}
    """

    attributes = listable | protected

    rules = {
        "NonNegative[x_?NumericQ]": "If[x >= 0, True, False, False]",
    }
    summary_text = "test whether an expression is a non-negative number"


class NonPositive(Builtin):
    """
    <dl>
    <dt>'NonPositive[$x$]'
        <dd>returns 'True' if $x$ is a negative real number or zero.
    </dl>

    >> {Negative[0], NonPositive[0]}
     = {False, True}
    """

    attributes = listable | protected

    rules = {
        "NonPositive[x_?NumericQ]": "If[x <= 0, True, False, False]",
    }
    summary_text = "test whether an expression is a non-positive number"


def expr_max(elements):
    result = Expression(SymbolDirectedInfinity, IntegerM1)
    for element in elements:
        c = do_cmp(element, result)
        if c > 0:
            result = element
    return result


def expr_min(elements):
    result = Expression(SymbolDirectedInfinity, Integer1)
    for element in elements:
        c = do_cmp(element, result)
        if c < 0:
            result = element
    return result


class _MinMax(Builtin):

    attributes = flat | numeric_function | one_identity | orderless | protected

    def apply(self, items, evaluation):
        "%(name)s[items___]"
        if hasattr(items, "flatten_with_respect_to_head"):
            items = items.flatten_with_respect_to_head(SymbolList)
        items = items.get_sequence()
        results = []
        best = None

        for item in items:
            if item.has_form("List", None):
                elements = item.elements
            else:
                elements = [item]
            for element in elements:
                if isinstance(element, String):
                    results.append(element)
                    continue
                if best is None:
                    best = element
                    results.append(best)
                    continue
                c = do_cmp(element, best)
                if c is None:
                    results.append(element)
                elif (self.sense == 1 and c > 0) or (self.sense == -1 and c < 0):
                    results.remove(best)
                    best = element
                    results.append(element)

        if not results:
            return Expression(SymbolDirectedInfinity, Integer(-self.sense))
        if len(results) == 1:
            return results.pop()
        if len(results) < len(items):
            # Some simplification was possible because we discarded
            # elements.
            return Expression(Symbol(self.get_name()), *results)
        # If we get here, no simplification was possible.
        return None


class Max(_MinMax):
    """
    <dl>
      <dt>'Max[$e_1$, $e_2$, ..., $e_i$]'
      <dd>returns the expression with the greatest value among the $e_i$.
    </dl>

    Maximum of a series of values:
    >> Max[4, -8, 1]
     = 4
    >> Max[E - Pi, Pi, E + Pi, 2 E]
     = E + Pi

    'Max' flattens lists in its arguments:
    >> Max[{1,2},3,{-3,3.5,-Infinity},{{1/2}}]
     = 3.5

    'Max' with symbolic arguments remains in symbolic form:
    >> Max[x, y]
     = Max[x, y]
    >> Max[5, x, -3, y, 40]
     = Max[40, x, y]

    With no arguments, 'Max' gives '-Infinity':
    >> Max[]
     = -Infinity

    'Max' does not compare strings or symbols:
    >> Max[-1.37, 2, "a", b]
     = Max[2, a, b]
    #> Max[x]
     = x
    """

    sense = 1
    summary_text = "the maximum value"


class Min(_MinMax):
    """
    <dl>
      <dt>'Min[$e_1$, $e_2$, ..., $e_i$]'
      <dd>returns the expression with the lowest value among the $e_i$.
    </dl>

    Minimum of a series of values:
    >> Min[4, -8, 1]
     = -8
    >> Min[E - Pi, Pi, E + Pi, 2 E]
     = E - Pi

    'Min' flattens lists in its arguments:
    >> Min[{1,2},3,{-3,3.5,-Infinity},{{1/2}}]
     = -Infinity

    'Min' with symbolic arguments remains in symbolic form:
    >> Min[x, y]
     = Min[x, y]
    >> Min[5, x, -3, y, 40]
     = Min[-3, x, y]

    With no arguments, 'Min' gives 'Infinity':
    >> Min[]
     = Infinity

    #> Min[x]
     = x
    """

    sense = -1
    summary_text = "the minimum value"
