from .helper import check_evaluation, session
import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        (
            "DiagonalMatrix[a + b]",
            "DiagonalMatrix[a + b]",
            "Leaves unchanged? Adapted from #> code that was in tensor.py",
        ),
    ],
)
def test_diagonal_matrix(str_expr: str, str_expected: str, fail_msg: str):
    result = session.evaluate(f"ToString[{str_expr}]").value
    print("result:", result)
    assert result == str_expected, fail_msg
