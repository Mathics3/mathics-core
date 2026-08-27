from test.helper import check_evaluation

import pytest

from mathics.core.builtin import check_requires_list


def test_canonical_sort():
    check_evaluation(
        "Sort[{F[2], ByteArray[{2}]}]",
        "{ByteArray[<1>], F[2]}",
        hold_expected=True,
    )
    check_evaluation(
        r"Sort[Table[IntegerDigits[2^n], {n, 10}]]",
        r"{{2}, {4}, {8}, {1, 6}, {3, 2}, {6, 4}, {1, 2, 8}, {2, 5, 6}, {5, 1, 2}, {1, 0, 2, 4}}",
    )
    check_evaluation(
        r"SortBy[Table[IntegerDigits[2^n], {n, 10}], First]",
        r"{{1, 6}, {1, 2, 8}, {1, 0, 2, 4}, {2}, {2, 5, 6}, {3, 2}, {4}, {5, 1, 2}, {6, 4}, {8}}",
    )


# FIXME: come up with an example that doesn't require skimage.
@pytest.mark.skipif(
    not check_requires_list(["skimage"]),
    reason="Right now need scikit-image for this to work",
)
def test_canonical_sort_images():
    check_evaluation(
        r'Sort[{Import["ExampleData/Einstein.jpg"], 5}]',
        r'{5, Import["ExampleData/Einstein.jpg"]}',
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Sort[{x_, y_}, PatternsOrderedQ]", None, "{x_, y_}", None),
    ],
)
def test_SortPatterns(str_expr, msgs, str_expected, fail_msg):
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
