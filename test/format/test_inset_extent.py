# -*- coding: utf-8 -*-
"""
Text and other insets, whose size is in pixels, count for an automatic
PlotRange with their anchor points only, as in WMA: they do not shrink the
graphic to their own size.
"""

import re
from test.helper import session

import pytest


def svg_size(expr: str):
    svg = session.evaluate(f'ExportString[{expr}, "SVG"]').value
    width, height = re.search(
        r'<svg width="([^"]*)px" height="([^"]*)px"', svg
    ).groups()
    return float(width), float(height)


def circle_radius(expr: str) -> float:
    svg = session.evaluate(f'ExportString[{expr}, "SVG"]').value
    return float(re.search(r'<ellipse [^>]*rx="([^"]*)"', svg).group(1))


@pytest.mark.parametrize(
    "text",
    [
        'Text["hello world", {0, 0}]',
        'Text["x", {0, 0}]',
        'Text[Style["abc", Bold], {0.5, 0}]',
    ],
)
def test_text_does_not_shrink_the_graphic(text):
    assert svg_size(f"Graphics[{{Circle[], {text}}}]") == svg_size(
        "Graphics[{Circle[]}]"
    )
    assert circle_radius(f"Graphics[{{Circle[], {text}}}]") == circle_radius(
        "Graphics[{Circle[]}]"
    )


def test_text_anchor_extends_the_plot_range():
    # PlotRange {{-1, 3}, {-1, 1}}, as in WMA: twice as wide as high.
    width, height = svg_size('Graphics[{Circle[], Text["x", {3, 0}]}]')
    assert abs(width / height - 2) < 0.05


def test_text_only():
    # A graphic of text only has the usual size, not the size of its text.
    width, height = svg_size('Graphics[{Text["hello", {0, 0}]}]')
    assert width > 300 and height > 300
    width, height = svg_size('Graphics[{Text["a", {0, 0}], Text["b", {2, 1}]}]')
    assert width > 300


@pytest.mark.parametrize(
    "expr",
    [
        "Graphics[{Circle[]}]",
        "Plot[Sin[x], {x, 0, 6}]",
        "Graphics[{Disk[]}, Axes -> True]",
    ],
)
def test_graphics_without_insets_are_unchanged(expr):
    # The sizes these had before: the elements cover the plot range.
    expected = {
        "Graphics[{Circle[]}]": (351.067, 351.067),
        "Plot[Sin[x], {x, 0, 6}]": (434.133, 275.235),
        "Graphics[{Disk[]}, Axes -> True]": (382.133, 382.133),
    }[expr]
    width, height = svg_size(expr)
    assert abs(width - expected[0]) < 0.01 and abs(height - expected[1]) < 0.01
