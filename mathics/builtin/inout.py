# -*- coding: utf-8 -*-

"""
Input and Output
"""

import re

import typing
from typing import Any, Optional


from mathics.builtin.base import (
    Builtin,
    BinaryOperator,
    Operator,
    Predefined,
)
from mathics.builtin.box.inout import GridBox, RowBox, to_boxes
from mathics.builtin.comparison import expr_min
from mathics.builtin.lists import list_boxes
from mathics.builtin.makeboxes import MakeBoxes
from mathics.builtin.options import options_to_rules
from mathics.builtin.tensors import get_dimensions

from mathics.core.atoms import (
    Integer,
    Real,
    String,
    StringFromPython,
)

from mathics.core.attributes import (
    hold_all as A_HOLD_ALL,
    hold_first as A_HOLD_FIRST,
    protected as A_PROTECTED,
)
from mathics.core.element import EvalMixin
from mathics.core.expression import Expression, BoxError
from mathics.core.evaluation import Message as EvaluationMessage
from mathics.core.formatter import _BoxedString
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolFullForm,
    SymbolList,
    SymbolNull,
)

from mathics.core.systemsymbols import (
    SymbolMakeBoxes,
    SymbolMessageName,
    SymbolQuiet,
    SymbolRow,
    SymbolRowBox,
    SymbolRule,
)

MULTI_NEWLINE_RE = re.compile(r"\n{2,}")

SymbolNumberForm = Symbol("System`NumberForm")
SymbolSuperscriptBox = Symbol("System`SuperscriptBox")
SymbolSubscriptBox = Symbol("System`SubscriptBox")


class BoxData(Builtin):
    """
    <dl>
    <dt>'BoxData[...]'
        <dd>is a low-level representation of the contents of a typesetting
    cell.
    </dl>
    """

    summary_text = "low-level representation of the contents of a typesetting cell"


class TextData(Builtin):
    """
    <dl>
    <dt>'TextData[...]'
        <dd>is a low-level representation of the contents of a textual
    cell.
    </dl>
    """

    summary_text = "low-level representation of the contents of a textual cell."


class Row(Builtin):
    """
    <dl>
    <dt>'Row[{$expr$, ...}]'
        <dd>formats several expressions inside a 'RowBox'.
    </dl>
    """

    summary_text = "1D layouts containing arbitrary objects in a row"

    def apply_makeboxes(self, items, sep, f, evaluation):
        """MakeBoxes[Row[{items___}, sep_:""],
        f:StandardForm|TraditionalForm|OutputForm]"""

        items = items.get_sequence()
        if not isinstance(sep, String):
            sep = MakeBoxes(sep, f)
        if len(items) == 1:
            return MakeBoxes(items[0], f)
        else:
            result = []
            for index, item in enumerate(items):
                if index > 0 and not sep.sameQ(String("")):
                    result.append(to_boxes(sep, evaluation))
                item = MakeBoxes(item, f).evaluate(evaluation)
                item = to_boxes(item, evaluation)
                result.append(item)
            return RowBox(*result)


class Grid(Builtin):
    """
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

    def apply_makeboxes(self, array, f, evaluation, options) -> Expression:
        """MakeBoxes[Grid[array_?MatrixQ, OptionsPattern[Grid]],
        f:StandardForm|TraditionalForm|OutputForm]"""
        return GridBox(
            ListExpression(
                *(
                    ListExpression(
                        *(
                            Expression(SymbolMakeBoxes, item, f)
                            for item in row.elements
                        ),
                    )
                    for row in array.elements
                ),
            ),
            *options_to_rules(options),
        )


SymbolTableDepth = Symbol("TableDepth")


class TableForm(Builtin):
    """
    <dl>
    <dt>'TableForm[$expr$]'
        <dd>displays $expr$ as a table.
    </dl>

    >> TableForm[Array[a, {3,2}],TableDepth->1]
     = {a[1, 1], a[1, 2]}
     .
     . {a[2, 1], a[2, 2]}
     .
     . {a[3, 1], a[3, 2]}

    A table of Graphics:
    >> Table[Style[Graphics[{EdgeForm[{Black}], RGBColor[r,g,b], Rectangle[]}], ImageSizeMultipliers->{0.2, 1}], {r,0,1,1/2}, {g,0,1,1/2}, {b,0,1,1/2}] // TableForm
     = -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-

    #> TableForm[{}]
     = #<--#
    """

    options = {"TableDepth": "Infinity"}
    summary_text = "format as a table"

    def apply_makeboxes(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm|OutputForm]"""

        dims = len(get_dimensions(table, head=SymbolList))
        depth = self.get_option(options, "TableDepth", evaluation)
        depth = expr_min((Integer(dims), depth))
        depth = depth.value
        if depth is None:
            evaluation.message(self.get_name(), "int")
            return

        if depth <= 0:
            return Expression(SymbolMakeBoxes, table, f)
        elif depth == 1:
            return GridBox(
                ListExpression(
                    *(
                        ListExpression(Expression(SymbolMakeBoxes, item, f))
                        for item in table.elements
                    ),
                )
            )
            # return Expression(
            #    'GridBox', Expression('List', *(
            #        Expression('List', Expression('MakeBoxes', item, f))
            #        for item in table.elements)))
        else:
            new_depth = Expression(SymbolRule, SymbolTableDepth, Integer(depth - 2))

            def transform_item(item):
                if depth > 2:
                    return Expression(Symbol(self.get_name()), item, new_depth)
                else:
                    return item

            return GridBox(
                ListExpression(
                    *(
                        ListExpression(
                            *(
                                Expression(SymbolMakeBoxes, transform_item(item), f)
                                for item in row.elements
                            ),
                        )
                        for row in table.elements
                    ),
                )
            )


class MatrixForm(TableForm):
    """
    <dl>
    <dt>'MatrixForm[$m$]'
        <dd>displays a matrix $m$, hiding the underlying list
        structure.
    </dl>

    >> Array[a,{4,3}]//MatrixForm
     = a[1, 1]   a[1, 2]   a[1, 3]
     .
     . a[2, 1]   a[2, 2]   a[2, 3]
     .
     . a[3, 1]   a[3, 2]   a[3, 3]
     .
     . a[4, 1]   a[4, 2]   a[4, 3]

    ## Issue #182
    #> {{2*a, 0},{0,0}}//MatrixForm
     = 2 a   0
     .
     . 0     0
    """

    summary_text = "format as a matrix"

    def apply_makeboxes_matrix(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm]"""

        result = super(MatrixForm, self).apply_makeboxes(table, f, evaluation, options)
        if result.get_head_name() == "System`GridBox":
            return Expression(
                SymbolRowBox, ListExpression(String("("), result, String(")"))
            )
        return result


class Superscript(Builtin):
    """
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


class Subscript(Builtin):
    """
    <dl>
    <dt>'Subscript[$a$, $i$]'
        <dd>displays as $a_i$.
    </dl>

    >> Subscript[x,1,2,3] // TeXForm
     = x_{1,2,3}
    """

    summary_text = "format an expression with a subscript"

    def apply_makeboxes(self, x, y, f, evaluation) -> Expression:
        "MakeBoxes[Subscript[x_, y__], f:StandardForm|TraditionalForm]"

        y = y.get_sequence()
        return Expression(
            SymbolSubscriptBox,
            Expression(SymbolMakeBoxes, x, f),
            *list_boxes(y, f, evaluation),
        )


class Subsuperscript(Builtin):
    """
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


class Postfix(BinaryOperator):
    """
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


class Prefix(BinaryOperator):
    """
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


class Infix(Builtin):
    """
    <dl>
    <dt>'Infix[$expr$, $oper$, $prec$, $assoc$]'
        <dd>displays $expr$ with the infix operator $oper$, with
        precedence $prec$ and associativity $assoc$.
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


class NonAssociative(Builtin):
    """
    <dl>
    <dt>'NonAssociative'
        <dd>is used with operator formatting constructs to specify a
        non-associative operator.
    </dl>
    """

    summary_text = "non-associative operator"


class Left(Builtin):
    """
    <dl>
    <dt>'Left'
        <dd>is used with operator formatting constructs to specify a
        left-associative operator.
    </dl>
    """

    summary_text = "left alignment/left associative"


class Right(Builtin):
    """
    <dl>
    <dt>'Right'
        <dd>is used with operator formatting constructs to specify a
        right-associative operator.
    </dl>
    """

    summary_text = "right alignment/right associative"


class Center(Builtin):
    """
    <dl>
    <dt>'Center'
        <dd>is used with the 'ColumnAlignments' option to 'Grid' or
        'TableForm' to specify a centered column.
    </dl>
    """

    summary_text = "center alignment"


class StringForm(Builtin):
    """
    <dl>
    <dt>'StringForm[$str$, $expr1$, $expr2$, ...]'
        <dd>displays the string $str$, replacing placeholders in $str$
        with the corresponding expressions.
    </dl>

    >> StringForm["`1` bla `2` blub `` bla `2`", a, b, c]
     = a bla b blub c bla b
    """

    summary_text = "make an string from a template and a list of parameters"

    def apply_makeboxes(self, s, args, f, evaluation):
        """MakeBoxes[StringForm[s_String, args___],
        f:StandardForm|TraditionalForm|OutputForm]"""

        s = s.value
        args = args.get_sequence()
        result = []
        pos = 0
        last_index = 0
        for match in re.finditer(r"(\`(\d*)\`)", s):
            start, end = match.span(1)
            if match.group(2):
                index = int(match.group(2))
            else:
                index = last_index + 1
            if index > last_index:
                last_index = index
            if start > pos:
                result.append(to_boxes(String(s[pos:start]), evaluation))
            pos = end
            if 1 <= index <= len(args):
                arg = args[index - 1]
                result.append(
                    to_boxes(MakeBoxes(arg, f).evaluate(evaluation), evaluation)
                )
        if pos < len(s):
            result.append(to_boxes(String(s[pos:]), evaluation))
        return RowBox(
            *tuple(
                r.evaluate(evaluation) if isinstance(r, EvalMixin) else r
                for r in result
            )
        )


class Message(Builtin):
    """
    <dl>
    <dt>'Message[$symbol$::$msg$, $expr1$, $expr2$, ...]'
        <dd>displays the specified message, replacing placeholders in
        the message text with the corresponding expressions.
    </dl>

    >> a::b = "Hello world!"
     = Hello world!
    >> Message[a::b]
     : Hello world!
    >> a::c := "Hello `1`, Mr 00`2`!"
    >> Message[a::c, "you", 3 + 4]
     : Hello you, Mr 007!
    """

    attributes = A_HOLD_FIRST | A_PROTECTED

    messages = {
        "name": "Message name `1` is not of the form symbol::name or symbol::name::language."
    }
    summary_text = "display a message"

    def apply(self, symbol, tag, params, evaluation):
        "Message[MessageName[symbol_Symbol, tag_String], params___]"

        params = params.get_sequence()
        evaluation.message(symbol.name, tag.value, *params)
        return SymbolNull


def check_message(expr) -> bool:
    "checks if an expression is a valid message"
    if expr.has_form("MessageName", 2):
        symbol, tag = expr.elements
        if symbol.get_name() and tag.get_string_value():
            return True
    return False


class Check(Builtin):
    """
    <dl>
    <dt>'Check[$expr$, $failexpr$]'
        <dd>evaluates $expr$, and returns the result, unless messages were generated, in which case it evaluates and $failexpr$ will be returned.
    <dt>'Check[$expr$, $failexpr$, {s1::t1,s2::t2,...}]'
        <dd>checks only for the specified messages.
    </dl>

    Return err when a message is generated:
    >> Check[1/0, err]
     : Infinite expression 1 / 0 encountered.
     = err

    #> Check[1^0, err]
     = 1

    Check only for specific messages:
    >> Check[Sin[0^0], err, Sin::argx]
     : Indeterminate expression 0 ^ 0 encountered.
     = Indeterminate

    >> Check[1/0, err, Power::infy]
     : Infinite expression 1 / 0 encountered.
     = err

    #> Check[1 + 2]
     : Check called with 1 argument; 2 or more arguments are expected.
     = Check[1 + 2]

    #> Check[1 + 2, err, 3 + 1]
     : Message name 3 + 1 is not of the form symbol::name or symbol::name::language.
     = Check[1 + 2, err, 3 + 1]

    #> Check[1 + 2, err, hello]
     : Message name hello is not of the form symbol::name or symbol::name::language.
     = Check[1 + 2, err, hello]

    #> Check[1/0, err, Compile::cpbool]
     : Infinite expression 1 / 0 encountered.
     = ComplexInfinity

    #> Check[{0^0, 1/0}, err]
     : Indeterminate expression 0 ^ 0 encountered.
     : Infinite expression 1 / 0 encountered.
     = err

    #> Check[0^0/0, err, Power::indet]
     : Indeterminate expression 0 ^ 0 encountered.
     : Infinite expression 1 / 0 encountered.
     = err

    #> Check[{0^0, 3/0}, err, Power::indet]
     : Indeterminate expression 0 ^ 0 encountered.
     : Infinite expression 1 / 0 encountered.
     = err

    #> Check[1 + 2, err, {a::b, 2 + 5}]
     : Message name 2 + 5 is not of the form symbol::name or symbol::name::language.
     = Check[1 + 2, err, {a::b, 2 + 5}]

    #> Off[Power::infy]
    #> Check[1 / 0, err]
     = ComplexInfinity

    #> On[Power::infy]
    #> Check[1 / 0, err]
     : Infinite expression 1 / 0 encountered.
     = err
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "argmu": "Check called with 1 argument; 2 or more arguments are expected.",
        "name": "Message name `1` is not of the form symbol::name or symbol::name::language.",
    }
    summary_text = "discard the result if the evaluation produced messages"

    def apply_1_argument(self, expr, evaluation):
        "Check[expr_]"
        return evaluation.message("Check", "argmu")

    def apply(self, expr, failexpr, params, evaluation):
        "Check[expr_, failexpr_, params___]"

        # Todo: To implement the third form of this function , we need to implement the function $MessageGroups first
        # <dt>'Check[$expr$, $failexpr$, "name"]'
        # <dd>checks only for messages in the named message group.

        def get_msg_list(exprs):
            messages = []
            for expr in exprs:
                if expr.has_form("List", None):
                    messages.extend(get_msg_list(expr.elements))
                elif check_message(expr):
                    messages.append(expr)
                else:
                    raise Exception(expr)
            return messages

        check_messages = set(evaluation.get_quiet_messages())
        display_fail_expr = False

        params = params.get_sequence()
        if len(params) == 0:
            result = expr.evaluate(evaluation)
            if len(evaluation.out):
                display_fail_expr = True
        else:
            try:
                msgs = get_msg_list(params)
                for x in msgs:
                    check_messages.add(x)
            except Exception as inst:
                evaluation.message("Check", "name", inst.args[0])
                return
            curr_msg = len(evaluation.out)
            result = expr.evaluate(evaluation)
            own_messages = evaluation.out[curr_msg:]
            for out_msg in own_messages:
                if type(out_msg) is not EvaluationMessage:
                    continue
                pattern = Expression(
                    SymbolMessageName, Symbol(out_msg.symbol), String(out_msg.tag)
                )
                if pattern in check_messages:
                    display_fail_expr = True
                    break
        return failexpr if display_fail_expr is True else result


class Quiet(Builtin):
    """
    <dl>
    <dt>'Quiet[$expr$, {$s1$::$t1$, ...}]'
        <dd>evaluates $expr$, without messages '{$s1$::$t1$, ...}' being displayed.
    <dt>'Quiet[$expr$, All]'
        <dd>evaluates $expr$, without any messages being displayed.
    <dt>'Quiet[$expr$, None]'
        <dd>evaluates $expr$, without all messages being displayed.
    <dt>'Quiet[$expr$, $off$, $on$]'
        <dd>evaluates $expr$, with messages $off$ being suppressed, but messages $on$ being displayed.
    </dl>

    Evaluate without generating messages:
    >> Quiet[1/0]
     = ComplexInfinity

    Same as above:
    >> Quiet[1/0, All]
     = ComplexInfinity

    >> a::b = "Hello";
    >> Quiet[x+x, {a::b}]
     = 2 x

    >> Quiet[Message[a::b]; x+x, {a::b}]
     = 2 x

    >> Message[a::b]; y=Quiet[Message[a::b]; x+x, {a::b}]; Message[a::b]; y
     : Hello
     : Hello
     = 2 x

    #> Quiet[expr, All, All]
     : Arguments 2 and 3 of Quiet[expr, All, All] should not both be All.
     = Quiet[expr, All, All]
    >> Quiet[x + x, {a::b}, {a::b}]
     : In Quiet[x + x, {a::b}, {a::b}] the message name(s) {a::b} appear in both the list of messages to switch off and the list of messages to switch on.
     = Quiet[x + x, {a::b}, {a::b}]
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "anmlist": (
            "Argument `1` of `2` should be All, None, a message name, "
            "or a list of message names."
        ),
        "allall": "Arguments 2 and 3 of `1` should not both be All.",
        "conflict": (
            "In `1` the message name(s) `2` appear in both the list of "
            "messages to switch off and the list of messages to switch on."
        ),
    }

    rules = {
        "Quiet[expr_]": "Quiet[expr, All]",
        "Quiet[expr_, moff_]": "Quiet[expr, moff, None]",
    }
    summary_text = "evaluate without showing messages"

    def apply(self, expr, moff, mon, evaluation):
        "Quiet[expr_, moff_, mon_]"

        def get_msg_list(expr):
            if check_message(expr):
                expr = ListExpression(expr)
            if expr.get_name() == "System`All":
                all = True
                messages = []
            elif expr.get_name() == "System`None":
                all = False
                messages = []
            elif expr.has_form("List", None):
                all = False
                messages = []
                for item in expr.elements:
                    if check_message(item):
                        messages.append(item)
                    else:
                        raise ValueError
            else:
                raise ValueError
            return all, messages

        old_quiet_all = evaluation.quiet_all
        old_quiet_messages = set(evaluation.get_quiet_messages())
        quiet_messages = old_quiet_messages.copy()
        try:
            quiet_expr = Expression(SymbolQuiet, expr, moff, mon)
            try:
                off_all, off_messages = get_msg_list(moff)
            except ValueError:
                evaluation.message("Quiet", "anmlist", 2, quiet_expr)
                return
            try:
                on_all, on_messages = get_msg_list(mon)
            except ValueError:
                evaluation.message("Quiet", "anmlist", 2, quiet_expr)
                return
            if off_all and on_all:
                evaluation.message("Quiet", "allall", quiet_expr)
                return
            evaluation.quiet_all = off_all
            conflict = []
            for off in off_messages:
                if off in on_messages:
                    conflict.append(off)
                    break
            if conflict:
                evaluation.message(
                    "Quiet", "conflict", quiet_expr, ListExpression(*conflict)
                )
                return
            for off in off_messages:
                quiet_messages.add(off)
            for on in on_messages:
                quiet_messages.discard(on)
            if on_all:
                quiet_messages = set()
            evaluation.set_quiet_messages(quiet_messages)

            return expr.evaluate(evaluation)
        finally:
            evaluation.quiet_all = old_quiet_all
            evaluation.set_quiet_messages(old_quiet_messages)


class Off(Builtin):
    """
    <dl>
    <dt>'Off[$symbol$::$tag$]'
        <dd>turns a message off so it is no longer printed.
    </dl>

    >> Off[Power::infy]
    >> 1 / 0
     = ComplexInfinity

    >> Off[Power::indet, Syntax::com]
    >> {0 ^ 0,}
     = {Indeterminate, Null}

    #> Off[1]
     :  Message name 1 is not of the form symbol::name or symbol::name::language.
    #> Off[Message::name, 1]

    #> On[Power::infy, Power::indet, Syntax::com]
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "turn off a message for printing"

    def apply(self, expr, evaluation):
        "Off[expr___]"

        seq = expr.get_sequence()
        quiet_messages = set(evaluation.get_quiet_messages())

        if not seq:
            # TODO Off[s::trace] for all symbols
            return

        for e in seq:
            if isinstance(e, Symbol):
                quiet_messages.add(Expression(SymbolMessageName, e, String("trace")))
            elif check_message(e):
                quiet_messages.add(e)
            else:
                evaluation.message("Message", "name", e)
            evaluation.set_quiet_messages(quiet_messages)

        return SymbolNull


class On(Builtin):
    """
    <dl>
    <dt>'On[$symbol$::$tag$]'
        <dd>turns a message on for printing.
    </dl>

    >> Off[Power::infy]
    >> 1 / 0
     = ComplexInfinity
    >> On[Power::infy]
    >> 1 / 0
     : Infinite expression 1 / 0 encountered.
     = ComplexInfinity
    """

    # TODO
    """
    #> On[f::x]
     : Message f::x not found.
    """
    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "turn on a message for printing"

    def apply(self, expr, evaluation):
        "On[expr___]"

        seq = expr.get_sequence()
        quiet_messages = set(evaluation.get_quiet_messages())

        if not seq:
            # TODO On[s::trace] for all symbols
            return

        for e in seq:
            if isinstance(e, Symbol):
                quiet_messages.discard(
                    Expression(SymbolMessageName, e, String("trace"))
                )
            elif check_message(e):
                quiet_messages.discard(e)
            else:
                evaluation.message("Message", "name", e)
            evaluation.set_quiet_messages(quiet_messages)
        return SymbolNull


class MessageName(BinaryOperator):
    """
    <dl>
    <dt>'MessageName[$symbol$, $tag$]'
    <dt>'$symbol$::$tag$'
        <dd>identifies a message.
    </dl>

    'MessageName' is the head of message IDs of the form 'symbol::tag'.
    >> FullForm[a::b]
     = MessageName[a, "b"]

    The second parameter 'tag' is interpreted as a string.
    >> FullForm[a::"b"]
     = MessageName[a, "b"]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    default_formats = False
    formats: typing.Dict[str, Any] = {}
    messages = {"messg": "Message cannot be set to `1`. It must be set to a string."}
    summary_text = "message identifyier"
    operator = "::"
    precedence = 750
    rules = {
        "MakeBoxes[MessageName[symbol_Symbol, tag_String], "
        "f:StandardForm|TraditionalForm|OutputForm]": (
            'RowBox[{MakeBoxes[symbol, f], "::", MakeBoxes[tag, f]}]'
        ),
        "MakeBoxes[MessageName[symbol_Symbol, tag_String], InputForm]": (
            'RowBox[{MakeBoxes[symbol, InputForm], "::", tag}]'
        ),
    }

    def apply(self, symbol, tag, evaluation):
        "MessageName[symbol_Symbol, tag_String]"

        pattern = Expression(SymbolMessageName, symbol, tag)
        return evaluation.definitions.get_value(
            symbol.get_name(), "System`Messages", pattern, evaluation
        )


class Syntax(Builtin):
    r"""
    <dl>
    <dt>'Syntax'
        <dd>is a symbol to which all syntax messages are assigned.
    </dl>

    >> 1 +
     : Incomplete expression; more input is needed (line 1 of "<test>").

    >> Sin[1)
     : "Sin[1" cannot be followed by ")" (line 1 of "<test>").

    >> ^ 2
     : Expression cannot begin with "^ 2" (line 1 of "<test>").

    >> 1.5``
     : "1.5`" cannot be followed by "`" (line 1 of "<test>").

    #> (x]
     : "(x" cannot be followed by "]" (line 1 of "<test>").

    #> (x,)
     : "(x" cannot be followed by ",)" (line 1 of "<test>").

    #> {x]
     : "{x" cannot be followed by "]" (line 1 of "<test>").

    #> f[x)
     : "f[x" cannot be followed by ")" (line 1 of "<test>").

    #> a[[x)]
     : "a[[x" cannot be followed by ")]" (line 1 of "<test>").

    #> x /: y , z
     : "x /: y " cannot be followed by ", z" (line 1 of "<test>").

    #> a :: 1
     : "a :: " cannot be followed by "1" (line 1 of "<test>").

    #> a ? b ? c
     : "a ? b " cannot be followed by "? c" (line 1 of "<test>").

    #> \:000G
     : 4 hexadecimal digits are required after \: to construct a 16-bit character (line 1 of "<test>").
     : Expression cannot begin with "\:000G" (line 1 of "<test>").

    #> \:000
     : 4 hexadecimal digits are required after \: to construct a 16-bit character (line 1 of "<test>").
     : Expression cannot begin with "\:000" (line 1 of "<test>").

    #> \009
     : 3 octal digits are required after \ to construct an 8-bit character (line 1 of "<test>").
     : Expression cannot begin with "\009" (line 1 of "<test>").

    #> \00
     : 3 octal digits are required after \ to construct an 8-bit character (line 1 of "<test>").
     : Expression cannot begin with "\00" (line 1 of "<test>").

    #> \.0G
     : 2 hexadecimal digits are required after \. to construct an 8-bit character (line 1 of "<test>").
     : Expression cannot begin with "\.0G" (line 1 of "<test>").

    #> \.0
     : 2 hexadecimal digits are required after \. to construct an 8-bit character (line 1 of "<test>").
     : Expression cannot begin with "\.0" (line 1 of "<test>").

    #> "abc \[fake]"
     : Unknown unicode longname "fake" (line 1 of "<test>").
     = abc \[fake]

    #> a ~ b + c
     : "a ~ b " cannot be followed by "+ c" (line 1 of "<test>").

    #> {1,}
     : Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "<test>").
     = {1, Null}
    #> {, 1}
     : Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "<test>").
     = {Null, 1}
    #> {,,}
     : Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "<test>").
     : Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "<test>").
     : Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "<test>").
     = {Null, Null, Null}
    """

    # Extension: MMA does not provide lineno and filename in its error messages
    messages = {
        "snthex": r"4 hexadecimal digits are required after \: to construct a 16-bit character (line `4` of `5`).",
        "sntoct1": r"3 octal digits are required after \ to construct an 8-bit character (line `4` of `5`).",
        "sntoct2": r"2 hexadecimal digits are required after \. to construct an 8-bit character (line `4` of `5`).",
        "sntxi": "Incomplete expression; more input is needed (line `4` of `5`).",
        "sntxb": "Expression cannot begin with `1` (line `4` of `5`).",
        "sntxf": "`1` cannot be followed by `2` (line `4` of `5`).",
        "bktwrn": "`1` represents multiplication; use `2` to represent a function (line `4` of `5`).",  # TODO
        "bktmch": "`1` must be followed by `2`, not `3` (line `4` of `5`).",
        "sntue": "Unexpected end of file; probably unfinished expression (line `4` of `5`).",
        "sntufn": "Unknown unicode longname `1` (line `4` of `5`).",
        "com": "Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line `4` of `5`).",
    }
    summary_text = "syntax messages"


class General(Builtin):
    """
    <dl>
    <dt>'General'
        <dd>is a symbol to which all general-purpose messages are assigned.
    </dl>

    >> General::argr
     = `1` called with 1 argument; `2` arguments are expected.
    >> Message[Rule::argr, Rule, 2]
     : Rule called with 1 argument; 2 arguments are expected.
    """

    messages = {
        "argb": (
            "`1` called with `2` arguments; "
            "between `3` and `4` arguments are expected."
        ),
        "argct": "`1` called with `2` arguments.",
        "argctu": "`1` called with 1 argument.",
        "argr": "`1` called with 1 argument; `2` arguments are expected.",
        "argrx": "`1` called with `2` arguments; `3` arguments are expected.",
        "argx": "`1` called with `2` arguments; 1 argument is expected.",
        "argt": (
            "`1` called with `2` arguments; " "`3` or `4` arguments are expected."
        ),
        "argtu": ("`1` called with 1 argument; `2` or `3` arguments are expected."),
        "base": "Requested base `1` in `2` should be between 2 and `3`.",
        "boxfmt": "`1` is not a box formatting type.",
        "color": "`1` is not a valid color or gray-level specification.",
        "cxt": "`1` is not a valid context name.",
        "divz": "The argument `1` should be nonzero.",
        "digit": "Digit at position `1` in `2` is too large to be used in base `3`.",
        "exact": "Argument `1` is not an exact number.",
        "fnsym": (
            "First argument in `1` is not a symbol " "or a string naming a symbol."
        ),
        "heads": "Heads `1` and `2` are expected to be the same.",
        "ilsnn": (
            "Single or list of non-negative integers expected at " "position `1`."
        ),
        "indet": "Indeterminate expression `1` encountered.",
        "innf": "Non-negative integer or Infinity expected at position `1`.",
        "int": "Integer expected.",
        "intp": "Positive integer expected.",
        "intnn": "Non-negative integer expected.",
        "iterb": "Iterator does not have appropriate bounds.",
        "ivar": "`1` is not a valid variable.",
        "level": ("Level specification `1` is not of the form n, " "{n}, or {m, n}."),
        "locked": "Symbol `1` is locked.",
        "matsq": "Argument `1` is not a non-empty square matrix.",
        "newpkg": "In WL, there is a new package for this.",
        "noopen": "Cannot open `1`.",
        "nord": "Invalid comparison with `1` attempted.",
        "normal": "Nonatomic expression expected.",
        "noval": ("Symbol `1` in part assignment does not have an immediate value."),
        "obspkg": "In WL, this package is obsolete.",
        "openx": "`1` is not open.",
        "optb": "Optional object `1` in `2` is not a single blank.",
        "ovfl": "Overflow occurred in computation.",
        "partd": "Part specification is longer than depth of object.",
        "partw": "Part `1` of `2` does not exist.",
        "plld": "Endpoints in `1` must be distinct machine-size real numbers.",
        "plln": "Limiting value `1` in `2` is not a machine-size real number.",
        "pspec": (
            "Part specification `1` is neither an integer nor " "a list of integer."
        ),
        "seqs": "Sequence specification expected, but got `1`.",
        "setp": "Part assignment to `1` could not be made",
        "setps": "`1` in the part assignment is not a symbol.",
        "span": "`1` is not a valid Span specification.",
        "stream": "`1` is not string, InputStream[], or OutputStream[]",
        "string": "String expected.",
        "sym": "Argument `1` at position `2` is expected to be a symbol.",
        "tag": "Rule for `1` can only be attached to `2`.",
        "take": "Cannot take positions `1` through `2` in `3`.",
        "vrule": (
            "Cannot set `1` to `2`, " "which is not a valid list of replacement rules."
        ),
        "write": "Tag `1` in `2` is Protected.",
        "wrsym": "Symbol `1` is Protected.",
        "ucdec": "An invalid unicode sequence was encountered and ignored.",
        "charcode": "The character encoding `1` is not supported. Use $CharacterEncodings to list supported encodings.",
        # Self-defined messages
        # 'rep': "`1` is not a valid replacement rule.",
        "options": "`1` is not a valid list of option rules.",
        "timeout": "Timeout reached.",
        "syntax": "`1`",
        "invalidargs": "Invalid arguments.",
        "notboxes": "`1` is not a valid box structure.",
        "pyimport": '`1`[] is not available. Python module "`2`" is not installed.',
    }
    summary_text = "general-purpose messages"


class Echo_(Predefined):
    """
    <dl>
    <dt>'$Echo'
        <dd>gives a list of files and pipes to which all input is echoed.

    </dl>
    """

    attributes = 0
    name = "$Echo"
    rules = {"$Echo": "{}"}
    summary_text = "files and pipes that echoes the input"


class Print(Builtin):
    """
    <dl>
    <dt>'Print[$expr$, ...]'
        <dd>prints each $expr$ in string form.
    </dl>

    >> Print["Hello world!"]
     | Hello world!
    >> Print["The answer is ", 7 * 6, "."]
     | The answer is 42.

    #> Print["-Hola\\n-Qué tal?"]
     | -Hola
     . -Qué tal?
    """

    summary_text = "print strings and formatted text"

    def apply(self, expr, evaluation):
        "Print[expr__]"

        expr = expr.get_sequence()
        expr = Expression(SymbolRow, ListExpression(*expr))
        evaluation.print_out(expr)
        return SymbolNull


class FullForm(Builtin):
    """
    <dl>
    <dt>'FullForm[$expr$]'
        <dd>displays the underlying form of $expr$.
    </dl>

    >> FullForm[a + b * c]
     = Plus[a, Times[b, c]]
    >> FullForm[2/3]
     = Rational[2, 3]
    >> FullForm["A string"]
     = "A string"
    """

    summary_text = "underlying M-Expression representation"


class StandardForm(Builtin):
    """
    <dl>
    <dt>'StandardForm[$expr$]'
        <dd>displays $expr$ in the default form.
    </dl>

    >> StandardForm[a + b * c]
     = a + b c
    >> StandardForm["A string"]
     = A string
    'StandardForm' is used by default:
    >> "A string"
     = A string
    >> f'[x]
     = f'[x]
    """

    summary_text = "default output format"


class TraditionalForm(Builtin):
    """
    <dl>
    <dt>'TraditionalForm[$expr$]'
        <dd>displays $expr$ in a format similar to the traditional mathematical notation, where
           function evaluations are represented by brackets instead of square brackets.
    </dl>

    ## To pass this test, we need to improve the implementation of Element.format
    ## >> TraditionalForm[g[x]]
    ## = g(x)
    """

    summary_text = "traditional output format"


class InputForm(Builtin):
    r"""
    <dl>
    <dt>'InputForm[$expr$]'
        <dd>displays $expr$ in an unambiguous form suitable for input.
    </dl>

    >> InputForm[a + b * c]
     = a + b*c
    >> InputForm["A string"]
     = "A string"
    >> InputForm[f'[x]]
     = Derivative[1][f][x]
    >> InputForm[Derivative[1, 0][f][x]]
     = Derivative[1, 0][f][x]
    #> InputForm[2 x ^ 2 + 4z!]
     = 2*x^2 + 4*z!
    #> InputForm["\$"]
     = "\\$"
    """
    summary_text = "plain-text input format"


class OutputForm(Builtin):
    """
    <dl>
    <dt>'OutputForm[$expr$]'
        <dd>displays $expr$ in a plain-text form.
    </dl>

    >> OutputForm[f'[x]]
     = f'[x]
    >> OutputForm[Derivative[1, 0][f][x]]
     = Derivative[1, 0][f][x]
    >> OutputForm["A string"]
     = A string
    >> OutputForm[Graphics[Rectangle[]]]
     = -Graphics-
    """

    summary_text = "plain-text output format"


class MathMLForm(Builtin):
    """
    <dl>
    <dt>'MathMLForm[$expr$]'
        <dd>displays $expr$ as a MathML expression.
    </dl>

    >> MathMLForm[HoldForm[Sqrt[a^3]]]
     = ...

    ## Test cases for Unicode - redo please as a real test
    >> MathMLForm[\\[Mu]]
    = ...

    # This can causes the TeX to fail
    # >> MathMLForm[Graphics[Text["\u03bc"]]]
    #  = ...

    ## The <mo> should contain U+2062 INVISIBLE TIMES
    ## MathMLForm[MatrixForm[{{2*a, 0},{0,0}}]]
    = ...
    """

    summary_text = "formatted expression as MathML commands"

    def apply_mathml(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, MathMLForm]"

        boxes = MakeBoxes(expr).evaluate(evaluation)
        try:
            mathml = boxes.boxes_to_mathml(evaluation=evaluation)
        except BoxError:
            evaluation.message(
                "General",
                "notboxes",
                Expression(SymbolFullForm, boxes).evaluate(evaluation),
            )
            mathml = ""
        is_a_picture = mathml[:6] == "<mtext"

        # mathml = '<math><mstyle displaystyle="true">%s</mstyle></math>' % mathml
        # #convert_box(boxes)
        query = evaluation.parse("Settings`$UseSansSerif")
        usesansserif = query.evaluate(evaluation).to_python()
        if not is_a_picture:
            if isinstance(usesansserif, bool) and usesansserif:
                mathml = '<mstyle mathvariant="sans-serif">%s</mstyle>' % mathml

        mathml = '<math display="block">%s</math>' % mathml  # convert_box(boxes)
        return Expression(SymbolRowBox, ListExpression(String(mathml)))


class PythonForm(Builtin):
    """
    <dl>
      <dt>'PythonForm[$expr$]'
      <dd>returns an approximate equivalent of $expr$ in Python, when that is possible. We assume
      that Python has SymPy imported. No explicit import will be include in the result.
    </dl>

    >> PythonForm[Infinity]
    = math.inf
    >> PythonForm[Pi]
    = sympy.pi
    >> E // PythonForm
    = sympy.E
    >> {1, 2, 3} // PythonForm
    = [1, 2, 3]
    """

    summary_text = "translate expressions as Python source code"
    # >> PythonForm[HoldForm[Sqrt[a^3]]]
    #  = sympy.sqrt{a**3} # or something like this

    def apply_python(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, PythonForm]"

        try:
            # from trepan.api import debug; debug()
            python_equivalent = expr.to_python(python_form=True)
        except Exception:
            return
        return StringFromPython(python_equivalent)

    def apply(self, expr, evaluation) -> Expression:
        "PythonForm[expr_]"
        return self.apply_python(expr, evaluation)


class SympyForm(Builtin):
    """
    <dl>
      <dt>'SympyForm[$expr$]'
      <dd>returns an Sympy $expr$ in Python. Sympy is used internally
      to implement a number of Mathics functions, like Simplify.
    </dl>

    >> SympyForm[Pi^2]
    = pi**2
    >> E^2 + 3E // SympyForm
    = exp(2) + 3*E
    """

    summary_text = "translate expressions to SymPy"

    def apply_sympy(self, expr, evaluation) -> Optional[Expression]:
        "MakeBoxes[expr_, SympyForm]"

        try:
            sympy_equivalent = expr.to_sympy()
        except Exception:
            return
        return StringFromPython(sympy_equivalent)

    def apply(self, expr, evaluation) -> Expression:
        "SympyForm[expr_]"
        return self.apply_sympy(expr, evaluation)


class TeXForm(Builtin):
    r"""
    <dl>
    <dt>'TeXForm[$expr$]'
        <dd>displays $expr$ using TeX math mode commands.
    </dl>

    >> TeXForm[HoldForm[Sqrt[a^3]]]
     = \sqrt{a^3}

    #> {"hi","you"} //InputForm //TeXForm
     = \left\{\text{hi}, \text{you}\right\}

    #> TeXForm[a+b*c]
     = a+b c
    #> TeXForm[InputForm[a+b*c]]
     = a\text{ + }b*c
    """
    summary_text = "formatted expression as TeX commands"

    def apply_tex(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, TeXForm]"
        boxes = MakeBoxes(expr).evaluate(evaluation)
        if isinstance(boxes, String):
            boxes = _BoxedString(boxes.value)
        try:
            # Here we set ``show_string_characters`` to False, to reproduce
            # the standard behaviour in WMA. Remove this parameter to recover the
            # quotes in InputForm and FullForm
            tex = boxes.boxes_to_tex(
                show_string_characters=False, evaluation=evaluation
            )

            # Replace multiple newlines by a single one e.g. between asy-blocks
            tex = MULTI_NEWLINE_RE.sub("\n", tex)

            tex = tex.replace(" \uF74c", " \\, d")  # tmp hack for Integrate
        except BoxError:
            evaluation.message(
                "General",
                "notboxes",
                Expression(SymbolFullForm, boxes).evaluate(evaluation),
            )
            tex = ""
        return Expression(SymbolRowBox, ListExpression(String(tex)))


class Style(Builtin):
    """
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


class Precedence(Builtin):
    """
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

    def apply(self, expr, evaluation) -> Real:
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
