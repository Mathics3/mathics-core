import pytest

from .helper import check_evaluation


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        ("ClearAll[a, b]", None, None),
        (
            "DiagonalMatrix[a + b]",
            "DiagonalMatrix[a + b]",
            "argument needs to be a list",
        ),
    ],
)
def test_diagonal_matrix(str_expr: str, str_expected: str, fail_msg: str):
    check_evaluation(str_expr, str_expected, fail_msg)
