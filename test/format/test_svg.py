import re
from test.helper import session

from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.atoms import Integer0, Integer1, Real
from mathics.core.expression import Expression
from mathics.core.formatter import lookup_method
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolPoint

evaluation = session.evaluation

GraphicsSymbol = Symbol("Graphics")
ListSymbol = Symbol("List")

DISK_TEST_EXPR = Expression(
    Symbol("Disk")
)  # , ListExpression(Integer0, Integer0), Integer1)
COLOR_RED = Expression(Symbol("RGBColor"), Integer1, Integer0, Integer0)
COLOR_RED_ALPHA = Expression(
    Symbol("RGBColor"), Integer1, Integer0, Integer0, Real(0.25)
)


svg_wrapper_pat = r"""\s*<svg width="[0-9.]+px" height="[0-9.]+px" xmlns:svg="http://www.w3.org/2000/svg"
\s*xmlns="http://www.w3.org/2000/svg"
"""


# TODO: consider replace the following functions by something that parses SVG and produce a better
# structure, like a dict, containing information about the size, background and the primitives.


def extract_svg_background(svg):
    matches = re.match(svg_wrapper_pat, svg)
    assert matches
    svg = svg[len(matches.group(0)) :]
    rest_re = r"^\s+viewBox=(.*)\s+((?s:[<].*))<!--GraphicsElements-->((?s:.*))"
    parts_match = re.match(rest_re, svg)
    if parts_match:
        return parts_match.groups()[1].strip().replace("\n", " ")
    return ""


def extract_svg_body(svg):
    matches = re.match(svg_wrapper_pat, svg)
    assert matches
    body = svg[len(matches.group(0)) :]
    assert matches
    view_inner_match = re.match(
        r"^\s+viewBox=.*\s+<!--GraphicsElements-->\s+(?:<!--.+-->\s+)?(.*)", body
    )
    assert view_inner_match
    inner_svg = view_inner_match.group(1)
    return inner_svg


def get_svg(expression):
    options = {}
    boxes = MakeBoxes(expression).evaluate(evaluation)

    # Would be nice to DRY this boilerplate from boxes_to_mathml
    elements = boxes._elements
    elements, calc_dimensions = boxes._prepare_elements(
        elements, options=options, neg_y=True
    )
    xmin, xmax, ymin, ymax, w, h, width, height = calc_dimensions()
    data = (elements, xmin, xmax, ymin, ymax, w, h, width, height)

    format_fn = lookup_method(boxes, "svg")
    return format_fn(boxes, elements, data=data, options=options)


def test_svg_circle():
    expression = Expression(
        GraphicsSymbol,
        Expression(Symbol("Circle"), Expression(ListSymbol, Integer0, Integer0)),
    )

    svg = get_svg(expression)
    inner_svg = extract_svg_body(svg)

    # Circles are implemented as ellipses with equal major and minor axes.
    # Check for that.
    matches = re.match(
        r'^<ellipse cx="(\S+)" cy="(\S+)" rx="(\S+)" ry="(\S+)" .*/>', inner_svg
    )
    assert matches
    assert matches.group(1) == matches.group(2) == matches.group(3)


def test_svg_point():
    expression = Expression(
        GraphicsSymbol,
        Expression(SymbolPoint, ListExpression(Integer0, Integer0)),
    )

    svg = get_svg(expression)
    inner_svg = extract_svg_body(svg)

    # Circles are implemented as ellipses with equal major and minor axes.
    # Check for that.
    matches = re.match(r'^<circle cx="(\S+)" cy="(\S+)"', inner_svg)
    assert matches
    assert matches.group(1) == matches.group(2)


def test_svg_arrowbox():
    expression = Expression(
        GraphicsSymbol,
        Expression(
            Symbol("Arrow"),
            ListExpression(
                ListExpression(Integer0, Integer0),
                ListExpression(Integer1, Integer1),
            ),
        ),
    )
    svg = get_svg(expression)
    inner_svg = extract_svg_body(svg)

    matches = re.match(r'^<polyline points="', inner_svg)
    # TODO: Could pick endpoint of this line and match with beginnign of arrow polygon below
    assert matches
    # arrow_polygon = inner_svg[len(matches.group(0)) - 1 :]
    # matches = re.match(r'^<polygon points=".+"\s+style=".*"\s*/>', arrow_polygon)
    # assert matches


def test_svg_background():
    # If not specified, the background is empty
    expression = Expression(
        GraphicsSymbol,
        DISK_TEST_EXPR,
    ).evaluate(evaluation)
    svg = get_svg(expression)
    assert extract_svg_background(svg) == ""

    # Other possibilities...
    def check(expr, result):
        svg = get_svg(expression)
        background_svg = extract_svg_background(svg)
        matches = re.match(r'[<]rect(.*)style="(.*)"(.*[>])[<]/rect[>]', background_svg)
        assert matches
        background_fill = matches.groups()[1]
        assert background_fill == result

    # RGB color
    expression = Expression(
        GraphicsSymbol,
        DISK_TEST_EXPR,
        Expression(Symbol("Rule"), Symbol("System`Background"), COLOR_RED),
    ).evaluate(evaluation)

    check(expression, "fill:rgb(100.0%, 0.0%, 0.0%)")

    # RGBA color
    expression = Expression(
        GraphicsSymbol,
        DISK_TEST_EXPR,
        Expression(Symbol("Rule"), Symbol("System`Background"), COLOR_RED_ALPHA),
    ).evaluate(evaluation)

    check(expression, "fill:rgba(100.0%, 0.0%, 0.0%, 25.0%)")


def test_svg_bezier_curve():
    expression = Expression(
        GraphicsSymbol,
        Expression(
            Symbol("BezierCurve"),
            ListExpression(
                ListExpression(Integer0, Integer0),
                ListExpression(Integer1, Integer1),
            ),
        ),
    )
    svg = get_svg(expression)
    inner_svg = extract_svg_body(svg)

    matches = re.match(r'^<path d="', inner_svg)
    assert matches


if __name__ == "__main__":
    test_svg_bezier_curve()
