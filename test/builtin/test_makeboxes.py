# -*- coding: utf-8 -*-
import pytest
from test.helper import check_evaluation, session
from mathics_scanner.errors import IncompleteSyntaxError

# 15 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"MakeBoxes[1.4]", r"1.4`", None),
        (r"MakeBoxes[1.4`]", r"1.4`", None),
        (r"MakeBoxes[1.5`20]", r"1.5`20.", None),
        (r"MakeBoxes[1.4`20]", r"1.4`20.", None),
        (r"MakeBoxes[1.5``20]", r"1.5`20.1760912591", None),
        (r"MakeBoxes[-1.4]", r'RowBox[{"-", 1.4`}]', None),
        (r"MakeBoxes[34.*^3]", r"34000.`", None),
        (r"MakeBoxes[0`]", r"0.`", None),
        (r"MakeBoxes[0`3]", r"0", None),
        (r"MakeBoxes[0``30]", r"0.``30.", None),
        (r"MakeBoxes[0.`]", r"0.`", None),
        (r"MakeBoxes[0.`3]", r"0.`", None),
        (r"MakeBoxes[0.``30]", r"0.``30.", None),
        (r"MakeBoxes[14]", r"14", None),
        (r"MakeBoxes[-14]", r'RowBox[{"-", 14}]', None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_real(str_expr, str_expected, msg):
    """
    # TODO: Constructing boxes from Real
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 3 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"\(x \/ y + z\)", r'RowBox[{FractionBox["x", "y"], "+", "z"}]', None),
        (
            r"\(x \/ (y + z)\)",
            r'FractionBox["x", RowBox[{"(", RowBox[{"y", "+", "z"}], ")"}]]',
            None,
        ),
        (r"\( \@ a + b \)", r'RowBox[{SqrtBox["a"], "+", "b"}]', None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_precedence(str_expr, str_expected, msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 3 tests
# TODO: Convert operators to appropriate representations e.g. 'Plus' to '+'
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"\(a + b\)", r'RowBox[{"a", "+", "b"}]', None),
        (
            r"\(TraditionalForm \` a + b\)",
            r'FormBox[RowBox[{"a", "+", "b"}], TraditionalForm]',
            None,
        ),
        (r"\(x \/ \(y + z\)\)", r'FractionBox["x", RowBox[{"y", "+", "z"}]]', None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_representation(str_expr, str_expected, msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


#  5 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r"\(c (1 + x)\)",
            r'RowBox[{"c", RowBox[{"(", RowBox[{"1", "+", "x"}], ")"}]}]',
            r"FIXME: Don't insert spaces with brackets",
        ),
        (r"\!\(x \^ 2\)", r"x ^ 2", "Required MakeExpression"),
        #
        (r"FullForm[%]", r'Power["x", "2"]', "Required MakeExpression"),
        #
        (r"MakeBoxes[1 + 1]", r'RowBox[{"1", "+", "1"}]', "TODO: Fix Infix operators"),
        #
        (
            r"\( a, b \)",
            r'RowBox[{"a", ",", "b"}]',
            "TODO: Parsing of special characters (like commas)",
        ),
    ],
)
@pytest.mark.xfail
def test_makeboxes_others(str_expr, str_expected, msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )
