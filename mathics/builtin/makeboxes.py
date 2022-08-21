# -*- coding: utf-8 -*-


"""
Low level Format definitions 
"""

import mpmath


from mathics.builtin.base import Builtin, Predefined
from mathics.builtin.box.layout import _boxed_string, RowBox, to_boxes
from mathics.core.atoms import (
    Integer,
    Integer1,
    Real,
    PrecisionReal,
    MachineReal,
    String,
)

from mathics.core.attributes import (
    hold_all_complete as A_HOLD_ALL_COMPLETE,
    read_protected as A_READ_PROTECTED,
)
from mathics.core.element import BoxElementMixin
from mathics.core.expression import Expression
from mathics.core.formatter import format_element
from mathics.core.list import ListExpression
from mathics.core.number import (
    dps,
    convert_base,
    machine_precision,
    reconstruct_digits,
)
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolNull,
    SymbolTrue,
)

from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolInfinity,
    SymbolMakeBoxes,
    SymbolOutputForm,
    SymbolRowBox,
    SymbolRuleDelayed,
)


SymbolNumberForm = Symbol("System`NumberForm")
SymbolSuperscriptBox = Symbol("System`SuperscriptBox")
SymbolSubscriptBox = Symbol("System`SubscriptBox")


def parenthesize(precedence, element, element_boxes, when_equal):
    from mathics.builtin import builtins_precedence

    while element.has_form("HoldForm", 1):
        element = element.elements[0]

    if element.has_form(("Infix", "Prefix", "Postfix"), 3, None):
        element_prec = element.elements[2].value
    elif element.has_form("PrecedenceForm", 2):
        element_prec = element.elements[1].value
    # For negative values, ensure that the element_precedence is at least the precedence. (Fixes #332)
    elif isinstance(element, (Integer, Real)) and element.value < 0:
        element_prec = precedence
    else:
        element_prec = builtins_precedence.get(element.get_head_name())
    if precedence is not None and element_prec is not None:
        if precedence > element_prec or (precedence == element_prec and when_equal):
            return Expression(
                SymbolRowBox,
                ListExpression(String("("), element_boxes, String(")")),
            )
    return element_boxes


def make_boxes_infix(elements, ops, precedence, grouping, form):
    result = []
    for index, element in enumerate(elements):
        if index > 0:
            result.append(ops[index - 1])
        parenthesized = False
        if grouping == "System`NonAssociative":
            parenthesized = True
        elif grouping == "System`Left" and index > 0:
            parenthesized = True
        elif grouping == "System`Right" and index == 0:
            parenthesized = True

        element_boxes = MakeBoxes(element, form)
        element = parenthesize(precedence, element, element_boxes, parenthesized)

        result.append(element)
    return Expression(SymbolRowBox, ListExpression(*result))


def real_to_s_exp(expr, n):
    if expr.is_zero:
        s = "0"
        if expr.is_machine_precision():
            exp = 0
        else:
            p = expr.get_precision()
            exp = -dps(p)
        nonnegative = 1
    else:
        if n is None:
            if expr.is_machine_precision():
                value = expr.get_float_value()
                s = repr(value)
            else:
                with mpmath.workprec(expr.get_precision()):
                    value = expr.to_mpmath()
                    s = mpmath.nstr(value, dps(expr.get_precision()) + 1)
        else:
            with mpmath.workprec(expr.get_precision()):
                value = expr.to_mpmath()
                s = mpmath.nstr(value, n)

        # sign prefix
        if s[0] == "-":
            assert value < 0
            nonnegative = 0
            s = s[1:]
        else:
            assert value >= 0
            nonnegative = 1

        # exponent (exp is actual, pexp is printed)
        if "e" in s:
            s, exp = s.split("e")
            exp = int(exp)
            if len(s) > 1 and s[1] == ".":
                # str(float) doesn't always include '.' if 'e' is present.
                s = s[0] + s[2:].rstrip("0")
        else:
            exp = s.index(".") - 1
            s = s[: exp + 1] + s[exp + 2 :].rstrip("0")

            # consume leading '0's.
            i = 0
            while s[i] == "0":
                i += 1
                exp -= 1
            s = s[i:]

        # add trailing zeros for precision reals
        if n is not None and not expr.is_machine_precision() and len(s) < n:
            s = s + "0" * (n - len(s))
    return s, exp, nonnegative


def int_to_s_exp(expr, n):
    n = expr.get_int_value()
    if n < 0:
        nonnegative = 0
        s = str(-n)
    else:
        nonnegative = 1
        s = str(n)
    exp = len(s) - 1
    return s, exp, nonnegative


def number_form(expr, n, f, evaluation, options):
    """
    Converts a Real or Integer instance to Boxes.

    n digits of precision with f (can be None) digits after the decimal point.
    evaluation (can be None) is used for messages.

    The allowed options are python versions of the options permitted to
    NumberForm and must be supplied. See NumberForm or Real.make_boxes
    for correct option examples.
    """

    assert isinstance(n, int) and n > 0 or n is None
    assert f is None or (isinstance(f, int) and f >= 0)

    is_int = False
    if isinstance(expr, Integer):
        assert n is not None
        s, exp, nonnegative = int_to_s_exp(expr, n)
        if f is None:
            is_int = True
    elif isinstance(expr, Real):
        if n is not None:
            n = min(n, dps(expr.get_precision()) + 1)
        s, exp, nonnegative = real_to_s_exp(expr, n)
        if n is None:
            n = len(s)
    else:
        raise ValueError("Expected Real or Integer.")

    assert isinstance(n, int) and n > 0

    sign_prefix = options["NumberSigns"][nonnegative]

    # round exponent to ExponentStep
    rexp = (exp // options["ExponentStep"]) * options["ExponentStep"]

    if is_int:
        # integer never uses scientific notation
        pexp = ""
    else:
        method = options["ExponentFunction"]
        pexp = method(Integer(rexp)).get_int_value()
        if pexp is not None:
            exp -= pexp
            pexp = str(pexp)
        else:
            pexp = ""

    # pad right with '0'.
    if len(s) < exp + 1:
        if evaluation is not None:
            evaluation.message("NumberForm", "sigz")
        # TODO NumberPadding?
        s = s + "0" * (1 + exp - len(s))
    # pad left with '0'.
    if exp < 0:
        s = "0" * (-exp) + s
        exp = 0

    # left and right of NumberPoint
    left, right = s[: exp + 1], s[exp + 1 :]

    def _round(number, ndigits):
        """
        python round() for integers but with correct rounding.
        e.g. `_round(14225, -1)` is `14230` not `14220`.
        """
        assert isinstance(ndigits, int)
        assert ndigits < 0
        assert isinstance(number, int)
        assert number >= 0
        number += 5 * int(10 ** -(1 + ndigits))
        number //= int(10**-ndigits)
        return number

    # pad with NumberPadding
    if f is not None:
        if len(right) < f:
            # pad right
            right = right + (f - len(right)) * options["NumberPadding"][1]
        elif len(right) > f:
            # round right
            tmp = int(left + right)
            tmp = _round(tmp, f - len(right))
            tmp = str(tmp)
            left, right = tmp[: exp + 1], tmp[exp + 1 :]

    def split_string(s, start, step):
        if start > 0:
            yield s[:start]
        for i in range(start, len(s), step):
            yield s[i : i + step]

    # insert NumberSeparator
    digit_block = options["DigitBlock"]
    if digit_block[0] != 0:
        left = split_string(left, len(left) % digit_block[0], digit_block[0])
        left = options["NumberSeparator"][0].join(left)
    if digit_block[1] != 0:
        right = split_string(right, 0, digit_block[1])
        right = options["NumberSeparator"][1].join(right)

    left_padding = 0
    max_sign_len = max(len(options["NumberSigns"][0]), len(options["NumberSigns"][1]))
    i = len(sign_prefix) + len(left) + len(right) - max_sign_len
    if i < n:
        left_padding = n - i
    elif len(sign_prefix) < max_sign_len:
        left_padding = max_sign_len - len(sign_prefix)
    left_padding = left_padding * options["NumberPadding"][0]

    # insert NumberPoint
    if options["SignPadding"]:
        prefix = sign_prefix + left_padding
    else:
        prefix = left_padding + sign_prefix

    if is_int:
        s = prefix + left
    else:
        s = prefix + left + options["NumberPoint"] + right

    # base
    base = "10"

    # build number
    method = options["NumberFormat"]
    if options["_Form"] in ("System`InputForm", "System`FullForm"):
        return method(
            _boxed_string(s, number_as_text=True),
            _boxed_string(base, number_as_text=True),
            _boxed_string(pexp, number_as_text=True),
            options,
        )
    else:
        return method(String(s), String(base), String(pexp), options)


# TODO: Differently from the current implementation, MakeBoxes should only
# accept as its format field the symbols in `$BoxForms`. This is something to
# fix in a following step.


class BoxForms_(Predefined):
    """
    <dl>
      <dt>
      <dd>$BoxForms is the list of box formats.
    </dl>
    """

    attributes = A_READ_PROTECTED
    name = "$BoxForms"
    rules = {"$BoxForms": "{StandardForm, TraditionalForm}"}
    summary_text = "the list of box formats"


class MakeBoxes(Builtin):
    """
    <dl>
      <dt>'MakeBoxes[$expr$]'
      <dd>is a low-level formatting primitive that converts $expr$
        to box form, without evaluating it.
      <dt>'\\( ... \\)'
      <dd>directly inputs box objects.
    </dl>

    String representation of boxes
    >> \\(x \\^ 2\\)
     = SuperscriptBox[x, 2]

    >> \\(x \\_ 2\\)
     = SubscriptBox[x, 2]

    >> \\( a \\+ b \\% c\\)
     = UnderoverscriptBox[a, b, c]

    >> \\( a \\& b \\% c\\)
     = UnderoverscriptBox[a, c, b]

    #> \\( \\@ 5 \\)
     = SqrtBox[5]

    >> \\(x \\& y \\)
     = OverscriptBox[x, y]

    >> \\(x \\+ y \\)
     = UnderscriptBox[x, y]

    #> \\( x \\^ 2 \\_ 4 \\)
     = SuperscriptBox[x, SubscriptBox[2, 4]]

    ## Tests for issue 151 (infix operators in heads)
    #> (a + b)[x]
     = (a + b)[x]
    #> (a b)[x]
     = (a b)[x]
    #> (a <> b)[x]
     : String expected.
     = (a <> b)[x]
    """

    # TODO: Convert operators to appropriate representations e.g. 'Plus' to '+'
    """
    >> \\(a + b\\)
     = RowBox[{a, +, b}]

    >> \\(TraditionalForm \\` a + b\\)
     = FormBox[RowBox[{a, +, b}], TraditionalForm]

    >> \\(x \\/ \\(y + z\\)\\)
     =  FractionBox[x, RowBox[{y, +, z}]]
    """

    # TODO: Constructing boxes from Real
    """
    ## Test Real MakeBoxes
    #> MakeBoxes[1.4]
     = 1.4`
    #> MakeBoxes[1.4`]
     = 1.4`
    #> MakeBoxes[1.5`20]
     = 1.5`20.
    #> MakeBoxes[1.4`20]
     = 1.4`20.
    #> MakeBoxes[1.5``20]
     = 1.5`20.1760912591
    #> MakeBoxes[-1.4]
     = RowBox[{-, 1.4`}]
    #> MakeBoxes[34.*^3]
     = 34000.`

    #> MakeBoxes[0`]
     = 0.`
    #> MakeBoxes[0`3]
     = 0
    #> MakeBoxes[0``30]
     = 0.``30.
    #> MakeBoxes[0.`]
     = 0.`
    #> MakeBoxes[0.`3]
     = 0.`
    #> MakeBoxes[0.``30]
     = 0.``30.

    #> MakeBoxes[14]
     = 14
    #> MakeBoxes[-14]
     = RowBox[{-, 14}]
    """

    # TODO: Correct precedence
    """
    >> \\(x \\/ y + z\\)
     = RowBox[{FractionBox[x, y], +, z}]
    >> \\(x \\/ (y + z)\\)
     = FractionBox[x, RowBox[{(, RowBox[{y, +, z}], )}]]

    #> \\( \\@ a + b \\)
     = RowBox[{SqrtBox[a], +, b}]
    """

    # FIXME: Don't insert spaces with brackets
    """
    #> \\(c (1 + x)\\)
     = RowBox[{c, RowBox[{(, RowBox[{1, +, x}], )}]}]
    """

    # TODO: Required MakeExpression
    """
    #> \\!\\(x \\^ 2\\)
     = x ^ 2
    #> FullForm[%]
     = Power[x, 2]
    """

    # TODO: Fix Infix operators
    """
    >> MakeBoxes[1 + 1]
     = RowBox[{1, +, 1}]
    """

    # TODO: Parsing of special characters (like commas)
    """
    >> \\( a, b \\)
     = RowBox[{a, ,, b}]
    """
    attributes = A_HOLD_ALL_COMPLETE

    rules = {
        "MakeBoxes[Infix[head_[elements___]], "
        "    f:StandardForm|TraditionalForm|OutputForm|InputForm]": (
            'MakeBoxes[Infix[head[elements], StringForm["~`1`~", head]], f]'
        ),
        "MakeBoxes[expr_]": "MakeBoxes[expr, StandardForm]",
        "MakeBoxes[(form:StandardForm|TraditionalForm|OutputForm|TeXForm|"
        "MathMLForm)[expr_], StandardForm|TraditionalForm]": ("MakeBoxes[expr, form]"),
        "MakeBoxes[(form:StandardForm|OutputForm|MathMLForm|TeXForm)[expr_], OutputForm]": "MakeBoxes[expr, form]",
        "MakeBoxes[(form:FullForm|InputForm)[expr_], StandardForm|TraditionalForm|OutputForm]": "StyleBox[MakeBoxes[expr, form], ShowStringCharacters->True]",
        "MakeBoxes[PrecedenceForm[expr_, prec_], f_]": "MakeBoxes[expr, f]",
        "MakeBoxes[Style[expr_, OptionsPattern[Style]], f_]": (
            "StyleBox[MakeBoxes[expr, f], "
            "ImageSizeMultipliers -> OptionValue[ImageSizeMultipliers]]"
        ),
    }
    summary_text = "settable low-level translator from expression to display boxes"

    def apply_general(self, expr, f, evaluation):
        """MakeBoxes[expr_,
        f:TraditionalForm|StandardForm|OutputForm|InputForm|FullForm]"""
        if isinstance(expr, BoxElementMixin):
            expr = expr.to_expression()
        if isinstance(expr, Atom):
            return expr.atom_to_boxes(f, evaluation)
        else:
            head = expr.head
            elements = expr.elements

            f_name = f.get_name()
            if f_name == "System`TraditionalForm":
                left, right = "(", ")"
            else:
                left, right = "[", "]"

            # Parenthesize infix operators at the head of expressions,
            # like (a + b)[x], but not f[a] in f[a][b].
            #
            head_boxes = parenthesize(670, head, MakeBoxes(head, f), False)
            head_boxes = head_boxes.evaluate(evaluation)
            head_boxes = to_boxes(head_boxes, evaluation)
            result = [head_boxes, to_boxes(String(left), evaluation)]

            if len(elements) > 1:
                row = []
                if f_name in (
                    "System`InputForm",
                    "System`OutputForm",
                    "System`FullForm",
                ):
                    sep = ", "
                else:
                    sep = ","
                for index, element in enumerate(elements):
                    if index > 0:
                        row.append(to_boxes(String(sep), evaluation))
                    row.append(
                        to_boxes(MakeBoxes(element, f).evaluate(evaluation), evaluation)
                    )
                result.append(RowBox(*row))
            elif len(elements) == 1:
                result.append(
                    to_boxes(MakeBoxes(elements[0], f).evaluate(evaluation), evaluation)
                )
            result.append(to_boxes(String(right), evaluation))
            return RowBox(*result)

    def apply_outerprecedenceform(self, expr, prec, evaluation):
        """MakeBoxes[OuterPrecedenceForm[expr_, prec_],
        StandardForm|TraditionalForm|OutputForm|InputForm]"""

        precedence = prec.get_int_value()
        boxes = MakeBoxes(expr)
        return parenthesize(precedence, expr, boxes, True)

    def apply_postprefix(self, p, expr, h, prec, f, evaluation):
        """MakeBoxes[(p:Prefix|Postfix)[expr_, h_, prec_:None],
        f:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        if not isinstance(h, String):
            h = MakeBoxes(h, f)

        precedence = prec.get_int_value()

        elements = expr.elements
        if len(elements) == 1:
            element = elements[0]
            element_boxes = MakeBoxes(element, f)
            element = parenthesize(precedence, element, element_boxes, True)
            if p.get_name() == "System`Postfix":
                args = (element, h)
            else:
                args = (h, element)

            return Expression(SymbolRowBox, ListExpression(*args).evaluate(evaluation))
        else:
            return MakeBoxes(expr, f).evaluate(evaluation)

    def apply_infix(self, expr, h, prec, grouping, f, evaluation):
        """MakeBoxes[Infix[expr_, h_, prec_:None, grouping_:None],
        f:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        def get_op(op):
            if not isinstance(op, String):
                op = MakeBoxes(op, f)
            else:
                op_value = op.get_string_value()
                if f.get_name() == "System`InputForm" and op_value in ["*", "^"]:
                    pass
                elif (
                    f.get_name() in ("System`InputForm", "System`OutputForm")
                    and not op_value.startswith(" ")
                    and not op_value.endswith(" ")
                ):
                    op = String(" " + op_value + " ")
            return op

        precedence = prec.get_int_value()
        grouping = grouping.get_name()

        if isinstance(expr, Atom):
            evaluation.message("Infix", "normal", Integer1)
            return None

        elements = expr.elements
        if len(elements) > 1:
            if h.has_form("List", len(elements) - 1):
                ops = [get_op(op) for op in h.elements]
            else:
                ops = [get_op(h)] * (len(elements) - 1)
            return make_boxes_infix(elements, ops, precedence, grouping, f)
        elif len(elements) == 1:
            return MakeBoxes(elements[0], f)
        else:
            return MakeBoxes(expr, f)


class ToBoxes(Builtin):
    """
    <dl>
      <dt>'ToBoxes[$expr$]'
      <dd>evaluates $expr$ and converts the result to box form.
    </dl>

    Unlike 'MakeBoxes', 'ToBoxes' evaluates its argument:
    >> ToBoxes[a + a]
     = RowBox[{2,  , a}]

    >> ToBoxes[a + b]
     = RowBox[{a, +, b}]
    >> ToBoxes[a ^ b] // FullForm
     = SuperscriptBox["a", "b"]
    """

    summary_text = "produce the display boxes of an evaluated expression"

    def apply(self, expr, form, evaluation):
        "ToBoxes[expr_, form_:StandardForm]"

        form_name = form.get_name()
        if form_name is None:
            evaluation.message("ToBoxes", "boxfmt", form)
        boxes = format_element(expr, evaluation, form)
        return boxes


# ### The following classes maybe deserves another module...


class _NumberForm(Builtin):
    """
    Base class for NumberForm, AccountingForm, EngineeringForm, and ScientificForm.
    """

    default_ExponentFunction = None
    default_NumberFormat = None

    messages = {
        "npad": "Value for option NumberPadding -> `1` should be a string or a pair of strings.",
        "dblk": "Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.",
        "npt": "Value for option `1` -> `2` is expected to be a string.",
        "nsgn": "Value for option NumberSigns -> `1` should be a pair of strings or two pairs of strings.",
        "nspr": "Value for option NumberSeparator -> `1` should be a string or a pair of strings.",
        "opttf": "Value of option `1` -> `2` should be True or False.",
        "estep": "Value of option `1` -> `2` is not a positive integer.",
        "iprf": "Formatting specification `1` should be a positive integer or a pair of positive integers.",  # NumberFormat only
        "sigz": "In addition to the number of digits requested, one or more zeros will appear as placeholders.",
    }

    def check_options(self, options, evaluation):
        """
        Checks options are valid and converts them to python.
        """
        result = {}
        for option_name in self.options:
            method = getattr(self, "check_" + option_name)
            arg = options["System`" + option_name]
            value = method(arg, evaluation)
            if value is None:
                return None
            result[option_name] = value
        return result

    def check_DigitBlock(self, value, evaluation):
        py_value = value.get_int_value()
        if value.sameQ(SymbolInfinity):
            return [0, 0]
        elif py_value is not None and py_value > 0:
            return [py_value, py_value]
        elif value.has_form("List", 2):
            nleft, nright = value.elements
            py_left, py_right = nleft.get_int_value(), nright.get_int_value()
            if nleft.sameQ(SymbolInfinity):
                nleft = 0
            elif py_left is not None and py_left > 0:
                nleft = py_left
            else:
                nleft = None
            if nright.sameQ(SymbolInfinity):
                nright = 0
            elif py_right is not None and py_right > 0:
                nright = py_right
            else:
                nright = None
            result = [nleft, nright]
            if None not in result:
                return result
        return evaluation.message(self.get_name(), "dblk", value)

    def check_ExponentFunction(self, value, evaluation):
        if value.sameQ(SymbolAutomatic):
            return self.default_ExponentFunction

        def exp_function(x):
            return Expression(value, x).evaluate(evaluation)

        return exp_function

    def check_NumberFormat(self, value, evaluation):
        if value.sameQ(SymbolAutomatic):
            return self.default_NumberFormat

        def num_function(man, base, exp, options):
            return Expression(value, man, base, exp).evaluate(evaluation)

        return num_function

    def check_NumberMultiplier(self, value, evaluation):
        result = value.get_string_value()
        if result is None:
            evaluation.message(self.get_name(), "npt", "NumberMultiplier", value)
        return result

    def check_NumberPoint(self, value, evaluation):
        result = value.get_string_value()
        if result is None:
            evaluation.message(self.get_name(), "npt", "NumberPoint", value)
        return result

    def check_ExponentStep(self, value, evaluation):
        result = value.get_int_value()
        if result is None or result <= 0:
            return evaluation.message(self.get_name(), "estep", "ExponentStep", value)
        return result

    def check_SignPadding(self, value, evaluation):
        if value.sameQ(SymbolTrue):
            return True
        elif value.sameQ(SymbolFalse):
            return False
        return evaluation.message(self.get_name(), "opttf", value)

    def _check_List2str(self, value, msg, evaluation):
        if value.has_form("List", 2):
            result = [element.get_string_value() for element in value.elements]
            if None not in result:
                return result
        return evaluation.message(self.get_name(), msg, value)

    def check_NumberSigns(self, value, evaluation):
        return self._check_List2str(value, "nsgn", evaluation)

    def check_NumberPadding(self, value, evaluation):
        return self._check_List2str(value, "npad", evaluation)

    def check_NumberSeparator(self, value, evaluation):
        py_str = value.get_string_value()
        if py_str is not None:
            return [py_str, py_str]
        return self._check_List2str(value, "nspr", evaluation)


class NumberForm(_NumberForm):
    """
    <dl>
      <dt>'NumberForm[$expr$, $n$]'
      <dd>prints a real number $expr$ with $n$-digits of precision.

      <dt>'NumberForm[$expr$, {$n$, $f$}]'
      <dd>prints with $n$-digits and $f$ digits to the right of the decimal point.
    </dl>

    >> NumberForm[N[Pi], 10]
     = 3.141592654

    >> NumberForm[N[Pi], {10, 5}]
     = 3.14159


    ## Undocumented edge cases
    #> NumberForm[Pi, 20]
     = Pi
    #> NumberForm[2/3, 10]
     = 2 / 3

    ## No n or f
    #> NumberForm[N[Pi]]
     = 3.14159
    #> NumberForm[N[Pi, 20]]
     = 3.1415926535897932385
    #> NumberForm[14310983091809]
     = 14310983091809

    ## Zero case
    #> z0 = 0.0;
    #> z1 = 0.0000000000000000000000000000;
    #> NumberForm[{z0, z1}, 10]
     = {0., 0.×10^-28}
    #> NumberForm[{z0, z1}, {10, 4}]
     = {0.0000, 0.0000×10^-28}

    ## Trailing zeros
    #> NumberForm[1.0, 10]
     = 1.
    #> NumberForm[1.000000000000000000000000, 10]
     = 1.000000000
    #> NumberForm[1.0, {10, 8}]
     = 1.00000000
    #> NumberForm[N[Pi, 33], 33]
     = 3.14159265358979323846264338327950

    ## Correct rounding - see sympy/issues/11472
    #> NumberForm[0.645658509, 6]
     = 0.645659
    #> NumberForm[N[1/7], 30]
     = 0.1428571428571428

    ## Integer case
    #> NumberForm[{0, 2, -415, 83515161451}, 5]
     = {0, 2, -415, 83515161451}
    #> NumberForm[{2^123, 2^123.}, 4, ExponentFunction -> ((#1) &)]
     = {10633823966279326983230456482242756608, 1.063×10^37}
    #> NumberForm[{0, 10, -512}, {10, 3}]
     = {0.000, 10.000, -512.000}

    ## Check arguments
    #> NumberForm[1.5, -4]
     : Formatting specification -4 should be a positive integer or a pair of positive integers.
     = 1.5
    #> NumberForm[1.5, {1.5, 2}]
     : Formatting specification {1.5, 2} should be a positive integer or a pair of positive integers.
     = 1.5
    #> NumberForm[1.5, {1, 2.5}]
     : Formatting specification {1, 2.5} should be a positive integer or a pair of positive integers.
     = 1.5

    ## Right padding
    #> NumberForm[153., 2]
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     = 150.
    #> NumberForm[0.00125, 1]
     = 0.001
    #> NumberForm[10^5 N[Pi], {5, 3}]
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     = 314160.000
    #> NumberForm[10^5 N[Pi], {6, 3}]
     = 314159.000
    #> NumberForm[10^5 N[Pi], {6, 10}]
     = 314159.0000000000
    #> NumberForm[1.0000000000000000000, 10, NumberPadding -> {"X", "Y"}]
     = X1.000000000

    ## Check options

    ## DigitBlock
    #> NumberForm[12345.123456789, 14, DigitBlock -> 3]
     = 12,345.123 456 789
    #> NumberForm[12345.12345678, 14, DigitBlock -> 3]
     = 12,345.123 456 78
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> {4, 2}]
     = 31,4159.26 53 58 97 9
    #> NumberForm[1.2345, 3, DigitBlock -> -4]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345
    #> NumberForm[1.2345, 3, DigitBlock -> x]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345
    #> NumberForm[1.2345, 3, DigitBlock -> {x, 3}]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345
    #> NumberForm[1.2345, 3, DigitBlock -> {5, -3}]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345

    ## ExponentFunction
    #> NumberForm[12345.123456789, 14, ExponentFunction -> ((#) &)]
     = 1.2345123456789×10^4
    #> NumberForm[12345.123456789, 14, ExponentFunction -> (Null&)]
     = 12345.123456789
    #> y = N[Pi^Range[-20, 40, 15]];
    #> NumberForm[y, 10, ExponentFunction -> (3 Quotient[#, 3] &)]
     =  {114.0256472×10^-12, 3.267763643×10^-3, 93.64804748×10^3, 2.683779414×10^12, 76.91214221×10^18}
    #> NumberForm[y, 10, ExponentFunction -> (Null &)]
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     = {0.0000000001140256472, 0.003267763643, 93648.04748, 2683779414000., 76912142210000000000.}

    ## ExponentStep
    #> NumberForm[10^8 N[Pi], 10, ExponentStep -> 3]
     = 314.1592654×10^6
    #> NumberForm[1.2345, 3, ExponentStep -> x]
     : Value of option ExponentStep -> x is not a positive integer.
     = 1.2345
    #> NumberForm[1.2345, 3, ExponentStep -> 0]
     : Value of option ExponentStep -> 0 is not a positive integer.
     = 1.2345
    #> NumberForm[y, 10, ExponentStep -> 6]
     = {114.0256472×10^-12, 3267.763643×10^-6, 93648.04748, 2.683779414×10^12, 76.91214221×10^18}

    ## NumberFormat
    #> NumberForm[y, 10, NumberFormat -> (#1 &)]
     = {1.140256472, 0.003267763643, 93648.04748, 2.683779414, 7.691214221}

    ## NumberMultiplier
    #> NumberForm[1.2345, 3, NumberMultiplier -> 0]
     : Value for option NumberMultiplier -> 0 is expected to be a string.
     = 1.2345
    #> NumberForm[N[10^ 7 Pi], 15, NumberMultiplier -> "*"]
     = 3.14159265358979*10^7

    ## NumberPoint
    #> NumberForm[1.2345, 5, NumberPoint -> ","]
     = 1,2345
    #> NumberForm[1.2345, 3, NumberPoint -> 0]
     : Value for option NumberPoint -> 0 is expected to be a string.
     = 1.2345

    ## NumberPadding
    #> NumberForm[1.41, {10, 5}]
     = 1.41000
    #> NumberForm[1.41, {10, 5}, NumberPadding -> {"", "X"}]
     = 1.41XXX
    #> NumberForm[1.41, {10, 5}, NumberPadding -> {"X", "Y"}]
     = XXXXX1.41YYY
    #> NumberForm[1.41, 10, NumberPadding -> {"X", "Y"}]
     = XXXXXXXX1.41
    #> NumberForm[1.2345, 3, NumberPadding -> 0]
     :  Value for option NumberPadding -> 0 should be a string or a pair of strings.
     = 1.2345
    #> NumberForm[1.41, 10, NumberPadding -> {"X", "Y"}, NumberSigns -> {"-------------", ""}]
     = XXXXXXXXXXXXXXXXXXXX1.41
    #> NumberForm[{1., -1., 2.5, -2.5}, {4, 6}, NumberPadding->{"X", "Y"}]
     = {X1.YYYYYY, -1.YYYYYY, X2.5YYYYY, -2.5YYYYY}

    ## NumberSeparator
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> " "]
     = 314 159.265 358 979
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> {" ", ","}]
     = 314 159.265,358,979
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> {",", " "}]
     = 314,159.265 358 979
    #> NumberForm[N[10^ 7 Pi], 15, DigitBlock -> 3, NumberSeparator -> {",", " "}]
     = 3.141 592 653 589 79×10^7
    #> NumberForm[1.2345, 3, NumberSeparator -> 0]
     :  Value for option NumberSeparator -> 0 should be a string or a pair of strings.
     = 1.2345

    ## NumberSigns
    #> NumberForm[1.2345, 5, NumberSigns -> {"-", "+"}]
     = +1.2345
    #> NumberForm[-1.2345, 5, NumberSigns -> {"- ", ""}]
     = - 1.2345
    #> NumberForm[1.2345, 3, NumberSigns -> 0]
     : Value for option NumberSigns -> 0 should be a pair of strings or two pairs of strings.
     = 1.2345

    ## SignPadding
    #> NumberForm[1.234, 6, SignPadding -> True, NumberPadding -> {"X", "Y"}]
     = XXX1.234
    #> NumberForm[-1.234, 6, SignPadding -> True, NumberPadding -> {"X", "Y"}]
     = -XX1.234
    #> NumberForm[-1.234, 6, SignPadding -> False, NumberPadding -> {"X", "Y"}]
     = XX-1.234
    #> NumberForm[-1.234, {6, 4}, SignPadding -> False, NumberPadding -> {"X", "Y"}]
     = X-1.234Y

    ## 1-arg, Option case
    #> NumberForm[34, ExponentFunction->(Null&)]
     = 34

    ## zero padding integer x0.0 case
    #> NumberForm[50.0, {5, 1}]
     = 50.0
    #> NumberForm[50, {5, 1}]
     = 50.0

    ## Rounding correctly
    #> NumberForm[43.157, {10, 1}]
     = 43.2
    #> NumberForm[43.15752525, {10, 5}, NumberSeparator -> ",", DigitBlock -> 1]
     = 4,3.1,5,7,5,3
    #> NumberForm[80.96, {16, 1}]
     = 81.0
    #> NumberForm[142.25, {10, 1}]
     = 142.3
    """

    options = {
        "DigitBlock": "Infinity",
        "ExponentFunction": "Automatic",
        "ExponentStep": "1",
        "NumberFormat": "Automatic",
        "NumberMultiplier": '"×"',
        "NumberPadding": '{"", "0"}',
        "NumberPoint": '"."',
        "NumberSeparator": '{",", " "}',
        "NumberSigns": '{"-", ""}',
        "SignPadding": "False",
    }
    summary_text = "print at most a number of digits of all approximate real numbers in the expression"

    @staticmethod
    def default_ExponentFunction(value):
        n = value.get_int_value()
        if -5 <= n <= 5:
            return SymbolNull
        else:
            return value

    @staticmethod
    def default_NumberFormat(man, base, exp, options):
        py_exp = exp.get_string_value()
        if py_exp:
            mul = String(options["NumberMultiplier"])
            return Expression(
                SymbolRowBox,
                ListExpression(man, mul, Expression(SymbolSuperscriptBox, base, exp)),
            )
        else:
            return man

    def apply_list_n(self, expr, n, evaluation, options) -> Expression:
        "NumberForm[expr_List, n_, OptionsPattern[NumberForm]]"
        options = [
            Expression(SymbolRuleDelayed, Symbol(key), value)
            for key, value in options.items()
        ]
        return ListExpression(
            *[
                Expression(SymbolNumberForm, element, n, *options)
                for element in expr.elements
            ]
        )

    def apply_list_nf(self, expr, n, f, evaluation, options) -> Expression:
        "NumberForm[expr_List, {n_, f_}, OptionsPattern[NumberForm]]"
        options = [
            Expression(SymbolRuleDelayed, Symbol(key), value)
            for key, value in options.items()
        ]
        return ListExpression(
            *[
                Expression(SymbolNumberForm, element, ListExpression(n, f), *options)
                for element in expr.elements
            ],
        )

    def apply_makeboxes(self, expr, form, evaluation, options={}):
        """MakeBoxes[NumberForm[expr_, OptionsPattern[NumberForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""

        fallback = Expression(SymbolMakeBoxes, expr, form)

        py_options = self.check_options(options, evaluation)
        if py_options is None:
            return fallback

        if isinstance(expr, Integer):
            py_n = len(str(abs(expr.get_int_value())))
        elif isinstance(expr, Real):
            if expr.is_machine_precision():
                py_n = 6
            else:
                py_n = dps(expr.get_precision())
        else:
            py_n = None

        if py_n is not None:
            py_options["_Form"] = form.get_name()
            return number_form(expr, py_n, None, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)

    def apply_makeboxes_n(self, expr, n, form, evaluation, options={}):
        """MakeBoxes[NumberForm[expr_, n_?NotOptionQ, OptionsPattern[NumberForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""

        fallback = Expression(SymbolMakeBoxes, expr, form)

        py_n = n.get_int_value()
        if py_n is None or py_n <= 0:
            evaluation.message("NumberForm", "iprf", n)
            return fallback

        py_options = self.check_options(options, evaluation)
        if py_options is None:
            return fallback

        if isinstance(expr, (Integer, Real)):
            py_options["_Form"] = form.get_name()
            return number_form(expr, py_n, None, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)

    def apply_makeboxes_nf(self, expr, n, f, form, evaluation, options={}):
        """MakeBoxes[NumberForm[expr_, {n_, f_}, OptionsPattern[NumberForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""

        fallback = Expression(SymbolMakeBoxes, expr, form)

        nf = ListExpression(n, f)
        py_n = n.get_int_value()
        py_f = f.get_int_value()
        if py_n is None or py_n <= 0 or py_f is None or py_f < 0:
            evaluation.message("NumberForm", "iprf", nf)
            return fallback

        py_options = self.check_options(options, evaluation)
        if py_options is None:
            return fallback

        if isinstance(expr, (Integer, Real)):
            py_options["_Form"] = form.get_name()
            return number_form(expr, py_n, py_f, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)


class BaseForm(Builtin):
    """
    <dl>
      <dt>'BaseForm[$expr$, $n$]'
      <dd>prints numbers in $expr$ in base $n$.
    </dl>

    >> BaseForm[33, 2]
     = 100001_2

    >> BaseForm[234, 16]
     = ea_16

    >> BaseForm[12.3, 2]
     = 1100.01001100110011001_2

    >> BaseForm[-42, 16]
     = -2a_16

    >> BaseForm[x, 2]
     = x

    >> BaseForm[12, 3] // FullForm
     = BaseForm[12, 3]

    Bases must be between 2 and 36:
    >> BaseForm[12, -3]
     : Positive machine-sized integer expected at position 2 in BaseForm[12, -3].
     = BaseForm[12, -3]
    >> BaseForm[12, 100]
     : Requested base 100 must be between 2 and 36.
     = BaseForm[12, 100]

    #> BaseForm[0, 2]
     = 0_2
    #> BaseForm[0.0, 2]
     = 0.0_2

    #> BaseForm[N[Pi, 30], 16]
     = 3.243f6a8885a308d313198a2e_16
    """

    summary_text = "print with all numbers given in a base"
    messages = {
        "intpm": (
            "Positive machine-sized integer expected at position 2 in "
            "BaseForm[`1`, `2`]."
        ),
        "basf": "Requested base `1` must be between 2 and 36.",
    }

    def apply_makeboxes(self, expr, n, f, evaluation):
        """MakeBoxes[BaseForm[expr_, n_],
        f:StandardForm|TraditionalForm|OutputForm]"""

        base = n.get_int_value()
        if base <= 0:
            evaluation.message("BaseForm", "intpm", expr, n)
            return None

        if isinstance(expr, PrecisionReal):
            x = expr.to_sympy()
            p = reconstruct_digits(expr.get_precision())
        elif isinstance(expr, MachineReal):
            x = expr.value
            p = reconstruct_digits(machine_precision)
        elif isinstance(expr, Integer):
            x = expr.value
            p = 0
        else:
            return to_boxes(Expression(SymbolMakeBoxes, expr, f), evaluation)

        try:
            val = convert_base(x, base, p)
        except ValueError:
            return evaluation.message("BaseForm", "basf", n)

        if f is SymbolOutputForm:
            return to_boxes(String("%s_%d" % (val, base)), evaluation)
        else:
            return to_boxes(
                Expression(SymbolSubscriptBox, String(val), String(base)), evaluation
            )
