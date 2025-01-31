# -*- coding: utf-8 -*-
"""
In-place binary assignment operator

There are a number operators and functions that combine assignment with \
some sort of binary operator.

Sometimes a value is returned <i>before</i> the assignment occurs. When \
there is an operator for this, the operator is a prefix operator and the \
function name starts with 'Pre'.

Sometimes the binary operation occurs first, and <i>then</i> the assignment \
occurs. When there is an operator for this, the operator is a postfix operator.

Infix operators combined with assignment end in 'By', 'From', or 'To'.
"""


from mathics.core.atoms import Integer1, IntegerM1
from mathics.core.attributes import A_HOLD_FIRST, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import InfixOperator, PostfixOperator, PrefixOperator
from mathics.core.evaluation import Evaluation
from mathics.core.systemsymbols import SymbolPlus
from mathics.eval.assignments.assign_binaryop import eval_inplace_op


class InplaceInfixOperator:
    grouping = "Right"
    operator_symbol = SymbolPlus
    increment_symbol = Integer1
    returns_updated_value: bool = True

    def eval(self, expr, evaluation: Evaluation):
        """%(name)s[expr_]"""
        return eval_inplace_op(
            self,
            expr,
            self.operator_symbol,
            self.increment_symbol,
            self.returns_updated_value,
            evaluation,
        )


class AddTo(InfixOperator, InplaceInfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/AddTo.html</url>

    <dl>
      <dt>'AddTo'[$x$, $dx$]
      <dt>'$x$ += $dx$'
      <dd>is equivalent to '$x$ = $x$ + $dx$'.
    </dl>

    >> a = 10;
    >> a += 2
     = 12
    >> a
     = 12
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    grouping = "Right"

    operator_symbol = SymbolPlus
    return_before_value: bool = True
    summary_text = "add a value and update; return the updated value"

    def eval(self, expr, increment, evaluation: Evaluation):
        """%(name)s[expr_, increment_]"""
        return eval_inplace_op(
            self,
            expr,
            self.operator_symbol,
            increment,
            self.return_before_value,
            evaluation,
        )


# Decrement has Infix properties for evaluation purposes, but Postfix
# properties for operator association.
class Decrement(InplaceInfixOperator, InfixOperator, PostfixOperator):
    """
    <url>:WMA link
    :https://reference.wolfram.com/language/ref/Decrement.html</url>

    <dl>
      <dt>'Decrement'[$x$]

      <dt>'$x$--'
      <dd>decrements $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 5; a--
     = 5
    >> a
     = 4

    Decrement a numerical value:

    >> a = 1.6; a--; a
     = 0.6

    Decrement all values in a list:

    >> a = {1, 3, 5}
     = {1, 3, 5}

    >> a--; a
     = {0, 2, 4}

    Compare with <url>:PreDecrement:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/predecrement
    </url> which returns the value before updating, and <url>:Increment:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/increment
    </url> which goes the other way.
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
    increment_symbol = IntegerM1
    operator_symbol = SymbolPlus

    returns_updated_value = False
    summary_text = (
        "decreases a value by one and assign the value; return the original value"
    )


class DivideBy(InplaceInfixOperator, InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DivideBy.html</url>

    <dl>
      <dt>'DivideBy'[$x$, $dx$]
      <dt>'$x$ /= $dx$'
      <dd>is equivalent to '$x$ = $x$ / $dx$'.
    </dl>

    >> a = 10;
    >> a /= 2
     = 5
    >> a
     = 5
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    grouping = "Right"

    rules = {
        "x_ /= dx_": "x = x / dx",
    }
    summary_text = "divide by a value and update; return the new value"


class Increment(InplaceInfixOperator, InfixOperator, PostfixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Increment.html</url>

    <dl>
      <dt>'Increment'[$x$]

      <dt>'$x$++'
      <dd>increments $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 1; a++
     = 1
    >> a
     = 2

    Increment a numeric value:

    >> a = 1.5; a++
     = 1.5

    >> a
     = 2.5

    Increment a symbolic value:

    >> y = 2 x; y++; y
     = 1 + 2 x

    Increment all values in a list:

    >> x = {1, 3, 5}
     = {1, 3, 5}

    x++; x
     = {2, 4, 6}

    Grouping of 'Increment', 'PreIncrement' and 'Plus':
    >> ++++a+++++2//Hold//FullForm
     = Hold[Plus[PreIncrement[PreIncrement[Increment[Increment[a]]]], 2]]

    Compare with <url>:PreIncrement:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/preincrement
    </url> which returns the value before update.

    #> Clear[a, x, y]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
    increment_symbol = Integer1
    operator_symbol = SymbolPlus
    returns_updated_value: bool = False
    summary_text = "increases the value by one and update; return the original value"


class PreDecrement(InplaceInfixOperator, PrefixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/PreDecrement.html</url>

    <dl>
      <dt>'PreDecrement'[$x$]

      <dt>'--$x$'
      <dd>decrements $x$ by 1, returning the new value of $x$.
    </dl>

    '--$a$' is equivalent to '$a$ = $a$ - 1':
    >> a = 2;
    >> --a
     = 1
    >> a
     = 1

    Compare with <url>:Decrement:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/decrement
    </url> which returns the updated value, and <url>:Increment:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/increment
    </url> which goes the other way.

    #> Clear[a]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
    increment_symbol = IntegerM1
    operator_symbol = SymbolPlus
    returns_updated_value: bool = True
    summary_text = "decrease the value by one and update; return the new value"


class PreIncrement(InplaceInfixOperator, PrefixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/PreIncrement.html</url>

    <dl>
      <dt>'PreIncrement'[$x$]
      <dt>'++$x$'
      <dd>increments $x$ by 1, returning the new value of $x$.
    </dl>

    '++$a$' is equivalent to '$a$ = $a$ + 1':
    >> a = 2
     = 2

    >> ++a
     = 3

    >> a
     = 3

    PreIncrement a numeric value:

    >> a + 1.6
     = 4.6


    PreIncrement a symbolic value:

    #> Clear[x, y]

    >> y = x; ++y
     = 1 + x

    >> y
     = 1 + x

    Compare with <url>:Increment:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/increment
    </url> which returns the updated value, and <url>:PreDecrement:
    /doc/reference-of-built-in-symbols/assignments/in-place-binary-assignment-operator/predecrement
    </url> which goes the other way.

    #> Clear[a, x, y]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
    operator_symbol = SymbolPlus
    return_before_value: bool = False

    summary_text = "increase the value by one and updage; return the new value"


class SubtractFrom(InfixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/SubtractFrom.html</url>

    <dl>
      <dt>'SubtractFrom'[$x$, $dx$]
      <dt>'$x$ -= $dx$'
      <dd>is equivalent to '$x$ = $x$ - $dx$'.
    </dl>

    >> a = 10;
    >> a -= 2
     = 8
    >> a
     = 8

    #> Clear[a]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    grouping = "Right"

    rules = {
        "x_ -= dx_": "x = x - dx",
    }
    summary_text = "subtract a value and update; return the new value"


class TimesBy(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TimesBy.html</url>

    <dl>
      <dt>'TimesBy'[$x$, $dx$]
      <dt>'$x$ *= $dx$'
      <dd>is equivalent to '$x$ = $x$ * $dx$'.
    </dl>

    >> a = 10;
    >> a *= 2
     = 20
    >> a
     = 20

    #> Clear[a]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    grouping = "Right"

    rules = {
        "x_ *= dx_": "x = x * dx",
    }
    summary_text = "multiply a value and update; return the new value"
