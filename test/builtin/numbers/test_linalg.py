# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.linalg
"""

from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Det",
            "1 argument is",
        ),
    ],
)
def test_arg_count_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg", "warnings"),
    [
        (None, None, None, None),
        (
            "Inverse[{{0, 2},{2, 0}}]",
            "{{0, 1 / 2},{1 / 2, 0}}",
            "",
            tuple(),
        ),
        (
            "Inverse[{{0, 2.},{2, 0}}]",
            "{{0, .5},{.5, 0}}",
            "",
            tuple(),
        ),
        (
            "Inverse[{{0, 2., 0},{2, 0, 0}, {0, 0, a}}]",
            "{{0, .5, 0},{.5, 0, 0},{0, 0, 1. / a}}",
            "",
            tuple(),
        ),
        # Multiplying a symbolic matrix by its inverse does not
        # produces the identity in general
        (
            "Inverse[{{a, b},{c, d}}].{{a, b},{c, d}}",
            (
                "{{a d / (a d - b c) - b c / (a d - b c), 0}, "
                "{0, a d / (a d - b c) - b c / (a d - b c)}}"
            ),
            "2x2 general inverse",
            tuple(),
        ),
        (
            "Inverse[{{a, b},{c, d}}].{{a, b},{c, d}}//Simplify",
            "{{1, 0},{0, 1}}",
            "2x2 general inverse",
            tuple(),
        ),
        (
            "Inverse[{{g[a], g[b]},{g[c], g[d]}}].{{g[a], g[b]},{g[c], g[d]}}//Simplify",
            ("{{1, 0},{0, 1}}"),
            "2x2 general inverse",
            tuple(),
        ),
        (
            "Inverse[{{1,1},{1,1}}]",
            "Inverse[{{1, 1},{1, 1}}]",
            "singular matrix",
            ("The matrix {{1, 1}, {1, 1}} is singular.",),
        ),
        (
            "Inverse[{{1, 1, 1},{1, 1, 2}}]",
            "Inverse[{{1, 1, 1},{1, 1, 2}}]",
            "singular matrix",
            (
                "Argument {{1, 1, 1}, {1, 1, 2}} at position 1 "
                "is not a non-empty square matrix.",
            ),
        ),
        (
            "Inverse[{{{1}, {1}},{{1}, {2}}}]",
            "Inverse[{{{1}, {1}},{{1}, {2}}}]",
            "singular matrix",
            (
                "Argument {{{1}, {1}}, {{1}, {2}}} at position 1 "
                "is not a non-empty square matrix.",
            ),
        ),
        (
            "Inverse[{{1, 0, 0}, {0, Sqrt[3]/2, 1/2}, {0,-1 / 2, Sqrt[3]/2}}]",
            "{{1, 0, 0}, {0, Sqrt[3] / 2, -1 / 2}, {0, 1 / 2, Sqrt[3] / 2}}",
            None,
            None,
        ),
    ],
)
def test_inverse(str_expr, str_expected, fail_msg, warnings):
    check_evaluation(
        str_expr, str_expected, failure_message="", expected_messages=warnings
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "Eigenvalues[{{1, 0}, {0}}]",
            (
                "Argument {{1, 0}, {0}} at position 1 is not a non-empty rectangular matrix.",
            ),
            "Eigenvalues[{{1, 0}, {0}}]",
            None,
        ),
        (
            "Eigenvectors[{{-2, 1, -1}, {-3, 2, 1}, {-1, 1, 0}}]",
            None,
            "{{1, 7, 3}, {1, 1, 0}, {0, 0, 0}}",
            None,
        ),
        ## Inconsistent system - ideally we'd print a different message
        (
            "LeastSquares[{{1, 1, 1}, {1, 1, 1}}, {1, 0}]",
            ("Solving for underdetermined system not implemented.",),
            "LeastSquares[{{1, 1, 1}, {1, 1, 1}}, {1, 0}]",
            None,
        ),
        (
            "LeastSquares[{1, {2}}, {1, 2}]",
            ("Argument {1, {2}} at position 1 is not a non-empty rectangular matrix.",),
            "LeastSquares[{1, {2}}, {1, 2}]",
            None,
        ),
        (
            "LeastSquares[{{1, 2}, {3, 4}}, {1, {2}}]",
            ("Argument {1, {2}} at position 2 is not a non-empty rectangular matrix.",),
            "LeastSquares[{{1, 2}, {3, 4}}, {1, {2}}]",
            None,
        ),
        (
            "LinearSolve[{1, {2}}, {1, 2}]",
            ("Argument {1, {2}} at position 1 is not a non-empty rectangular matrix.",),
            "LinearSolve[{1, {2}}, {1, 2}]",
            None,
        ),
        (
            "LinearSolve[{{1, 2}, {3, 4}}, {1, {2}}]",
            ("Argument {1, {2}} at position 2 is not a non-empty rectangular matrix.",),
            "LinearSolve[{{1, 2}, {3, 4}}, {1, {2}}]",
            None,
        ),
        ("MatrixExp[{{a, 0}, {0, b}}]", None, "{{E ^ a, 0}, {0, E ^ b}}", None),
        (
            "MatrixExp[{{1, 0}, {0}}]",
            (
                "Argument {{1, 0}, {0}} at position 1 is not a non-empty rectangular matrix.",
            ),
            "MatrixExp[{{1, 0}, {0}}]",
            None,
        ),
        (
            "MatrixPower[{{0, x}, {0, 0}}, n]",
            None,
            "MatrixPower[{{0, x}, {0, 0}}, n]",
            None,
        ),
        (
            "MatrixPower[{{1, 0}, {0}}, 2]",
            (
                "Argument {{1, 0}, {0}} at position 1 is not a non-empty rectangular matrix.",
            ),
            "MatrixPower[{{1, 0}, {0}}, 2]",
            None,
        ),
        (
            "MatrixRank[{{1, 0}, {0}}]",
            (
                "Argument {{1, 0}, {0}} at position 1 is not a non-empty rectangular matrix.",
            ),
            "MatrixRank[{{1, 0}, {0}}]",
            None,
        ),
        (
            "NullSpace[{1, {2}}]",
            ("Argument {1, {2}} at position 1 is not a non-empty rectangular matrix.",),
            "NullSpace[{1, {2}}]",
            None,
        ),
        (
            "PseudoInverse[{1, {2}}]",
            ("Argument {1, {2}} at position 1 is not a non-empty rectangular matrix.",),
            "PseudoInverse[{1, {2}}]",
            None,
        ),
        (
            "QRDecomposition[{1, {2}}]",
            ("Argument {1, {2}} at position 1 is not a non-empty rectangular matrix.",),
            "QRDecomposition[{1, {2}}]",
            None,
        ),
        (
            "RowReduce[{{1, 0}, {0}}]",
            (
                "Argument {{1, 0}, {0}} at position 1 is not a non-empty rectangular matrix.",
            ),
            "RowReduce[{{1, 0}, {0}}]",
            None,
        ),
        (
            "SingularValueDecomposition[{{3/2, 2}, {5/2, 3}}]",
            ("Symbolic SVD is not implemented, performing numerically.",),
            (
                "{{{0.538954, 0.842335}, {0.842335, -0.538954}}, "
                "{{4.63555, 0.}, {0., 0.107862}}, "
                "{{0.628678, 0.777666}, {-0.777666, 0.628678}}}"
            ),
            None,
        ),
        (
            "SingularValueDecomposition[{1, {2}}]",
            ("Argument {1, {2}} at position 1 is not a non-empty rectangular matrix.",),
            "SingularValueDecomposition[{1, {2}}]",
            None,
        ),
        (
            "A = Array[a, {2,2}]; eigvals=Eigenvalues[A.ConjugateTranspose[A]]",
            None,
            (
                "{-Sqrt[(a[1, 1] Conjugate[a[1, 1]] + a[1, 2] Conjugate[a[1, 2]] + "
                "a[2, 1] Conjugate[a[2, 1]] + a[2, 2] Conjugate[a[2, 2]]) ^ 2 - "
                "4 (a[1, 1] Conjugate[a[1, 1]] + a[1, 2] Conjugate[a[1, 2]]) "
                "(a[2, 1] Conjugate[a[2, 1]] + a[2, 2] Conjugate[a[2, 2]]) + "
                "4 (a[1, 1] Conjugate[a[2, 1]] + a[1, 2] Conjugate[a[2, 2]]) "
                "(a[2, 1] Conjugate[a[1, 1]] + a[2, 2] Conjugate[a[1, 2]])] / 2 "
                "+ a[1, 1] Conjugate[a[1, 1]] / 2 + a[1, 2] Conjugate[a[1, 2]] / 2 + "
                "a[2, 1] Conjugate[a[2, 1]] / 2 + a[2, 2] Conjugate[a[2, 2]] / 2, "
                "Sqrt[(a[1, 1] Conjugate[a[1, 1]] + a[1, 2] Conjugate[a[1, 2]] + "
                "a[2, 1] Conjugate[a[2, 1]] + a[2, 2] Conjugate[a[2, 2]]) ^ 2 - "
                "4 (a[1, 1] Conjugate[a[1, 1]] + a[1, 2] Conjugate[a[1, 2]]) "
                "(a[2, 1] Conjugate[a[2, 1]] + a[2, 2] Conjugate[a[2, 2]]) + 4 "
                "(a[1, 1] Conjugate[a[2, 1]] + a[1, 2] Conjugate[a[2, 2]]) "
                "(a[2, 1] Conjugate[a[1, 1]] + a[2, 2] Conjugate[a[1, 2]])] / 2 + "
                "a[1, 1] Conjugate[a[1, 1]] / 2 + a[1, 2] Conjugate[a[1, 2]] / 2 + "
                "a[2, 1] Conjugate[a[2, 1]] / 2 + a[2, 2] Conjugate[a[2, 2]] / 2}"
            ),
            None,  # "Sympy issue #1156",
        ),
        (
            "eigvals[[1]] // FullSimplify",
            None,
            (
                "-Sqrt[(a[1, 1] Conjugate[a[1, 1]] + a[1, 2] Conjugate[a[1, 2]] + "
                "a[2, 1] Conjugate[a[2, 1]] + a[2, 2] Conjugate[a[2, 2]]) ^ 2 - "
                "4 a[1, 1] a[2, 2] Conjugate[a[1, 1]] Conjugate[a[2, 2]] - "
                "4 a[1, 2] a[2, 1] Conjugate[a[1, 2]] Conjugate[a[2, 1]] + "
                "4 a[1, 1] a[2, 2] Conjugate[a[1, 2]] Conjugate[a[2, 1]] + "
                "4 a[1, 2] a[2, 1] Conjugate[a[1, 1]] Conjugate[a[2, 2]]] / 2 + "
                "a[1, 1] Conjugate[a[1, 1]] / 2 + a[1, 2] Conjugate[a[1, 2]] / 2 + "
                "a[2, 1] Conjugate[a[2, 1]] / 2 + a[2, 2] Conjugate[a[2, 2]] / 2"
            ),
            None,  # "Sympy issue #1156",
        ),
        (
            "eigvals /. a[x_, y_] -> x+I*y",
            None,
            ("{10 - 3 Sqrt[11], 10 + 3 Sqrt[11]}"),
            None,  # "Sympy issue #1156",
        ),
    ],
)
def test_linalg(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected"),
    [
        (
            "RowReduce[{{1, 0, 4}, {2, 0, 3}, {2, 1, 2}}, Modulus -> 5]",
            None,
            "{{1, 0, 4}, {0, 1, 4}, {0, 0, 0}}",
        ),
        ("RowReduce[{{1, 1}, {1, 1}}, Modulus -> 2]", None, "{{1, 1}, {0, 0}}"),
        ("RowReduce[{{1/2, 1}, {1, 3}}, Modulus -> 3]", None, "{{1, 0}, {0, 1}}"),
        ("RowReduce[{{-1, 2}, {3, -4}}, Modulus -> 0]", None, "{{1, 0}, {0, 1}}"),
        ("NullSpace[{{1, 1}, {1, 1}}, Modulus -> 2]", None, "{{1, 1}}"),
        ("NullSpace[{{1, 1, 1}}, Modulus -> 7]", None, "{{6, 0, 1}, {6, 1, 0}}"),
        ("NullSpace[{{1, 0}, {0, 1}}, Modulus -> 3]", None, "{}"),
        (
            "NullSpace[{{1, 0, 4}, {2, 0, 3}, {2, 1, 2}}, Modulus -> 5]",
            None,
            "{{1, 1, 1}}",
        ),
        ("MatrixRank[{{1, 0, 4}, {2, 0, 3}, {2, 1, 2}}, Modulus -> 5]", None, "2"),
        ("MatrixRank[{{2, 4}, {6, 8}}, Modulus -> 2]", None, "0"),
        ("Inverse[{{1, 1}, {0, 1}}, Modulus -> 2]", None, "{{1, 1}, {0, 1}}"),
        ("Inverse[{{12, -2}, {1, 3}}, Modulus -> 5]", None, "{{1, 4}, {3, 4}}"),
        (
            "Head[Inverse[{{1, 1}, {1, 1}}, Modulus -> 2]]",
            ("The matrix {{1, 1}, {1, 1}} is singular.",),
            "Inverse",
        ),
        (
            "Head[Inverse[{{1, 2}, {3, 4}}, Modulus -> 2]]",
            ("The matrix {{1, 2}, {3, 4}} is singular.",),
            "Inverse",
        ),
        ("LinearSolve[{{1, 1}, {0, 1}}, {1, 0}, Modulus -> 2]", None, "{1, 0}"),
        (
            "LinearSolve[{{1, 1, 1}, {1, 2, 3}, {1, 4, 9}}, {1, 2, 3}, Modulus -> 47]",
            None,
            "{23, 2, 23}",
        ),
        ("LinearSolve[{{1, 1}, {1, 1}}, {1, 1}, Modulus -> 2]", None, "{1, 0}"),
        (
            "Head[LinearSolve[{{1, 1}, {1, 1}}, {1, 0}, Modulus -> 2]]",
            ("Linear equation encountered that has no solution.",),
            "LinearSolve",
        ),
        # Left unevaluated: a modulus that is not a prime, a symbolic entry,
        # and a denominator that is not invertible.
        (
            "Head[NullSpace[{{1, 2}, {3, 2}}, Modulus -> 6]]",
            None,
            "NullSpace",
        ),
        (
            "Head[MatrixRank[{{1, 2}, {3, 2}}, Modulus -> x]]",
            None,
            "MatrixRank",
        ),
        (
            "Head[RowReduce[{{a, 1}, {1, 3}}, Modulus -> 3]]",
            None,
            "RowReduce",
        ),
        (
            "Head[RowReduce[{{1/3, 1}, {1, 3}}, Modulus -> 3]]",
            None,
            "RowReduce",
        ),
    ],
)
def test_linalg_modulus(str_expr, msgs, str_expected):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        expected_messages=msgs,
    )


def test_linalg_modulus_random():
    """Check the modular results against their defining properties."""
    check_evaluation(
        "SeedRandom[42]; "
        "And @@ Table[Module[{m, p, ns, rr, rk, x},"
        "  m = RandomInteger[{-5, 5}, {6, 8}]; p = {2, 3, 7}[[Mod[k, 3] + 1]];"
        "  ns = NullSpace[m, Modulus -> p];"
        "  rr = RowReduce[m, Modulus -> p];"
        "  rk = MatrixRank[m, Modulus -> p];"
        "  x = LinearSolve[m, m . Range[8], Modulus -> p];"
        "  And["
        "    Length[ns] + rk == 8,"
        "    ns === {} || Union[Flatten[Mod[m . Transpose[ns], p]]] === {0},"
        "    Mod[m . x - m . Range[8], p] === Table[0, 6],"
        "    Count[rr, Except[{0 ..}]] == rk]],"
        "  {k, 30}]",
        "True",
    )
    check_evaluation(
        "SeedRandom[7]; "
        "And @@ Table[Module[{m, inv},"
        "  m = RandomInteger[{0, 6}, {5, 5}];"
        "  inv = Quiet[Inverse[m, Modulus -> 7]];"
        "  Head[inv] === Inverse || Mod[m . inv, 7] === IdentityMatrix[5]],"
        "  {k, 30}]",
        "True",
    )
