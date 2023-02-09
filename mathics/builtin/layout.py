# -*- coding: utf-8 -*-

"""
Layout

This module contains symbols used to define the high level layout for
expression formatting.

For instance, to represent a set of consecutive expressions in a row,
we can use 'Row'.

"""


from mathics.builtin.base import BinaryOperator, Builtin, Operator
from mathics.builtin.box.layout import GridBox, RowBox, to_boxes
from mathics.builtin.makeboxes import MakeBoxes
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Real, String
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolMakeBoxes
from mathics.eval.lists import list_boxes
from mathics.eval.makeboxes import format_element

SymbolSubscriptBox = Symbol("System`SubscriptBox")


class Center(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Center.html</url>

    <dl>
      <dt>'Center'
      <dd>is used with the 'ColumnAlignments' option to 'Grid' or
        'TableForm' to specify a centered column.
    </dl>
    """

    summary_text = "center alignment"


class Format(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Format.html</url>

    <dl>
      <dt>'Format[$expr$]'
      <dd>holds values specifying how $expr$ should be printed.
    </dl>

    Assign values to 'Format' to control how particular expressions
    should be formatted when printed to the user.
    >> Format[f[x___]] := Infix[{x}, "~"]
    >> f[1, 2, 3]
     = 1 ~ 2 ~ 3
    >> f[1]
     = 1

    Raw objects cannot be formatted:
    >> Format[3] = "three";
     : Cannot assign to raw object 3.

    Format types must be symbols:
    >> Format[r, a + b] = "r";
     : Format type a + b is not a symbol.

    Formats must be attached to the head of an expression:
    >> f /: Format[g[f]] = "my f";
     : Tag f not found or too deep for an assigned rule.
    """

    messages = {"fttp": "Format type `1` is not a symbol."}
    summary_text = (
        "settable low-level translator from various forms to evaluatable expressions"
    )


class Grid(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Grid.html</url>

    <dl>
      <dt>'Grid[{{$a1$, $a2$, ...}, {$b1$, $b2$, ...}, ...}]'
      <dd>formats several expressions inside a 'GridBox'.
    </dl>

    >> Grid[{{a, b}, {c, d}}]
     = a   b
     .
     . c   d

    For shallow lists, elements are shown as a column:
    >> Grid[{a, b, c}]
     = a
     .
     . b
     .
     . c

    If the sublists have different sizes, the grid has the number of columns of the \
    largest one. Incomplete rows are completed with empty strings:

    >> Grid[{{"first", "second", "third"},{a},{1, 2, 3}}]
     = first   second   third
     .
     . a
     .
     . 1       2        3

    If the list is a mixture of lists and other expressions, the non-list expressions are
    shown as rows:

    >> Grid[{"This is a long title", {"first", "second", "third"},{a},{1, 2, 3}}]
     = This is a long title
     .
     . first   second   third
     .
     . a
     .
     . 1       2        3

    """

    options = GridBox.options
    summary_text = " 2D layout containing arbitrary objects"

    def eval_makeboxes(self, array, f, evaluation: Evaluation, options) -> Expression:
        """MakeBoxes[Grid[array_List, OptionsPattern[Grid]],
        f:StandardForm|TraditionalForm|OutputForm]"""

        elements = array.elements

        rows = (
            element.elements if element.has_form("List", None) else element
            for element in elements
        )

        def format_row(row):
            if isinstance(row, tuple):
                return ListExpression(
                    *(format_element(item, evaluation, f) for item in row),
                )
            return format_element(row, evaluation, f)

        return GridBox(
            ListExpression(*(format_row(row) for row in rows)),
            *options_to_rules(options),
        )


class Infix(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Infix.html</url>

    <dl>
      <dt>'Infix[$expr$, $oper$, $prec$, $assoc$]'
      <dd>displays $expr$ with the infix operator $oper$, with precedence $prec$ and associativity $assoc$.
    </dl>

    'Infix' can be used with 'Format' to display certain forms with
    user-defined infix notation:
    >> Format[g[x_, y_]] := Infix[{x, y}, "#", 350, Left]
    >> g[a, g[b, c]]
     = a # (b # c)
    >> g[g[a, b], c]
     = a # b # c
    >> g[a + b, c]
     = (a + b) # c
    >> g[a * b, c]
     = a b # c
    >> g[a, b] + c
     = c + a # b
    >> g[a, b] * c
     = c (a # b)

    >> Infix[{a, b, c}, {"+", "-"}]
     = a + b - c

    #> Format[r[items___]] := Infix[If[Length[{items}] > 1, {items}, {ab}], "~"]
    #> r[1, 2, 3]
     = 1 ~ 2 ~ 3
    #> r[1]
     = ab
    """

    messages = {
        "normal": "Nonatomic expression expected at position `1`",
    }
    summary_text = "infix form"


class Left(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Left.html</url>

    <dl>
      <dt>'Left'
      <dd>is used with operator formatting constructs to specify a \
          left-associative operator.
    </dl>
    """

    summary_text = "left alignment/left associative"


class NonAssociative(Builtin):
    """
        ## For some reason, this is a Builtin symbol in WMA, but it is not available in WR.
        ## <url>:WMA link:https://reference.wolfram.com/language/ref/NonAssociative.html</url>
    on, logic, comparison, datentime, attributes and binary)

        <dl>
          <dt>'NonAssociative'
          <dd>is used with operator formatting constructs to specify a non-associative operator.
        </dl>
    """

    summary_text = "non-associative operator"


class Postfix(BinaryOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Postfix.html</url>

    <dl>
      <dt>'$x$ // $f$'
      <dd>is equivalent to '$f$[$x$]'.
    </dl>

    >> b // a
     = a[b]
    >> c // b // a
     = a[b[c]]

    The postfix operator '//' is parsed to an expression before evaluation:
    >> Hold[x // a // b // c // d // e // f]
     = Hold[f[e[d[c[b[a[x]]]]]]]
    """

    grouping = "Left"
    operator = "//"
    operator_display = None
    precedence = 70
    summary_text = "postfix form"


class Precedence(Builtin):
    """
        ## As NonAssociative, this is a Builtin in WMA that does not have an entry in WR.
        ## <url>:WMA link:https://reference.wolfram.com/language/ref/Precedence.html</url>
    on, logic, comparison, datentime, attributes and binary)

        <dl>
          <dt>'Precedence[$op$]'
          <dd>returns the precedence of the built-in operator $op$.
        </dl>

        >> Precedence[Plus]
         = 310.
        >> Precedence[Plus] < Precedence[Times]
         = True

        Unknown symbols have precedence 670:
        >> Precedence[f]
         = 670.
        Other expressions have precedence 1000:
        >> Precedence[a + b]
         = 1000.
    """

    summary_text = "an object to be parenthesized with a given precedence level"

    def eval(self, expr, evaluation) -> Real:
        "Precedence[expr_]"

        name = expr.get_name()
        precedence = 1000
        if name:
            builtin = evaluation.definitions.get_definition(name, only_if_exists=True)
            if builtin:
                builtin = builtin.builtin
            if builtin is not None and isinstance(builtin, Operator):
                precedence = builtin.precedence
            else:
                precedence = 670
        return Real(precedence)


class Prefix(BinaryOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Prefix.html</url>

    <dl>
      <dt>'$f$ @ $x$'
      <dd>is equivalent to '$f$[$x$]'.
    </dl>

    >> a @ b
     = a[b]
    >> a @ b @ c
     = a[b[c]]
    >> Format[p[x_]] := Prefix[{x}, "*"]
    >> p[3]
     = *3
    >> Format[q[x_]] := Prefix[{x}, "~", 350]
    >> q[a+b]
     = ~(a + b)
    >> q[a*b]
     = ~a b
    >> q[a]+b
     = b + ~a

    The prefix operator '@' is parsed to an expression before evaluation:
    >> Hold[a @ b @ c @ d @ e @ f @ x]
     = Hold[a[b[c[d[e[f[x]]]]]]]
    """

    grouping = "Right"
    operator = "@"
    operator_display = None
    precedence = 640
    summary_text = "prefix form"


class Right(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Right.html</url>

    <dl>
      <dt>'Right'
      <dd>is used with operator formatting constructs to specify a right-associative operator.
    </dl>
    """

    summary_text = "right alignment/right associative"


class Row(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Row.html</url>

    <dl>
      <dt>'Row[{$expr$, ...}]'
      <dd>formats several expressions inside a 'RowBox'.
    </dl>
    """

    summary_text = "1D layouts containing arbitrary objects in a row"

    def eval_makeboxes(self, items, sep, form, evaluation: Evaluation):
        """MakeBoxes[Row[{items___}, sep_:""],
        form:StandardForm|TraditionalForm|OutputForm]"""

        items = items.get_sequence()
        if not isinstance(sep, String):
            sep = MakeBoxes(sep, form)
        if len(items) == 1:
            return MakeBoxes(items[0], form)
        else:
            result = []
            for index, item in enumerate(items):
                if index > 0 and not sep.sameQ(String("")):
                    result.append(to_boxes(sep, evaluation))
                item = MakeBoxes(item, form).evaluate(evaluation)
                item = to_boxes(item, evaluation)
                result.append(item)
            return RowBox(*result)


class Style(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Style.html</url>

    <dl>
      <dt>'Style[$expr$, options]'
      <dd>displays $expr$ formatted using the specified option settings.

      <dt>'Style[$expr$, "style"]'
      <dd> uses the option settings for the specified style in the current notebook.

      <dt>'Style[$expr$, $color$]'
      <dd>displays using the specified color.

      <dt>'Style[$expr$, $Bold$]'
      <dd>displays with fonts made bold.

      <dt>'Style[$expr$, $Italic$]'
      <dd>displays with fonts made italic.

      <dt>'Style[$expr$, $Underlined$]'
      <dd>displays with fonts underlined.

      <dt>'Style[$expr$, $Larger$]
      <dd>displays with fonts made larger.

      <dt>'Style[$expr$, $Smaller$]'
      <dd>displays with fonts made smaller.

      <dt>'Style[$expr$, $n$]'
      <dd>displays with font size n.

      <dt>'Style[$expr$, $Tiny$]'
      <dt>'Style[$expr$, $Small$]', etc.
      <dd>display with fonts that are tiny, small, etc.
    </dl>
    """

    summary_text = "wrapper specifying styles and style options to apply"
    options = {"ImageSizeMultipliers": "Automatic"}

    rules = {
        "MakeBoxes[Style[expr_, OptionsPattern[Style]], f_]": (
            "StyleBox[MakeBoxes[expr, f], "
            "ImageSizeMultipliers -> OptionValue[ImageSizeMultipliers]]"
        )
    }


class Subscript(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Subscript.html</url>

    <dl>
      <dt>'Subscript[$a$, $i$]'
      <dd>displays as $a_i$.
    </dl>

    >> Subscript[x,1,2,3] // TeXForm
     = x_{1,2,3}
    """

    summary_text = "format an expression with a subscript"

    def eval_makeboxes(self, x, y, f, evaluation) -> Expression:
        "MakeBoxes[Subscript[x_, y__], f:StandardForm|TraditionalForm]"

        y = y.get_sequence()
        return Expression(
            SymbolSubscriptBox,
            Expression(SymbolMakeBoxes, x, f),
            *list_boxes(y, f, evaluation),
        )


class Subsuperscript(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Subsuperscript.html</url>

    <dl>
      <dt>'Subsuperscript[$a$, $b$, $c$]'
      <dd>displays as $a_b^c$.
    </dl>

    >> Subsuperscript[a, b, c] // TeXForm
     = a_b^c
    """

    rules = {
        "MakeBoxes[Subsuperscript[x_, y_, z_], "
        "f:StandardForm|TraditionalForm]": (
            "SubsuperscriptBox[MakeBoxes[x, f], MakeBoxes[y, f], " "MakeBoxes[z, f]]"
        )
    }
    summary_text = "format an expression with a subscript and a superscript"


class Superscript(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Superscript.html</url>

    <dl>
      <dt>'Superscript[$x$, $y$]'
      <dd>displays as $x$^$y$.
    </dl>

    >> Superscript[x,3] // TeXForm
     = x^3
    """

    summary_text = "format an expression with a superscript"
    rules = {
        "MakeBoxes[Superscript[x_, y_], f:StandardForm|TraditionalForm]": (
            "SuperscriptBox[MakeBoxes[x, f], MakeBoxes[y, f]]"
        )
    }
