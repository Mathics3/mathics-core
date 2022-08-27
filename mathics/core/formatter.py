import inspect
import typing
from typing import Any, Callable
import re


from mathics.core.atoms import SymbolI, String, Integer, Rational, Complex
from mathics.core.element import BaseElement, BoxElementMixin, EvalMixin
from mathics.core.convert.expression import to_expression_with_specialization
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolMakeBoxes,
    Atom,
    SymbolDivide,
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


def boxes_to_format(boxes, format, **options) -> str:  # Maybe Union[str, bytearray]
    """
    Translates a box structure ``boxes`` to a file format ``format``.

    """
    return lookup_method(boxes, format)(boxes, **options)


def lookup_method(self, format: str) -> Callable:
    """
    Find a conversion method for `format` in self's class method resolution order.
    """
    for cls in inspect.getmro(type(self)):
        format_fn = format2fn.get((format, cls), None)
        if format_fn is not None:
            # print(f"format function: {format_fn.__name__} for {type(self).__name__}")
            return format_fn
    # backward compatibility
    boxes_to_method = getattr(self, f"boxes_to_{format}", None)
    if getattr(BoxElementMixin, f"boxes_to_{format}") is boxes_to_method:
        boxes_to_method = None
    if boxes_to_method:

        def ret_fn(box, elements=None, **opts):
            return boxes_to_method(elements, **opts)

        return ret_fn

    error_msg = f"Can't find formatter {format} for {type(self).__name__}"
    raise RuntimeError(error_msg)


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


element_formatters = {}


def format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol, **kwargs
) -> BaseElement:
    """
    Applies formats associated to the expression, and then calls Makeboxes
    """
    expr = do_format(element, evaluation, form)
    result = Expression(SymbolMakeBoxes, expr, form)
    result_box = result.evaluate(evaluation)
    if isinstance(result_box, String):
        return result_box
    if isinstance(result_box, BoxElementMixin):
        return result_box
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
            and not isinstance(expr, (Atom, BoxElementMixin))
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
            head = do_format(expr_head, evaluation, form)
            expr = to_expression_with_specialization(head, *new_elements)

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
