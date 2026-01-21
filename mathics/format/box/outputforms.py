import re

from mathics.core.atoms import Integer, String
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BoxError, Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolFullForm,
    SymbolList,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolMathMLForm,
    SymbolTeXForm,
    SymbolTraditionalForm,
)
from mathics.eval.testing_expressions import expr_min
from mathics.format.box.makeboxes import format_element, is_print_form_callback

MULTI_NEWLINE_RE = re.compile(r"\n{2,}")


@is_print_form_callback("System`MathMLForm")
def eval_mathmlform(expr: BaseElement, evaluation: Evaluation) -> BoxElementMixin:
    "MakeBoxes[MathMLForm[expr_], form_]"
    from mathics.builtin.box.layout import RowBox

    boxes = format_element(expr, evaluation, SymbolTraditionalForm)
    try:
        mathml = boxes.boxes_to_mathml(evaluation=evaluation)
    except BoxError:
        evaluation.message(
            "General",
            "notboxes",
            Expression(SymbolFullForm, expr).evaluate(evaluation),
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
    return InterpretationBox(
        String(f'"{mathml}"'),
        Expression(SymbolMathMLForm, expr),
        **{"System`AutoDelete": SymbolTrue, "System`Editable": SymbolTrue},
    )


def eval_tableform(
    self, table: BaseElement, f: Symbol, evaluation: Evaluation, options
):
    """MakeBoxes[TableForm[table_], f_]"""
    from mathics.builtin.box.layout import GridBox
    from mathics.builtin.tensors import get_dimensions

    if not isinstance(table, Expression):
        return format_element(table, evaluation, f)

    dims = len(get_dimensions(table, head=SymbolList))
    depth = self.get_option(options, "TableDepth", evaluation, pop=True)
    options["System`TableDepth"] = depth
    depth = expr_min((Integer(dims), depth))
    depth = depth.value
    if depth is None:
        evaluation.message(self.get_name(), "int")
        return

    grid_options = evaluation.definitions.get_options("System`GridBox")

    if depth <= 0:
        return format_element(table, evaluation, f)
    elif depth == 1:
        return GridBox(
            ListExpression(
                *(
                    ListExpression(format_element(item, evaluation, f))
                    for item in table.elements
                ),
            ),
            **grid_options,
        )
        # return Expression(
        #    'GridBox', Expression('List', *(
        #        Expression('List', Expression('MakeBoxes', item, f))
        #        for item in table.elements)))
    else:
        options["System`TableDepth"] = Integer(depth - 2)

        def transform_item(item):
            if depth > 2:
                return self.eval_makeboxes(item, f, evaluation, options)
            else:
                return format_element(item, evaluation, f)

        result = GridBox(
            ListExpression(
                *(
                    ListExpression(
                        *(transform_item(item) for item in row.elements),
                    )
                    for row in table.elements
                ),
            ),
            **grid_options,
        )
        options["System`TableDepth"] = Integer(depth)
        return result


@is_print_form_callback("System`TeXForm")
def eval_texform(expr: BaseElement, evaluation: Evaluation) -> BoxElementMixin:
    from mathics.builtin.box.layout import InterpretationBox

    boxes = format_element(expr, evaluation, SymbolTraditionalForm)
    try:
        # Here we set ``show_string_characters`` to False, to reproduce
        # the standard behaviour in WMA. Remove this parameter to recover the
        # quotes in InputForm and FullForm
        tex = boxes.boxes_to_tex(
            evaluation=evaluation, show_string_characters=SymbolFalse
        )

        # Replace multiple newlines by a single one e.g. between asy-blocks
        tex = MULTI_NEWLINE_RE.sub("\n", tex)

        tex = tex.replace(" \uF74c", " \\, d")  # tmp hack for Integrate
    except BoxError:
        evaluation.message(
            "General",
            "notboxes",
            Expression(SymbolFullForm, expr).evaluate(evaluation),
        )
        tex = ""
    return InterpretationBox(
        String(f'"{tex}"'),
        Expression(SymbolTeXForm, expr),
        **{"System`AutoDelete": SymbolTrue, "System`Editable": SymbolTrue},
    )
