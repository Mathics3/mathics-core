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
    return_before_value: bool = False

    def eval(self, expr, evaluation: Evaluation):
        """%(name)s[expr_]"""
        return eval_inplace_op(
            self,
            expr,
            self.operator_symbol,
            self.increment_symbol,
            self.return_before_value,
            evaluation,
        )


# class AddTo(InfixOperator, InplaceInfixOperator):
#     """
#     <url>:WMA link:https://reference.wolfram.com/language/ref/AddTo.html</url>

#     <dl>
#       <dt>'AddTo[$x$, $dx$]'
#       <dt>'$x$ += $dx$'
#       <dd>is equivalent to '$x$ = $x$ + $dx$'.
#     </dl>

#     >> a = 10;
#     >> a += 2
#      = 12
#     >> a
#      = 12
#     """

#     attributes = A_HOLD_FIRST | A_PROTECTED
#     operator = "+="

#     operator_symbol: Symbol = SymbolPlus
#     return_before_value: bool = False
#     summary_text = "add a value and assigns that returning the new value"

#     def eval(self, expr, increment, evaluation: Evaluation):
#         """%(name)s[expr_, increment_]"""
#         return eval_inplace_op(self, expr, self.operator_symbol, increment, self.return_before_value, evaluation)


# class Decrement(InplaceInfixOperator, InfixOperator, PostfixOperator):
#     """
#     <url>:WMA link
#     :https://reference.wolfram.com/language/ref/Decrement.html</url>

#     <dl>
#       <dt>'Decrement[$x$]'

#       <dt>'$x$--'
#       <dd>decrements $x$ by 1, returning the original value of $x$.
#     </dl>

#     >> a = 5;
#     X> a--
#      = 5
#     X> a
#      = 4
#     """

#     increment_symbol = IntegerM1
#     attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
#     operator = "--"

#     summary_text = (
#         "decreases the value by one and assigns that returning the original value"
#     )


# class AddTo(InfixOperator):
#     """
#     <url>:WMA link:https://reference.wolfram.com/language/ref/AddTo.html</url>

#     <dl>
#       <dt>'AddTo[$x$, $dx$]'
#       <dt>'$x$ += $dx$'
#       <dd>is equivalent to '$x$ = $x$ + $dx$'.
#     </dl>

#     >> a = 10;
#     >> a += 2
#      = 12
#     >> a
#      = 12
#     """

#     attributes = A_HOLD_FIRST | A_PROTECTED
#     grouping = "Right"
#     operator = "+="

#     rules = {
#         "x_ += dx_": "x = x + dx",
#     }
#     summary_text = "add a value and assigns that returning the new value"


class Decrement(PostfixOperator):
    """
    <url>:WMA link
    :https://reference.wolfram.com/language/ref/Decrement.html</url>

    <dl>
      <dt>'Decrement[$x$]'

      <dt>'$x$--'
      <dd>decrements $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 5;
    X> a--
     = 5
    X> a
     = 4
    """

    operator = "--"
    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED

    rules = {
        "x_--": "Module[{t=x}, x = x - 1; t]",
    }

    summary_text = (
        "decreases the value by one and assigns that returning the original value"
    )


class DivideBy(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DivideBy.html</url>

    <dl>
      <dt>'DivideBy[$x$, $dx$]'
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
    operator = "/="

    rules = {
        "x_ /= dx_": "x = x / dx",
    }
    summary_text = "divide a value and assigns that returning the new value"


# class Increment(InplaceInfixOperator, InfixOperator, PostfixOperator):
#     """
#     <url>:WMA link:
#     https://reference.wolfram.com/language/ref/Increment.html</url>

#     <dl>
#       <dt>'Increment[$x$]'

#       <dt>'$x$++'
#       <dd>increments $x$ by 1, returning the original value of $x$.
#     </dl>

#     >> a = 2;
#     >> a++
#      = 2
#     >> a
#      = 3
#     Grouping of 'Increment', 'PreIncrement' and 'Plus':
#     >> ++++a+++++2//Hold//FullForm
#      = Hold[Plus[PreIncrement[PreIncrement[Increment[Increment[a]]]], 2]]
#     """

#     attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
#     increment_symbol = Integer1
#     operator = "++"
#     operator_symbol = SymbolPlus
#     return_before_value: bool = True
#     summary_text = (
#         "increases the value by one and assigns that returning the original value"
#     )


class Increment(PostfixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Increment.html</url>

    <dl>
      <dt>'Increment[$x$]'

      <dt>'$x$++'
      <dd>increments $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 2;
    >> a++
     = 2
    >> a
     = 3
    Grouping of 'Increment', 'PreIncrement' and 'Plus':
    >> ++++a+++++2//Hold//FullForm
     = Hold[Plus[PreIncrement[PreIncrement[Increment[Increment[a]]]], 2]]
    """

    operator = "++"
    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED

    rules = {
        "x_++": (
            "Module[{Internal`IncrementTemporary = x},"
            "       x = x + 1;"
            "       Internal`IncrementTemporary"
            "]"
        ),
    }

    summary_text = (
        "increases the value by one and assigns that returning the original value"
    )


class PreIncrement(PrefixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/PreIncrement.html</url>

    <dl>
      <dt>'PreIncrement[$x$]'
      <dt>'++$x$'
      <dd>increments $x$ by 1, returning the new value of $x$.
    </dl>

    '++$a$' is equivalent to '$a$ = $a$ + 1':
    >> a = 2;
    >> ++a
     = 3
    >> a
     = 3
    """

    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
    operator = "++"

    rules = {
        "++x_": "x = x + 1",
    }

    summary_text = "increase the value by one and assigns that returning the new value"


class PreDecrement(PrefixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/PreDecrement.html</url>

    <dl>
      <dt>'PreDecrement[$x$]'

      <dt>'--$x$'
      <dd>decrements $x$ by 1, returning the new value of $x$.
    </dl>

    '--$a$' is equivalent to '$a$ = $a$ - 1':
    >> a = 2;
    >> --a
     = 1
    >> a
     = 1
    """

    operator = "--"
    attributes = A_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED

    rules = {
        "--x_": "x = x - 1",
    }
    summary_text = "decrease the value by one and assigns that returning the new value"


class SubtractFrom(InfixOperator):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/SubtractFrom.html</url>

    <dl>
      <dt>'SubtractFrom[$x$, $dx$]'
      <dt>'$x$ -= $dx$'
      <dd>is equivalent to '$x$ = $x$ - $dx$'.
    </dl>

    >> a = 10;
    >> a -= 2
     = 8
    >> a
     = 8
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    grouping = "Right"
    operator = "-="

    rules = {
        "x_ -= dx_": "x = x - dx",
    }
    summary_text = "subtract a value and assins that returning the new value"


class TimesBy(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TimesBy.html</url>

    <dl>
      <dt>'TimesBy[$x$, $dx$]'
      <dt>'$x$ *= $dx$'
      <dd>is equivalent to '$x$ = $x$ * $dx$'.
    </dl>

    >> a = 10;
    >> a *= 2
     = 20
    >> a
     = 20
    """

    operator = "*="
    attributes = A_HOLD_FIRST | A_PROTECTED
    grouping = "Right"

    rules = {
        "x_ *= dx_": "x = x * dx",
    }
    summary_text = "multiply a value and assigns that returning the new value"
