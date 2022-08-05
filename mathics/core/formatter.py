import inspect
import mpmath
import typing
from typing import Any, Callable, Tuple, Optional
import re


from mathics.core.atoms import (
    SymbolString,
    SymbolI,
    String,
    Integer,
    Rational,
    Real,
    Complex,
)
from mathics.core.number import dps
from mathics.core.element import BaseElement, BoxElement, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.parser import is_symbol_name
from mathics.core.symbols import (
    Symbol,
    SymbolMakeBoxes,
    Atom,
    SymbolDivide,
    SymbolFalse,
    SymbolFullForm,
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolHoldForm,
    SymbolList,
    SymbolNumberForm,
    SymbolPostfix,
    SymbolPlus,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolTimes,
    SymbolTrue,
    format_symbols,
)
from mathics.core.systemsymbols import (
    SymbolComplex,
    SymbolMinus,
    SymbolOutputForm,
    SymbolRational,
    SymbolStandardForm,
)

# key is str: (to_xxx name, value) is formatter function to call
format2fn: dict = {}


def encode_mathml(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&quot;").replace(" ", "&nbsp;")
    text = text.replace("\n", '<mspace linebreak="newline" />')
    return text


TEX_REPLACE = {
    "{": r"\{",
    "}": r"\}",
    "_": r"\_",
    "$": r"\$",
    "%": r"\%",
    "#": r"\#",
    "&": r"\&",
    "\\": r"\backslash{}",
    "^": r"{}^{\wedge}",
    "~": r"\sim{}",
    "|": r"\vert{}",
}
TEX_TEXT_REPLACE = TEX_REPLACE.copy()
TEX_TEXT_REPLACE.update(
    {
        "<": r"$<$",
        ">": r"$>$",
        "~": r"$\sim$",
        "|": r"$\vert$",
        "\\": r"$\backslash$",
        "^": r"${}^{\wedge}$",
    }
)
TEX_REPLACE_RE = re.compile("([" + "".join([re.escape(c) for c in TEX_REPLACE]) + "])")


def encode_tex(text: str, in_text=False) -> str:
    def replace(match):
        c = match.group(1)
        repl = TEX_TEXT_REPLACE if in_text else TEX_REPLACE
        # return TEX_REPLACE[c]
        return repl.get(c, c)

    text = TEX_REPLACE_RE.sub(replace, text)
    text = text.replace("\n", "\\newline\n")
    return text


extra_operators = set(
    (
        ",",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "\u301a",
        "\u301b",
        "\u00d7",
        "\u2032",
        "\u2032\u2032",
        " ",
        "\u2062",
        "\u222b",
        "\u2146",
    )
)


def lookup_method(self, format: str, module_fn_name=None) -> Callable:
    """
    Find a conversion method for `format` in self's class method resolution order.
    """
    for cls in inspect.getmro(type(self)):
        format_fn = format2fn.get((format, cls), None)
        if format_fn is not None:
            # print(f"format function: {format_fn.__name__} for {type(self).__name__}")
            return format_fn
    raise RuntimeError(
        f"Can't find formatter {format_fn.__name__} for {type(self).__name__}"
    )


def add_conversion_fn(cls, module_fn_name=None) -> None:
    """Add to `format2fn` a mapping from a conversion type and builtin-class
    to a conversion method.

    The conversion type is determined form the module name.
    For example, in module mathics.format.svg the conversion
    type is "svg".

    The conversion method is assumed to be a method in the caller's
    module, and is derived from lowercasing `cls`.

    For example function arrowbox in module mathics.format.svg would be
    the SVG conversion routine for class ArrowBox.

    We use frame introspection to get all of this done.
    """
    fr = inspect.currentframe().f_back
    module_dict = fr.f_globals

    # The last part of the module name is expected to be the conversion routine.
    conversion_type = module_dict["__name__"].split(".")[-1]

    # Derive the conversion function from the passed-in class argument,
    # unless it is already set.
    if module_fn_name is None:
        module_fn_name = cls.__name__.lower()
    elif hasattr(module_fn_name, "__name__"):
        module_fn_name = module_fn_name.__name__

    # Finally register the mapping: (Builtin-class, conversion name) -> conversion_function.
    format2fn[(conversion_type, cls)] = module_dict[module_fn_name]


def int_to_s_exp(expr: BaseElement, n: int) -> Tuple[str, int, bool]:
    n = expr.get_int_value()
    if n < 0:
        nonnegative = 0
        s = str(-n)
    else:
        nonnegative = 1
        s = str(n)
    exp = len(s) - 1
    return s, exp, nonnegative


def real_to_s_exp(expr: BaseElement, n: Optional[int]) -> Tuple[str, int, bool]:
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


def number_form(
    expr: BaseElement, n: int, f: int, evaluation: Optional[Evaluation], options: dict
) -> Optional[BoxElement]:
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
            _BoxedString(s, number_as_text=True),
            _BoxedString(base, number_as_text=True),
            _BoxedString(pexp, number_as_text=True),
            options,
        )
    else:
        return method(_BoxedString(s), _BoxedString(base), _BoxedString(pexp), options)


#
#   Comment from Rocky:
#   " More scalable and more comprehensible is doing it inside a module for a particular form like we did for formatter. See [Aspect-Oriented Programming](https://en.wikipedia.org/wiki/Aspect-oriented_programming)
#
# Adding a method on the base class which does a lookup on the class I think is a good thing and the way to go. And it more closely maintains API compatibility, were it not for the fact that the form should be a Symbol rather than a str.
# But in the short term we can do the same as we did for Expression and allow either a str or a Symbol and do the checking inside the .format() routine. Then eventually we'll remove the check."
#  Also, moving the implementation of boxes_to_mathml / boxes_to_tex etc to specific module would be a following step.
#
#


class _BoxedString(BoxElement):
    value: str
    box_options: dict
    options = {
        "System`ShowStringCharacters": "False",
    }

    @property
    def head(self):
        return SymbolString

    def __init__(self, string: str, **options):
        self.value = string
        self.box_options = {
            "System`ShowStringCharacters": SymbolFalse,
        }
        self.box_options.update(options)

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

    def boxes_to_text(self, **options):
        value = self.value
        if value.startswith('"') and value.endswith('"'):  # nopep8
            show_string_characters = options.get("show_string_characters", None)
            if show_string_characters is None:
                show_string_characters = (
                    self.box_options["System`ShowStringCharacters"] is SymbolTrue
                )

            if not show_string_characters:
                value = value[1:-1]
        return value

    def boxes_to_mathml(self, **options) -> str:
        from mathics.builtin import display_operators_set as operators

        text = self.value

        number_as_text = options.get("number_as_text", None)
        if number_as_text is None:
            number_as_text = self.box_options.get("number_as_text", False)

        def render(format, string):
            encoded_text = encode_mathml(string)
            return format % encoded_text

        if text.startswith('"') and text.endswith('"'):
            show_string_characters = options.get("show_string_characters", None)
            if show_string_characters is None:
                show_string_characters = (
                    self.box_options["System`ShowStringCharacters"] is SymbolTrue
                )

            if show_string_characters:
                return render("<ms>%s</ms>", text[1:-1])
            else:
                outtext = ""
                for line in text[1:-1].split("\n"):
                    outtext += render("<mtext>%s</mtext>", line)
                return outtext
        elif (
            text
            and not number_as_text
            and ("0" <= text[0] <= "9" or text[0] in (".", "-"))
        ):
            return render("<mn>%s</mn>", text)
        else:
            if text in operators or text in extra_operators:
                if text == "\u2146":
                    return render(
                        '<mo form="prefix" lspace="0.2em" rspace="0">%s</mo>', text
                    )
                if text == "\u2062":
                    return render(
                        '<mo form="prefix" lspace="0" rspace="0.2em">%s</mo>', text
                    )
                return render("<mo>%s</mo>", text)
            elif is_symbol_name(text):
                return render("<mi>%s</mi>", text)
            else:
                outtext = ""
                for line in text.split("\n"):
                    outtext += render("<mtext>%s</mtext>", line)
                return outtext

    def boxes_to_tex(self, **options) -> str:
        text = self.value

        def render(format, string, in_text=False):
            return format % encode_tex(string, in_text)

        if text.startswith('"') and text.endswith('"'):
            show_string_characters = options.get("show_string_characters", None)
            if show_string_characters is None:
                show_string_characters = (
                    self.box_options["System`ShowStringCharacters"] is SymbolTrue
                )
            # In WMA, ``TeXForm`` never adds quotes to
            # strings, even if ``InputForm`` or ``FullForm``
            # is required, to so get the standard WMA behaviour,
            # this option is set to False:
            # show_string_characters = False

            if show_string_characters:
                return render(r'\text{"%s"}', text[1:-1], in_text=True)
            else:
                return render(r"\text{%s}", text[1:-1], in_text=True)
        elif text and text[0] in "0123456789-.":
            return render("%s", text)
        else:
            # FIXME: this should be done in a better way.
            if text == "\u2032":
                return "'"
            elif text == "\u2032\u2032":
                return "''"
            elif text == "\u2062":
                return " "
            elif text == "\u221e":
                return r"\infty "
            elif text == "\u00d7":
                return r"\times "
            elif text in ("(", "[", "{"):
                return render(r"\left%s", text)
            elif text in (")", "]", "}"):
                return render(r"\right%s", text)
            elif text == "\u301a":
                return r"\left[\left["
            elif text == "\u301b":
                return r"\right]\right]"
            elif text == "," or text == ", ":
                return text
            elif text == "\u222b":
                return r"\int"
            # Tolerate WL or Unicode DifferentialD
            elif text in ("\u2146", "\U0001D451"):
                return r"\, d"
            elif text == "\u2211":
                return r"\sum"
            elif text == "\u220f":
                return r"\prod"
            elif len(text) > 1:
                return render(r"\text{%s}", text, in_text=True)
            else:
                return render("%s", text)

    def get_head(self) -> Symbol:
        return SymbolString

    def get_head_name(self) -> str:
        return "System`String"

    def get_string_value(self) -> str:
        return self.value

    def to_expression(self) -> String:
        return String(self.value)


element_formatters = {}


def format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol, **kwargs
) -> BaseElement:
    """
    Applies formats associated to the expression, and then calls Makeboxes
    """
    do_format = element_formatters.get(type(element), do_format_element)
    expr = do_format(element, evaluation, form)
    result = Expression(SymbolMakeBoxes, expr, form)
    result_box = result.evaluate(evaluation)

    if isinstance(result_box, BoxElement):
        return result_box
    elif isinstance(result_box, String):
        return _BoxedString(result_box.value)
    else:
        return format_element(element, evaluation, SymbolFullForm, **kwargs)


# do_format_*


def do_format(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> BaseElement:
    do_format_method = element_formatters.get(type(element), do_format_element)
    return do_format_method(element, evaluation, form)


def do_format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> BaseElement:
    """
    Applies formats associated to the expression and removes
    superfluous enclosing formats.
    """

    formats = format_symbols
    evaluation.inc_recursion_depth()
    try:
        expr = element
        head = element.get_head()
        elements = element.get_elements()
        include_form = False
        # If the expression is enclosed by a Format
        # takes the form from the expression and
        # removes the format from the expression.
        if head in formats and len(elements) == 1:
            expr = elements[0]
            if not (form is SymbolOutputForm and head is SymbolStandardForm):
                form = head
                include_form = True

        # If form is Fullform, return it without changes
        if form is SymbolFullForm:
            if include_form:
                expr = Expression(form, expr)
            return expr
        # Repeated and RepeatedNull confuse the formatter,
        # so we need to hardlink their format rules:
        if head is SymbolRepeated:
            if len(elements) == 1:
                return Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolPostfix,
                        ListExpression(elements[0]),
                        String(".."),
                        Integer(170),
                    ),
                )
            else:
                return Expression(SymbolHoldForm, expr)
        elif head is SymbolRepeatedNull:
            if len(elements) == 1:
                return Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolPostfix,
                        Expression(SymbolList, elements[0]),
                        String("..."),
                        Integer(170),
                    ),
                )
            else:
                return Expression(SymbolHoldForm, expr)

        # If expr is not an atom, looks for formats in its definition
        # and apply them.
        def format_expr(expr):
            if not (isinstance(expr, Atom)) and not (isinstance(expr.head, Atom)):
                # expr is of the form f[...][...]
                return None
            name = expr.get_lookup_name()
            formats = evaluation.definitions.get_formats(name, form.get_name())
            for rule in formats:
                result = rule.apply(expr, evaluation)
                if result is not None and result != expr:
                    return result.evaluate(evaluation)
            return None

        formatted = format_expr(expr) if isinstance(expr, EvalMixin) else None
        if formatted is not None:
            do_format = element_formatters.get(type(formatted), do_format_element)
            result = do_format(formatted, evaluation, form)
            if include_form:
                result = Expression(form, result)
            return result

        # If the expression is still enclosed by a Format,
        # iterate.
        # If the expression is not atomic or of certain
        # specific cases, iterate over the elements.
        head = expr.get_head()
        if head in formats:
            do_format = element_formatters.get(type(element), do_format_element)
            expr = do_format(expr, evaluation, form)
        elif (
            head is not SymbolNumberForm
            and not isinstance(expr, (Atom, BoxElement))
            and head not in (SymbolGraphics, SymbolGraphics3D)
        ):
            # print("Not inside graphics or numberform, and not is atom")
            new_elements = [
                element_formatters.get(type(element), do_format_element)(
                    element, evaluation, form
                )
                for element in expr.elements
            ]
            expr_head = expr.head
            do_format = element_formatters.get(type(expr_head), do_format_element)
            expr = Expression(do_format(expr_head, evaluation, form), *new_elements)
        if include_form:
            expr = Expression(form, expr)
        return expr
    finally:
        evaluation.dec_recursion_depth()


def do_format_rational(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> BaseElement:
    if form is SymbolFullForm:
        return do_format_expression(
            Expression(
                Expression(SymbolHoldForm, SymbolRational),
                element.numerator(),
                element.denominator(),
            ),
            evaluation,
            form,
        )
    else:
        numerator = element.numerator()
        minus = numerator.value < 0
        if minus:
            numerator = Integer(-numerator.value)
        result = Expression(SymbolDivide, numerator, element.denominator())
        if minus:
            result = Expression(SymbolMinus, result)
        result = Expression(SymbolHoldForm, result)
        return do_format_expression(result, evaluation, form)


def do_format_complex(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> BaseElement:
    if form is SymbolFullForm:
        return do_format_expression(
            Expression(
                Expression(SymbolHoldForm, SymbolComplex), element.real, element.imag
            ),
            evaluation,
            form,
        )

    parts: typing.List[Any] = []
    if element.is_machine_precision() or not element.real.is_zero:
        parts.append(element.real)
    if element.imag.sameQ(Integer(1)):
        parts.append(SymbolI)
    else:
        parts.append(Expression(SymbolTimes, element.imag, SymbolI))

    if len(parts) == 1:
        result = parts[0]
    else:
        result = Expression(SymbolPlus, *parts)

    return do_format_expression(Expression(SymbolHoldForm, result), evaluation, form)


def do_format_expression(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> BaseElement:
    # # not sure how much useful is this format_cache
    # if element._format_cache is None:
    #    element._format_cache = {}

    # last_evaluated_time, expr = element._format_cache.get(form, (None, None))
    # if last_evaluated_time is not None and expr is not None:
    # if True
    #    symbolname = expr.get_name()
    #    if symbolname != "":
    #        if not evaluation.definitions.is_uncertain_final_value(
    #            last_evaluated_time, set((symbolname,))
    #        ):
    #            return expr
    expr = do_format_element(element, evaluation, form)
    # element._format_cache[form] = (evaluation.definitions.now, expr)
    return expr


element_formatters[Rational] = do_format_rational
element_formatters[Complex] = do_format_complex
element_formatters[Expression] = do_format_expression
