import re
from test.helper import session

from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.atoms import Integer0, Integer1, Real
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolGraphics, SymbolPoint

evaluation = session.evaluation


# TODO: DRY this, which is repeated in test_svg

GraphicsSymbol = Symbol("Graphics")
ListSymbol = Symbol("List")


DISK_TEST_EXPR = Expression(
    Symbol("Disk")
)  # , ListExpression(Integer0, Integer0), Integer1)
COLOR_RED = Expression(Symbol("RGBColor"), Integer1, Integer0, Integer0)
COLOR_RED_ALPHA = Expression(
    Symbol("RGBColor"), Integer1, Integer0, Integer0, Real(0.25)
)


asy_wrapper_pat = r"""^\s*
\s*\\begin{asy}
\s*usepackage\("amsmath"\);
\s*size\(.+\);
\s*
"""


def extract_asy_body(asy):
    matches = re.match(asy_wrapper_pat, asy)
    body = asy[len(matches.group(0)) :]
    assert matches
    print(body)
    return body


def get_asy(expression):
    boxes = MakeBoxes(expression).evaluate(evaluation)
    return boxes.boxes_to_tex()


def test_asy_circle():
    expression = Expression(
        SymbolGraphics,
        Expression(Symbol("Circle"), ListExpression(Integer0, Integer0)),
    )

    asy = get_asy(expression)
    inner_asy = extract_asy_body(asy)

    # Circles are implemented as ellipses with equal major and minor axes.
    # Check for that.
    matches = re.match(r"^draw\(ellipse\(\((.+),\s*(.+)\),(.*),(.*)\), .*", inner_asy)

    assert matches
    # Check that center point is centered and
    # major and minor axes are the same
    assert matches.group(1) == matches.group(2)
    assert matches.group(3) == matches.group(4)


def test_asy_point():
    expression = Expression(
        SymbolGraphics,
        Expression(SymbolPoint, ListExpression(Integer0, Integer0)),
    )

    asy = get_asy(expression)
    inner_asy = extract_asy_body(asy)

    print(inner_asy)
    # matches = re.match(r'^Circle\((.+), (.+), (.+)\),.+;', inner_asy)
    matches = re.match(r"// PointBox\ndot\(\((.+), (.+)\), .+\);.*", inner_asy)
    assert matches
    # Since the x,y point is the same, we'll check that whatever this
    # coordinate mapped to, it is the same.
    assert matches.group(1) == matches.group(2)


def test_asy_arrowbox():
    expression = Expression(
        SymbolGraphics,
        Expression(
            Symbol("Arrow"),
            ListExpression(
                ListExpression(Integer0, Integer0),
                ListExpression(Integer1, Integer1),
            ),
        ),
    )
    asy = get_asy(expression)
    inner_asy = extract_asy_body(asy)

    matches = re.match(r"^draw\(.*\)", inner_asy)
    # TODO: Match line and arrowbox
    assert matches


def test_asy_background():
    def check(expr, result):
        # TODO: use regular expressions...
        background = get_asy(expression).strip().splitlines()[3]
        print(background)
        assert background == result

    # If not specified, the background is empty
    expression = Expression(
        GraphicsSymbol,
        DISK_TEST_EXPR,
    ).evaluate(evaluation)
    check(expression, "")

    expression = Expression(
        GraphicsSymbol,
        DISK_TEST_EXPR,
        Expression(Symbol("Rule"), Symbol("System`Background"), COLOR_RED),
    ).evaluate(evaluation)
    check(expression, "filldraw(box((0,0), (350,350)), rgb(1, 0, 0));")

    expression = Expression(
        GraphicsSymbol,
        DISK_TEST_EXPR,
        Expression(Symbol("Rule"), Symbol("System`Background"), COLOR_RED_ALPHA),
    ).evaluate(evaluation)
    check(expression, "filldraw(box((0,0), (350,350)), rgb(1, 0, 0)+opacity(0.25));")


def test_asy_bezier_curve():
    expression = Expression(
        SymbolGraphics,
        Expression(
            Symbol("BezierCurve"),
            ListExpression(
                ListExpression(Integer0, Integer0),
                ListExpression(Integer1, Integer1),
            ),
        ),
    )
    asy = get_asy(expression)
    inner_asy = extract_asy_body(asy)

    matches = re.match(r"// BezierCurveBox\nimport graph;", inner_asy)
    # TODO: Match line and arrowbox
    assert matches


def test_asy_rectanglebox():
    expression = Expression(
        SymbolGraphics,
        ListExpression(
            Expression(Symbol("Rectangle"), ListExpression(Integer0, Integer0))
        ),
    )
    asy = get_asy(expression)
    inner_asy = extract_asy_body(asy)

    matches = re.match(r"// RectangleBox\n", inner_asy)
    assert matches


if __name__ == "__main__":
    test_asy_bezier_curve()
