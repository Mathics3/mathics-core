# -*- coding: utf-8 -*-
"""
Assignmment plus binary operator

There are a number operators and functions that combine assignment with some sort of binary operator.

Sometimes a value is returned <i>before</i> the assignment occurs. When there is an operator for this, the operator is a prefix operator and the function name starts with 'Pre'.

Sometimes the binary operation occurs first, and <i>then</i> the assignment occurs. When there is an operator for this, the operator is a postfix operator.

Infix operators combined with assignment end in 'By', 'From', or 'To'.

"""


from mathics.builtin.base import (
    BinaryOperator,
    PostfixOperator,
    PrefixOperator,
)


class AddTo(BinaryOperator):
    """
    <dl>
      <dt>'AddTo[$x$, $dx$]'</dt>

      <dt>'$x$ += $dx$'</dt>
      <dd>is equivalent to '$x$ = $x$ + $dx$'.
    </dl>

    >> a = 10;
    >> a += 2
     = 12
    >> a
     = 12
    """

    attributes = ("HoldFirst",)
    grouping = "Right"
    operator = "+="
    precedence = 100

    rules = {
        "x_ += dx_": "x = x + dx",
    }
    summary_text = "adds a value and assignes that returning the new value"


class Decrement(PostfixOperator):
    """
    <dl>
      <dt>'Decrement[$x$]'</dt>

      <dt>'$x$--'</dt>
      <dd>decrements $x$ by 1, returning the original value of $x$.
    </dl>

    >> a = 5;
    X> a--
     = 5
    X> a
     = 4
    """

    operator = "--"
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

    rules = {
        "x_--": "Module[{t=x}, x = x - 1; t]",
    }

    summary_text = (
        "decreases the value by one and assigns that returning the original value"
    )


class DivideBy(BinaryOperator):
    """
    <dl>
      <dt>'DivideBy[$x$, $dx$]'</dt>

      <dt>'$x$ /= $dx$'</dt>
      <dd>is equivalent to '$x$ = $x$ / $dx$'.
    </dl>

    >> a = 10;
    >> a /= 2
     = 5
    >> a
     = 5
    """

    attributes = ("HoldFirst",)
    grouping = "Right"
    operator = "/="
    precedence = 100

    rules = {
        "x_ /= dx_": "x = x / dx",
    }
    summary_text = "divides a value and assigns that returning the new value"


class Increment(PostfixOperator):
    """
    <dl>
      <dt>'Increment[$x$]'</dt>

      <dt>'$x$++'</dt>
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
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

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
    <dl>
    <dt>'PreIncrement[$x$]'</dt>
    <dt>'++$x$'</dt>
        <dd>increments $x$ by 1, returning the new value of $x$.
    </dl>

    '++$a$' is equivalent to '$a$ = $a$ + 1':
    >> a = 2;
    >> ++a
     = 3
    >> a
     = 3
    """

    attributes = ("HoldFirst", "ReadProtected")
    operator = "++"
    precedence = 660

    rules = {
        "++x_": "x = x + 1",
    }

    summary_text = "increases the value by one and assigns that returning the new value"


class PreDecrement(PrefixOperator):
    """
    <dl>
      <dt>'PreDecrement[$x$]'</dt>

      <dt>'--$x$'</dt>
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
    precedence = 660
    attributes = ("HoldFirst", "ReadProtected")

    rules = {
        "--x_": "x = x - 1",
    }
    summary_text = "decreases the value by one and assigns that returning the new value"


class SubtractFrom(BinaryOperator):
    """
    <dl>
    <dt>'SubtractFrom[$x$, $dx$]'</dt>
    <dt>'$x$ -= $dx$'</dt>
        <dd>is equivalent to '$x$ = $x$ - $dx$'.
    </dl>

    >> a = 10;
    >> a -= 2
     = 8
    >> a
     = 8
    """

    attributes = ("HoldFirst",)
    grouping = "Right"
    operator = "-="
    precedence = 100

    rules = {
        "x_ -= dx_": "x = x - dx",
    }
    summary_text = "subtracts a value and assins that returning the new value"


class TimesBy(BinaryOperator):
    """
    <dl>
      <dt>'TimesBy[$x$, $dx$]'</dt>

      <dt>'$x$ *= $dx$'</dt>
      <dd>is equivalent to '$x$ = $x$ * $dx$'.
    </dl>

    >> a = 10;
    >> a *= 2
     = 20
    >> a
     = 20
    """

    operator = "*="
    precedence = 100
    attributes = ("HoldFirst",)
    grouping = "Right"

    rules = {
        "x_ *= dx_": "x = x * dx",
    }
    summary_text = "multiplies a value and assigns that returning the new value"
