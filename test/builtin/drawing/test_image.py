# -*- coding: utf-8 -*-
"""
Tests for mathics.core.drawing.image:

Image[] and image related functions.
"""
import os
from test.helper import evaluate

import pytest

from mathics.builtin.base import check_requires_list
from mathics.core.symbols import SymbolNull

# Note we test with tif, jpg, and gif. Add others?
image_tests = [
    ('hedy = Import["ExampleData/hedy.tif"];', None, ""),
    ("BinaryImageQ[hedy]", "False", ""),
    ("BinaryImageQ[Binarize[hedy]]", "True", ""),
    (
        """ein = Import["ExampleData/Einstein.jpg"]; ImageDimensions[ein]""",
        "{615, 768}",
        "",
    ),
    ("ImageDimensions[ImageResize[ein, {61, 76}]]", "{61, 76}", ""),
    ("ImageDimensions[ImageTake[ein, 50]]", "{615, 50}", ""),
    ("ImageDimensions[ImageTake[ein, -50]]", "{615, 50}", ""),
    ("ImageDimensions[ImageTake[ein, 100000]]", "{615, 768}", ""),
    ("ImageDimensions[ImageTake[ein, -100000]]", "{615, 768}", ""),
    (
        """alice = Import["ExampleData/MadTeaParty.gif"]; ImageDimensions[alice]""",
        "{640, 487}",
        "",
    ),
    ("ImageDimensions[ImageResize[alice, {64, 48}]]", "{64, 48}", ""),
    ("ImageDimensions[ImageTake[alice, 50]]", "{640, 50}", ""),
    ("Image[{{0, 1}, {1, 0}, {1, 1}}] // ImageDimensions", "{2, 3}", ""),
    ("Image[{{0.2, 0.4}, {0.9, 0.6}, {0.3, 0.8}}] // ImageDimensions", "{2, 3}", ""),
    # FIXME: Our image handling is recovering from brokenness, but is not quite back...
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
     not check_requires_list(["skimage"]),
     reason="scikit-image (AKA skimage) is needed for working with Images",
)
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
