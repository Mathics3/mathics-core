# -*- coding: utf-8 -*-
"""
GraphicsGrid, GraphicsRow, GraphicsColumn and GraphicsArray: a Graphics of
Insets, and the rendering of a graphic inset into a graphic.
"""

import re
import xml.dom.minidom

import pytest

from test.helper import check_evaluation, session


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("Head[GraphicsGrid[{{Graphics[Disk[]], Graphics[Circle[]]}}]]", "Graphics"),
        (
            "Cases[GraphicsGrid[{{Graphics[Disk[]], Graphics[Circle[]]}, "
            "{Graphics[Rectangle[]]}}], _Inset, Infinity] // Length",
            "3",
        ),
        # Row 1 is at the top: the second row is lower.
        (
            "Cases[GraphicsColumn[{Graphics[Disk[]], Graphics[Circle[]]}], "
            "Inset[_, {x_, y_}, ___] :> y, Infinity] // (#[[1]] > #[[2]] &)",
            "True",
        ),
        (
            "Cases[GraphicsRow[{Graphics[Disk[]], Graphics[Circle[]]}, Spacings -> 0], "
            "Inset[_, {x_, _}, ___] :> x, Infinity]",
            "{180., 540.}",
        ),
        # Each graphic gets its own size.
        (
            "Cases[GraphicsRow[{Graphics[Disk[]], Graphics[Circle[], ImageSize -> 100]}], "
            "Inset[_, _, _, s_] :> s, Infinity]",
            "{{360., 360.}, {100., 100.}}",
        ),
        (
            "PlotRange /. List @@ Rest[GraphicsRow[{Graphics[Disk[]]}, Spacings -> 0]]",
            "{{0., 360.}, {-360., 0.}}",
        ),
        (
            "Count[GraphicsGrid[{{Graphics[Disk[]]}}, Frame -> All], _Line, Infinity]",
            "1",
        ),
        (
            "Background /. List @@ Rest[GraphicsRow[{Graphics[Disk[]]}, Background -> Red]]",
            "RGBColor[1, 0, 0]",
        ),
    ],
)
def test_graphics_grid(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)


def test_graphics_array_is_obsolete():
    check_evaluation(
        "Head[GraphicsArray[{Graphics[Disk[]], Graphics[Circle[]]}]]",
        "Graphics",
        expected_messages=("GraphicsArray is obsolete. Switching to GraphicsGrid.",),
    )
    check_evaluation(
        "Length[Cases[GraphicsArray[{{Graphics[Disk[]]}, {Graphics[Circle[]]}}, "
        "GraphicsSpacing -> 0.1], _Inset, Infinity]]",
        "2",
        expected_messages=("GraphicsArray is obsolete. Switching to GraphicsGrid.",),
    )


def svg_of(expr: str) -> str:
    return session.evaluate(f'ExportString[{expr}, "SVG"]').value


def test_inset_graphics_svg():
    svg = svg_of(
        "Graphics[{Inset[Graphics[Disk[]], {0, 0}, ImageScaled[{0.5, 0.5}], {1, 1}], "
        "Inset[Graphics[Rectangle[]], {2, 0}, ImageScaled[{0.5, 0.5}], {1, 1}]}, "
        "PlotRange -> {{-1, 3}, {-1, 1}}]"
    )
    # Two graphics, each an <svg> of its own in its rectangle: 100 pixels
    # for one unit, the centers at (100, 100) and (300, 100).
    rects = re.findall(
        r'<svg x="([^"]*)" y="([^"]*)" width="([^"]*)" height="([^"]*)"', svg
    )
    assert [tuple(float(v) for v in r) for r in rects] == [
        (50.0, 50.0, 100.0, 100.0),
        (250.0, 50.0, 100.0, 100.0),
    ]
    assert "not a valid primitive" not in svg
    xml.dom.minidom.parseString(svg.strip())


def test_inset_graphics_corner():
    # ImageScaled[{0, 0}]: the lower left corner of the inset is at the point.
    svg = svg_of(
        "Graphics[Inset[Graphics[Disk[]], {0, 0}, ImageScaled[{0, 0}], {1, 1}], "
        "PlotRange -> {{-1, 1}, {-1, 1}}]"
    )
    x, y, w, h = (
        float(v)
        for v in re.search(
            r'<svg x="([^"]*)" y="([^"]*)" width="([^"]*)" height="([^"]*)"', svg
        ).groups()
    )
    # One unit is w pixels; the lower left corner of the inset is at the
    # center of the image, (w, w), so its upper left corner is at (w, 0).
    assert w == h
    assert abs(x - w) < 1e-6 and abs(y) < 1e-6


def test_graphics_grid_svg_and_asy():
    expr = "GraphicsRow[{Graphics[Disk[]], Graphics[Circle[]], Graphics[Rectangle[]]}]"
    svg = svg_of(expr)
    assert svg.count("<svg") == 4
    xml.dom.minidom.parseString(svg.strip())
    tex = session.evaluate(f"ToString[{expr}, TeXForm]").value
    assert tex.count("// InsetBox: graphic") == 3
    assert tex.count("add(shift(") == 3


def test_inset_text_is_escaped():
    svg = svg_of('Graphics[Text["a < b & c", {0, 0}]]')
    assert "a &lt; b &amp; c" in svg
    xml.dom.minidom.parseString(svg.strip())
