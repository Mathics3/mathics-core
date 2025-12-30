import os
from test.helper import check_evaluation, session

import pytest
import yaml

from mathics.core.symbols import Symbol

# from mathics.core.builtin import BoxConstruct, Predefined


#
#  Aim of the tests:
#
# In these tests, we check that the current behavior of makeboxes does not change
# without noticing that it could affect compatibility with WL and with
# mathics-django. Also looking at some issues in the current behavior regarding
# the WL standard (for instance, how to represent $a^(b/c)$) and the Mathics
# own implementation (BoxError raising in some simple conditions).
# These test should be updated as we fix pending issues.


# Set this to 0 in case mathml tests must be considered xfail. With True, ensures the
# compatibility with the current mathics-django branch.

MATHML_STRICT = (
    int(os.environ.get("MATHML_STRICT", "1")) == 1
)  # To set to False, set ENV var to "0"


# This dict contains all the tests. The main key is an expression to be evaluated and
# formatted. For each expression, we have a base message, and tests for each output box
# mode ("text", "mathml" and "tex"). On each mode, we have a dict for the different formats.
# If the value associated with a format is a string and the message does not
# finish with "- Fragile!", the test is considered mandatory,
# (not xfail), and the assert message is the base message.
# If there is a tuple instead, the test is against the first element of the tuple,
# and allowed to fail. In this case, the assert message is the
# concatenation of the base message and the second element of the tuple.

PATH = os.path.dirname(__file__) + os.path.sep

with open(PATH + "format_tests.yaml", "r") as src:
    all_test = yaml.safe_load(src)


def load_tests(key):
    """
    This function takes the full set of tests, pick the ones corresponding to one
    of the final formats ("text", "latex", "mathml") and produce two list:
    the first with the mandatory tests, and the other with "fragile" tests
    """
    global all_tests
    global MATHML_STRICT

    def is_fragile(assert_msg: str) -> bool:
        """
        Return True if assert_msg indicates we have a fragile test, and False otherwise
        """
        return assert_msg.endswith("Fragile!")

    mandatory_tests = []
    fragile_tests = []
    for expr in all_test:
        base_msg = all_test[expr]["msg"]
        expected_fmt = all_test[expr].get(key, None)
        test_is_fragile = is_fragile(base_msg)

        # Some fragile tests have been commented out.
        # If we have a fragile test where the output has not
        # been adjusted, then skip it.
        #
        if expected_fmt is None:
            assert is_fragile(base_msg), [expr, key, base_msg]
            continue

        for form in expected_fmt:
            tst = expected_fmt[form]
            form_is_fragile = test_is_fragile
            must_be = False
            if not isinstance(tst, str):
                tst, extra_msg = tst
                if len(extra_msg) > 7 and extra_msg[:7] == "must be":
                    must_be = True
                elif is_fragile(extra_msg):
                    form_is_fragile = True
                msg = base_msg + " - " + extra_msg
            else:
                msg = base_msg

            # discard Fragile for "text", "latex" or if
            # MATHML_STRICT is True
            if key != "mathml" or MATHML_STRICT:
                form_is_fragile = False
            full_test = (expr, tst, Symbol(form), msg)
            if form_is_fragile or must_be:
                fragile_tests.append(full_test)
            else:
                mandatory_tests.append(full_test)

    return mandatory_tests, fragile_tests


mandatory_tests, fragile_tests = load_tests("text")

if fragile_tests:

    @pytest.mark.parametrize(
        ("str_expr", "str_expected", "form", "msg"),
        fragile_tests,
    )
    @pytest.mark.xfail
    def test_makeboxes_text_fragile(str_expr, str_expected, form, msg):
        result = session.evaluate(str_expr)
        format_result = result.format(session.evaluation, form)
        if msg:
            assert (
                format_result.boxes_to_text(evaluation=session.evaluation)
                == str_expected
            ), msg
        else:
            strresult = format_result.boxes_to_text(evaluation=session.evaluation)
            assert strresult == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "form", "msg"),
    mandatory_tests,
)
def test_makeboxes_text(str_expr, str_expected, form, msg):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, form)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_text(evaluation=session.evaluation)
        assert strresult == str_expected


mandatory_tests, fragile_tests = load_tests("latex")

if fragile_tests:

    @pytest.mark.parametrize(
        ("str_expr", "str_expected", "form", "msg"),
        fragile_tests,
    )
    @pytest.mark.xfail
    def test_makeboxes_tex_fragile(str_expr, str_expected, form, msg):
        result = session.evaluate(str_expr)
        format_result = result.format(session.evaluation, form)
        if msg:
            assert (
                format_result.boxes_to_tex(
                    show_string_characters=False, evaluation=session.evaluation
                ).strip()
                == str_expected.strip()
            ), msg
        else:
            strresult = format_result.boxes_to_tex(evaluation=session.evaluation)
            assert strresult.strip() == str_expected.strip()


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "form", "msg"),
    mandatory_tests,
)
def test_makeboxes_tex(str_expr, str_expected, form, msg):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, form)
    if msg:
        assert (
            format_result.boxes_to_tex(
                show_string_characters=False, evaluation=session.evaluation
            ).strip()
            == str_expected.strip()
        ), msg
    else:
        strresult = format_result.boxes_to_text(evaluation=session.evaluation).strip()
        assert strresult == str_expected


mandatory_tests, fragile_tests = load_tests("mathml")

if fragile_tests:

    @pytest.mark.parametrize(
        ("str_expr", "str_expected", "form", "msg"),
        fragile_tests,
    )
    @pytest.mark.xfail
    def test_makeboxes_mathml_fragile(str_expr, str_expected, form, msg):
        result = session.evaluate(str_expr)
        format_result = result.format(session.evaluation, form)
        if msg:
            assert (
                format_result.boxes_to_mathml(evaluation=session.evaluation)
                == str_expected
            ), msg
        else:
            strresult = format_result.boxes_to_mathml(evaluation=session.evaluation)
            assert strresult == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "form", "msg"),
    mandatory_tests,
)
def test_makeboxes_mathml(str_expr, str_expected, form, msg):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, form)
    if msg:
        assert (
            format_result.boxes_to_mathml(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_mathml(evaluation=session.evaluation)
        assert strresult == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            "OutputForm[Complex[2.0 ^ 40, 3]]",
            "1.09951×10^12 + 3. I",
            "OutputForm Complex",
        ),
        (
            "InputForm[Complex[2.0 ^ 40, 3]]",
            "1.099511627776*^12 + 3.*I",
            "InputForm Complex",
        ),
    ],
)
def test_format_private_doctests(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            (
                'Format[r[items___]] := Infix[If[Length[{items}] > 1, {items}, {ab}], "~"];'
                "r[1, 2, 3]"
            ),
            None,
            "1 ~ 2 ~ 3",
            None,
        ),
        ("r[1]", None, "ab", None),
        (None, None, None, None),
    ],
)
def test_private_doctests_layout(str_expr, msgs, str_expected, fail_msg):
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
