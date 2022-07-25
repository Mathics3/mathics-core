# -*- coding: utf-8 -*-
"""
Tests for mathics.core.drawing.image:

Image[] and image related functions.
"""
import os
import pytest

from test.helper import evaluate
from mathics.builtin.base import check_requires_list
from mathics.core.symbols import SymbolNull

image_tests = [('img = Import["ExampleData/lena.tif"];', None, "")]
if check_requires_list(["skimage"]):
    image_tests += [
        ("BinaryImageQ[img]", "False", ""),
        ("BinaryImageQ[Binarize[img]]", "True", ""),
        (
            """ein = Import["ExampleData/Einstein.jpg"]; ImageDimensions[ein]""",
            "{615, 768}",
            "",
        ),
        # FIXME: I wonder if the testing framework is broken here.
        # ('ImageResize[img], {400, 600}]', "-Image-", ""),
        # ("ImageDimensions[%]", "{400, 600}", ""),
        # ("ImageResize[ein, 256]", "-Image-", ""),
        # ("ImageDimensions[%]", "{256, 320}", ""),
        # ('ImageResize[ein, 256, Resampling -> "Bicubic"]', "-Image-", ""),
        # ('ImageResize[ein, {256, 256}, Resampling -> "Gaussian"]', "",
        #  "Gaussian resampling needs to maintain aspect ratio.")
        # ('ImageResize[ein, 256, Resampling -> "Invalid"]', "", "Invalid resampling method Invalid."),
        # ('ImageResize[ein, 256, Resampling -> Invalid]', "", "Invalid resampling method Invalid."),
        # ('ImageResize[ein, {x}]', "", "The size {x} is not a valid image size specification."),
        # ('ImageResize[ein, x]', "", "The size x is not a valid image size specification."),
        # ("ImageType[Binarize[img]]", "Bit", ""),
        # ("Binarize[img, 0.7]", "-Image-", ""),
        # ("Binarize[img, {0.2, 0.6}", "-Image-", "")
        # Are there others?
    ]


@pytest.mark.skipif(
    os.getenv("SANDBOX", False),
    reason="Test doesn't work in a sandboxed environment with access to local files",
)
@pytest.mark.parametrize(("str_expr, str_expected, msg"), image_tests)
def test_image(str_expr: str, str_expected: str, msg: str, message=""):
    result = evaluate(str_expr)
    if result is not SymbolNull or str_expected is not None:
        expected = evaluate(str_expected)
        if msg:
            assert result == expected, msg
        else:
            assert result == expected
