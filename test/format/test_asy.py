import re

from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.atoms import Integer0, Integer1
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolGraphics, SymbolPoint
from mathics.session import MathicsSession

session = MathicsSession(add_builtin=True, catch_interrupt=False)
evaluation = Evaluation(session.definitions)


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
