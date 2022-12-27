# -*- coding: utf-8 -*-

"""
This module contains symbols used to define the high level layout for \
expression formatting.

For instance, to represent a set of consecutive expressions in a row, \
we can use ``Row``.

"""
from typing import Optional, Union

from mathics.builtin.base import BinaryOperator, Builtin, Operator
from mathics.builtin.box.layout import GridBox, RowBox, to_boxes
from mathics.builtin.lists import list_boxes
from mathics.builtin.makeboxes import MakeBoxes
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Integer1, Real, String
from mathics.core.convert.op import operator_to_ascii, operator_to_unicode
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import (
    SymbolFullForm,
    SymbolInputForm,
    SymbolLeft,
    SymbolMakeBoxes,
    SymbolNone,
    SymbolOutputForm,
    SymbolRight,
    SymbolRowBox,
)
from mathics.eval.makeboxes import eval_fullform_makeboxes, format_element, parenthesize

SymbolNonAssociative = Symbol("System`NonAssociative")
SymbolSubscriptBox = Symbol("System`SubscriptBox")


####################################################################
# This section might get moved to mathics.box
#
# Some of the code below get replace Mathics code or may get put in
# collection of boxing modules,
# e.g. ``mathics.box.boxes_operators.box_infix()``.
#
####################################################################


def box_infix(
    expr: Expression,
    operator: BaseElement,
    form: Symbol,
    evaluation: Evaluation,
    precedence_value: Optional[int] = 0,
    grouping: Optional[str] = None,
) -> Optional[Expression]:
    """Implements MakeBoxes[Infix[...]].
    This function kicks off boxing for Infix operators.

    Operators are processed to add spaces and to use the right encoding.
    """

    # FIXME: this should go into a some formatter.
    def format_operator(operator) -> Union[String, BaseElement]:
        """
        Format infix operator `operator`. To do this outside parameter form is used.
        Sometimes no changes are made and operator is returned unchanged.

        This function probably should be rewritten be more scalable across other forms
        and moved to a module that contiaing similar formatting routines.
        """
        if not isinstance(operator, String):
            return MakeBoxes(operator, form)

        op_str = operator.value

        # FIXME: performing a check using the operator symbol representation feels a bit
        # fragile. The operator name seems more straightforward and more robust.
        if form == SymbolInputForm and op_str in ["*", "^", " "]:
            return operator
        elif (
            form in (SymbolInputForm, SymbolOutputForm)
            and not op_str.startswith(" ")
            and not op_str.endswith(" ")
        ):
            # FIXME: Again, testing on specific forms is fragile and not scalable.
            op = String(" " + op_str + " ")
            return op
        return operator

    if isinstance(expr, Atom):
        evaluation.message("Infix", "normal", Integer1)
        return None

    elements = expr.elements
    if len(elements) > 1:
        if operator.has_form("List", len(elements) - 1):
            operator = [format_operator(op) for op in operator.elements]
            return box_infix_elements(
                elements, operator, precedence_value, grouping, form
            )
        else:
            encoding_rule = evaluation.definitions.get_ownvalue("$CharacterEncoding")
            encoding = "UTF8" if encoding_rule is None else encoding_rule.replace.value
            op_str = (
                operator.value if isinstance(operator, String) else operator.short_name
            )
            if encoding == "ASCII":
                operator = format_operator(
                    String(operator_to_ascii.get(op_str, op_str))
                )
            else:
                operator = format_operator(
                    String(operator_to_unicode.get(op_str, op_str))
                )

        return box_infix_elements(elements, operator, precedence_value, grouping, form)

    elif len(elements) == 1:
        return MakeBoxes(elements[0], form)
    else:
        return MakeBoxes(expr, form)


# FIXME: op should be a string, so remove the Union.
def box_infix_elements(
    elements, op: Union[String, list], precedence: int, grouping, form: Symbol
) -> Expression:
    result = []
    for index, element in enumerate(elements):
        if index > 0:
            if isinstance(op, list):
                result.append(op[index - 1])
            else:
                result.append(op)
        parenthesized = False
        if grouping == "System`NonAssociative":
            parenthesized = True
        elif grouping == "System`Left" and index > 0:
            parenthesized = True
        elif grouping == "System`Right" and index == 0:
            parenthesized = True

        element_boxes = Expression(SymbolMakeBoxes, element, form)
        element = parenthesize(precedence, element, element_boxes, parenthesized)

        result.append(element)
    return Expression(SymbolRowBox, ListExpression(*result))


####################################################################
# End of section of code that might be in mathics.box.
####################################################################


class Center(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Center.html</url>

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
    """

    options = GridBox.options
    summary_text = " 2D layout containing arbitrary objects"

    def eval_makeboxes(self, array, f, evaluation: Evaluation, options) -> Expression:
        """MakeBoxes[Grid[array_?MatrixQ, OptionsPattern[Grid]],
        f:StandardForm|TraditionalForm|OutputForm]"""
        return GridBox(
            ListExpression(
                *(
                    ListExpression(
                        *(format_element(item, evaluation, f) for item in row.elements),
                    )
                    for row in array.elements
                ),
            ),
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
        "argb": "Infix called with `1` arguments; between 1 and 4 arguments are expected.",
        "group": "Infix::group: Grouping specification `1` is not NonAssociative, None, Left, or Right.",
        "intm": "Machine-sized integer expected at position 3 in `1`",
        "normal": "Nonatomic expression expected at position `1`",
    }
    summary_text = "infix form"

    # the right rule should be
    # mbexpression:MakeBoxes[Infix[___], form]
    def eval_makeboxes(self, expression, form, evaluation: Evaluation):
        """MakeBoxes[Infix[___],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""
        infix_expr = expression.elements[0]
        elements = list(infix_expr.elements)
        num_parms = len(elements)

        if num_parms == 0 or num_parms > 4:
            evaluation.message("Infix", "argb", Integer(num_parms))
            return eval_fullform_makeboxes(infix_expr, evaluation, form)

        if num_parms == 1:
            expr = elements[0]
            return box_infix(expr, String("~"), form, evaluation)
        if num_parms == 2:
            expr, operator = elements
            return box_infix(expr, operator, form, evaluation)

        expr, operator, precedence = elements[:3]
        if not isinstance(precedence, Integer):
            evaluation.message(
                "Infix",
                "intm",
                Expression(SymbolFullForm, infix_expr),
            )
            return eval_fullform_makeboxes(infix_expr, evaluation, form)

        grouping = SymbolNone if num_parms < 4 else elements[3]
        if grouping is SymbolNone:
            return box_infix(expr, operator, form, evaluation, precedence.value)
        if grouping in (SymbolNonAssociative, SymbolLeft, SymbolRight):
            return box_infix(
                expr, operator, form, evaluation, precedence.value, grouping.get_name()
            )

        evaluation.message("Infix", "argb", grouping)
        return eval_fullform_makeboxes(infix_expr, evaluation, form)


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
          <dd>is used with operator formatting constructs to specify a \
          non-associative operator.
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
      <dd>is used with operator formatting constructs to specify a \
          right-associative operator.
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
    <url>:WMA link:https://reference.wolfram.com/language/ref/Subscript.html</url>

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
