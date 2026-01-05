# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.forms.
"""

from test.helper import check_evaluation, session

import pytest


@pytest.mark.parametrize(
    ("expr", "form", "head", "subhead"),
    [
        ("x", "InputForm", "InterpretationBox", "StyleBox"),
        ("x", "OutputForm", "InterpretationBox", "PaneBox"),
        ("x", "TeXForm", "InterpretationBox", "String"),
        ("x", "StandardForm", "TagForm", "FormBox"),
        ("x", "FullForm", "TagBox", "StyleBox"),
    ],
)
@pytest.mark.xfail
def test_makeboxes_form(expr, form, head, subhead):
    """
    Check the structure of the result of MakeBoxes
    on expressions with different forms.
    """
    expr = session.evaluate("MakeBoxes[{form}[{expr}]]")
    assert expr.get_head_name() == f"System`{head}"
    assert expr.elements[0].get_head_name() == f"System`{subhead}"


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("BaseForm[0, 2]", None, "0_2", None),
        ("BaseForm[0.0, 2]", None, "0.0_2", None),
        ("BaseForm[N[Pi, 30], 16]", None, "3.243f6a8885a308d313198a2e_16", None),
        ("InputForm[2 x ^ 2 + 4z!]", None, "2*x^2 + 4*z!", None),
        (r'InputForm["\$"]', None, r'"\\$"', None),
        ## Undocumented edge cases
        ("NumberForm[Pi, 20]", None, "Pi", None),
        ("NumberForm[2/3, 10]", None, "2 / 3", None),
        ## No n or f
        ("NumberForm[N[Pi]]", None, "3.14159", None),
        ("NumberForm[N[Pi, 20]]", None, "3.1415926535897932385", None),
        ("NumberForm[14310983091809]", None, "14310983091809", None),
        ## Zero case
        ("z0 = 0.0;z1 = 0.0000000000000000000000000000;", None, "Null", None),
        ("NumberForm[{z0, z1}, 10]", None, "{0., 0.×10^-28}", None),
        ("NumberForm[{z0, z1}, {10, 4}]", None, "{0.0000, 0.0000×10^-28}", None),
        ("z0=.;z1=.;", None, "Null", None),
        ## Trailing zeros
        ("NumberForm[1.0, 10]", None, "1.", None),
        ("NumberForm[1.000000000000000000000000, 10]", None, "1.000000000", None),
        ("NumberForm[1.0, {10, 8}]", None, "1.00000000", None),
        ("NumberForm[N[Pi, 33], 33]", None, "3.14159265358979323846264338327950", None),
        ## Correct rounding
        ("NumberForm[0.645658509, 6]", None, "0.645659", "sympy/issues/11472"),
        ("NumberForm[N[1/7], 30]", None, "0.1428571428571428", "sympy/issues/11472"),
        ## Integer case
        (
            "NumberForm[{0, 2, -415, 83515161451}, 5]",
            None,
            "{0, 2, -415, 83515161451}",
            None,
        ),
        (
            "NumberForm[{2^123, 2^123.}, 4, ExponentFunction -> ((#1) &)]",
            None,
            "{10633823966279326983230456482242756608, 1.063×10^37}",
            None,
        ),
        ("NumberForm[{0, 10, -512}, {10, 3}]", None, "{0.000, 10.000, -512.000}", None),
        ## Check arguments
        (
            "NumberForm[1.5, -4]",
            (
                "Formatting specification -4 should be a positive integer or a pair of positive integers.",
            ),
            "1.5",
            None,
        ),
        (
            "NumberForm[1.5, {1.5, 2}]",
            (
                "Formatting specification {1.5, 2} should be a positive integer or a pair of positive integers.",
            ),
            "1.5",
            None,
        ),
        (
            "NumberForm[1.5, {1, 2.5}]",
            (
                "Formatting specification {1, 2.5} should be a positive integer or a pair of positive integers.",
            ),
            "1.5",
            None,
        ),
        ## Right padding
        (
            "NumberForm[153., 2]",
            (
                "In addition to the number of digits requested, one or more zeros will appear as placeholders.",
            ),
            "150.",
            None,
        ),
        ("NumberForm[0.00125, 1]", None, "0.001", None),
        (
            "NumberForm[10^5 N[Pi], {5, 3}]",
            (
                "In addition to the number of digits requested, one or more zeros will appear as placeholders.",
            ),
            "314160.000",
            None,
        ),
        ("NumberForm[10^5 N[Pi], {6, 3}]", None, "314159.000", None),
        ("NumberForm[10^5 N[Pi], {6, 10}]", None, "314159.0000000000", None),
        (
            'NumberForm[1.0000000000000000000, 10, NumberPadding -> {"X", "Y"}]',
            None,
            "X1.000000000",
            None,
        ),
        ## Check options
        ## DigitBlock
        (
            "NumberForm[12345.123456789, 14, DigitBlock -> 3]",
            None,
            "12,345.123 456 789",
            None,
        ),
        (
            "NumberForm[12345.12345678, 14, DigitBlock -> 3]",
            None,
            "12,345.123 456 78",
            None,
        ),
        (
            "NumberForm[N[10^ 5 Pi], 15, DigitBlock -> {4, 2}]",
            None,
            "31,4159.26 53 58 97 9",
            None,
        ),
        (
            "NumberForm[1.2345, 3, DigitBlock -> -4]",
            (
                "Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.",
            ),
            "1.2345",
            None,
        ),
        (
            "NumberForm[1.2345, 3, DigitBlock -> x]",
            (
                "Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.",
            ),
            "1.2345",
            None,
        ),
        (
            "NumberForm[1.2345, 3, DigitBlock -> {x, 3}]",
            (
                "Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.",
            ),
            "1.2345",
            None,
        ),
        (
            "NumberForm[1.2345, 3, DigitBlock -> {5, -3}]",
            (
                "Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.",
            ),
            "1.2345",
            None,
        ),
        ## ExponentFunction
        (
            "NumberForm[12345.123456789, 14, ExponentFunction -> ((#) &)]",
            None,
            "1.2345123456789×10^4",
            None,
        ),
        (
            "NumberForm[12345.123456789, 14, ExponentFunction -> (Null&)]",
            None,
            "12345.123456789",
            None,
        ),
        ("y = N[Pi^Range[-20, 40, 15]];", None, "Null", None),
        (
            "NumberForm[y, 10, ExponentFunction -> (3 Quotient[#, 3] &)]",
            None,
            "{114.0256472×10^-12, 3.267763643×10^-3, 93.64804748×10^3, 2.683779414×10^12, 76.91214221×10^18}",
            None,
        ),
        (
            "NumberForm[y, 10, ExponentFunction -> (Null &)]",
            (
                "In addition to the number of digits requested, one or more zeros will appear as placeholders.",
                "In addition to the number of digits requested, one or more zeros will appear as placeholders.",
            ),
            "{0.0000000001140256472, 0.003267763643, 93648.04748, 2683779414000., 76912142210000000000.}",
            None,
        ),
        ## ExponentStep
        (
            "NumberForm[10^8 N[Pi], 10, ExponentStep -> 3]",
            None,
            "314.1592654×10^6",
            None,
        ),
        (
            "NumberForm[1.2345, 3, ExponentStep -> x]",
            ("Value of option ExponentStep -> x is not a positive integer.",),
            "1.2345",
            None,
        ),
        (
            "NumberForm[1.2345, 3, ExponentStep -> 0]",
            ("Value of option ExponentStep -> 0 is not a positive integer.",),
            "1.2345",
            None,
        ),
        (
            "NumberForm[y, 10, ExponentStep -> 6]",
            None,
            "{114.0256472×10^-12, 3267.763643×10^-6, 93648.04748, 2.683779414×10^12, 76.91214221×10^18}",
            None,
        ),
        ## NumberFormat
        (
            "NumberForm[y, 10, NumberFormat -> (#1 &)]",
            None,
            "{1.140256472, 0.003267763643, 93648.04748, 2.683779414, 7.691214221}",
            None,
        ),
        ## NumberMultiplier
        (
            "NumberForm[1.2345, 3, NumberMultiplier -> 0]",
            ("Value for option NumberMultiplier -> 0 is expected to be a string.",),
            "1.2345",
            None,
        ),
        (
            'NumberForm[N[10^ 7 Pi], 15, NumberMultiplier -> "*"]',
            None,
            "3.14159265358979*10^7",
            None,
        ),
        ## NumberPoint
        ('NumberForm[1.2345, 5, NumberPoint -> ","]', None, "1,2345", None),
        (
            "NumberForm[1.2345, 3, NumberPoint -> 0]",
            ("Value for option NumberPoint -> 0 is expected to be a string.",),
            "1.2345",
            None,
        ),
        ## NumberPadding
        ("NumberForm[1.41, {10, 5}]", None, "1.41000", None),
        (
            'NumberForm[1.41, {10, 5}, NumberPadding -> {"", "X"}]',
            None,
            "1.41XXX",
            None,
        ),
        (
            'NumberForm[1.41, {10, 5}, NumberPadding -> {"X", "Y"}]',
            None,
            "XXXXX1.41YYY",
            None,
        ),
        (
            'NumberForm[1.41, 10, NumberPadding -> {"X", "Y"}]',
            None,
            "XXXXXXXX1.41",
            None,
        ),
        (
            "NumberForm[1.2345, 3, NumberPadding -> 0]",
            (
                "Value for option NumberPadding -> 0 should be a string or a pair of strings.",
            ),
            "1.2345",
            None,
        ),
        (
            'NumberForm[1.41, 10, NumberPadding -> {"X", "Y"}, NumberSigns -> {"-------------", ""}]',
            None,
            "XXXXXXXXXXXXXXXXXXXX1.41",
            None,
        ),
        (
            'NumberForm[{1., -1., 2.5, -2.5}, {4, 6}, NumberPadding->{"X", "Y"}]',
            None,
            "{X1.YYYYYY, -1.YYYYYY, X2.5YYYYY, -2.5YYYYY}",
            None,
        ),
        ## NumberSeparator
        (
            'NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> " "]',
            None,
            "314 159.265 358 979",
            None,
        ),
        (
            'NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> {" ", ","}]',
            None,
            "314 159.265,358,979",
            None,
        ),
        (
            'NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> {",", " "}]',
            None,
            "314,159.265 358 979",
            None,
        ),
        (
            'NumberForm[N[10^ 7 Pi], 15, DigitBlock -> 3, NumberSeparator -> {",", " "}]',
            None,
            "3.141 592 653 589 79×10^7",
            None,
        ),
        (
            "NumberForm[1.2345, 3, NumberSeparator -> 0]",
            (
                "Value for option NumberSeparator -> 0 should be a string or a pair of strings.",
            ),
            "1.2345",
            None,
        ),
        ## NumberSigns
        ('NumberForm[1.2345, 5, NumberSigns -> {"-", "+"}]', None, "+1.2345", None),
        ('NumberForm[-1.2345, 5, NumberSigns -> {"- ", ""}]', None, "- 1.2345", None),
        (
            "NumberForm[1.2345, 3, NumberSigns -> 0]",
            (
                "Value for option NumberSigns -> 0 should be a pair of strings or two pairs of strings.",
            ),
            "1.2345",
            None,
        ),
        ## SignPadding
        (
            'NumberForm[1.234, 6, SignPadding -> True, NumberPadding -> {"X", "Y"}]',
            None,
            "XXX1.234",
            None,
        ),
        (
            'NumberForm[-1.234, 6, SignPadding -> True, NumberPadding -> {"X", "Y"}]',
            None,
            "-XX1.234",
            None,
        ),
        (
            'NumberForm[-1.234, 6, SignPadding -> False, NumberPadding -> {"X", "Y"}]',
            None,
            "XX-1.234",
            None,
        ),
        (
            'NumberForm[-1.234, {6, 4}, SignPadding -> False, NumberPadding -> {"X", "Y"}]',
            None,
            "X-1.234Y",
            None,
        ),
        ("NumberForm[34, ExponentFunction->(Null&)]", None, "34", "1-arg, Option case"),
        ## zero padding integer x0.0 case
        ("NumberForm[50.0, {5, 1}]", None, "50.0", None),
        ("NumberForm[50, {5, 1}]", None, "50.0", None),
        ## Rounding correctly
        ("NumberForm[43.157, {10, 1}]", None, "43.2", None),
        (
            'NumberForm[43.15752525, {10, 5}, NumberSeparator -> ",", DigitBlock -> 1]',
            None,
            "4,3.1,5,7,5,3",
            None,
        ),
        ("NumberForm[80.96, {16, 1}]", None, "81.0", None),
        ("NumberForm[142.25, {10, 1}]", None, "142.3", None),
        (
            '{"hi","you"} //InputForm //TeXForm',
            None,
            "\\left\\{\\text{``hi''}, \\text{``you''}\\right\\}",
            None,
        ),
        ("a=.;b=.;c=.;TeXForm[a+b*c]", None, "a+b c", None),
        ("TeXForm[InputForm[a+b*c]]", None, r"a\text{ + }b*c", None),
        ("TableForm[{}]", None, "", None),
        (
            "{{2*a, 0},{0,0}}//MatrixForm",
            None,
            "2 \u2062 a   0\n\n0       0\n",
            "Issue #182",
        ),
    ],
)
def test_private_doctests_output(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
