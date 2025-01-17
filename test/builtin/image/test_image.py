# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.image.colors

Largely tests error messages when parameters are incorrect.
"""
from test.helper import check_evaluation, session

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msgs", "assert_failure_msg"),
    [
        (None, None, None, None),
        #
        # Base Image Atom
        #
        (
            "Image[{{{1,1,0},{0,1,1}}, {{1,0,1},{1,1,0}}}]",
            "-Image-",
            None,
            "Image Atom B&W",
        ),
        (
            "Image[{{{0,0,0,0.25},{0,0,0,0.5}}, {{0,0,0,0.5},{0,0,0,0.75}}}]",
            "-Image-",
            None,
            "Image Atom RGB",
        ),
        #
        # Operations over images
        #
        ('hedy = Import["ExampleData/hedy.tif"];', "Null", None, "Load an image"),
        (
            'ImageData[hedy, "Bytf"]',
            "ImageData[-Image-, Bytf]",
            ('Unsupported pixel format "Bytf".',),
            "Wrong Image Data",
        ),
        (
            "ImagePartition[hedy, 257]",
            "{{-Image-, -Image-}, {-Image-, -Image-}, {-Image-, -Image-}}",
            None,
            None,
        ),
        ("ImagePartition[hedy, 646]", "{{-Image-}}", None, None),
        ("ImagePartition[hedy, 647]", "{}", None, None),
        (
            "ImagePartition[hedy, {256, 300}]",
            "{{-Image-, -Image-}, {-Image-, -Image-}}",
            None,
            None,
        ),
        (
            "ImagePartition[hedy, {0, 300}]",
            "ImagePartition[-Image-, {0, 300}]",
            ("{0, 300} is not a valid size specification for image partitions.",),
            None,
        ),
        (
            "{82 / 255, 22 / 255, 57 / 255} // N",
            "{0.321569, 0.0862745, 0.223529}",
            None,
            "pixel byte values from bottom left corner",
        ),
        (
            "PixelValue[hedy, {0, 1}];",
            "Null",
            ("Padding not implemented for PixelValue.",),
            None,
        ),
        ("PixelValue[hedy, {512, 1}]", "{0.0509804, 0.0509804, 0.0588235}", None, None),
        (
            "PixelValue[hedy, {647, 1}];",
            "Null",
            ("Padding not implemented for PixelValue.",),
            None,
        ),
        (
            "PixelValue[hedy, {1, 0}];",
            "Null",
            ("Padding not implemented for PixelValue.",),
            None,
        ),
        ("PixelValue[hedy, {1, 512}]", "{0.286275, 0.4, 0.423529}", None, None),
        (
            "PixelValue[hedy, {1, 801}];",
            "Null",
            ("Padding not implemented for PixelValue.",),
            None,
        ),
        #
        # Composition
        #
        (
            "i = Image[{{0, 0.5, 0.2, 0.1, 0.9}, {1.0, 0.1, 0.3, 0.8, 0.6}}];",
            "Null",
            None,
            None,
        ),
        ("ImageAdd[i, 0.2, i, 0.1]", "-Image-", None, None),
        (
            "ImageAdd[i, x]",
            "ImageAdd[-Image-, x]",
            ("Expecting a number, image, or graphics instead of x.",),
            None,
        ),
        ("ImageMultiply[i, 0.2, i, 0.1]", "-Image-", None, None),
        (
            "ImageMultiply[i, x]",
            "ImageMultiply[-Image-, x]",
            ("Expecting a number, image, or graphics instead of x.",),
            None,
        ),
        (
            'ein = Import["ExampleData/Einstein.jpg"]; noise = RandomImage[{0.7, 1.3}, ImageDimensions[ein]];ImageMultiply[noise, ein]',
            "-Image-",
            None,
            "Multiply Image by random noise",
        ),
        ("ImageSubtract[i, 0.2, i, 0.1]", "-Image-", None, None),
        (
            "ImageSubtract[i, x]",
            "ImageSubtract[-Image-, x]",
            ("Expecting a number, image, or graphics instead of x.",),
            None,
        ),
        #
        # Random
        #
        ("RandomImage[0.5]", "-Image-", None, None),
        ("RandomImage[{0.1, 0.9}]", "-Image-", None, None),
        ("RandomImage[0.9, {400, 600}]", "-Image-", None, None),
        ("RandomImage[{0.1, 0.5}, {400, 600}]", "-Image-", None, None),
        (
            'RandomImage[{0.1, 0.5}, {400, 600}, ColorSpace -> "RGB"]',
            "-Image-",
            None,
            None,
        ),
        #
        # Geometry
        #
        (
            "ein == ImageReflect[ein, Left -> Left] == ImageReflect[ein, Right -> Right] == ImageReflect[ein, Top -> Top] == ImageReflect[ein, Bottom -> Bottom]",
            "True",
            None,
            None,
        ),
        (
            "ImageReflect[ein, Left -> Right] == ImageReflect[ein, Right -> Left] == ImageReflect[ein, Left] == ImageReflect[ein, Right]",
            "True",
            None,
            None,
        ),
        (
            "ImageReflect[ein, Bottom -> Top] == ImageReflect[ein, Top -> Bottom] == ImageReflect[ein, Top] == ImageReflect[ein, Bottom]",
            "True",
            None,
            None,
        ),
        (
            "ImageReflect[ein, Left -> Top] == ImageReflect[ein, Right -> Bottom]",
            "True",
            None,
            "Transpose",
        ),
        (
            "ImageReflect[ein, Left -> Bottom] == ImageReflect[ein, Right -> Top]",
            "True",
            None,
            "Anti-Transpose",
        ),
        (
            "ImageReflect[ein, x -> Top]",
            "ImageReflect[-Image-, x -> Top]",
            ("x -> Top is not a valid 2D reflection specification.",),
            None,
        ),
        (
            "ImageRotate[ein, ein]",
            "ImageRotate[-Image-, -Image-]",
            (
                "Angle -Image- should be a real number, one of Top, Bottom, Left, Right, or a rule from one to another.",
            ),
            None,
        ),
    ],
)
def test_private_doctest(str_expr, str_expected, msgs, assert_failure_msg):
    check_evaluation(
        str_expr,
        str_expected,
        hold_expected=True,
        expected_messages=msgs,
        failure_message=assert_failure_msg,
    )
