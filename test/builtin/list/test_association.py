# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.list.constructing
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            "assoc=<|a -> x, b -> y, c -> <|d -> t|>|>",
            None,
            "<|a -> x, b -> y, c -> <|d -> t|>|>",
            None,
        ),
        ('assoc["s"]', None, "Missing[KeyAbsent, s]", None),
        (
            "assoc=<|a -> x, b + c -> y, {<|{}|>, a -> {z}}|>",
            None,
            "<|a -> {z}, b + c -> y|>",
            None,
        ),
        ("assoc[a]", None, "{z}", None),
        ('assoc=<|"x" -> 1, {y} -> 1|>', None, "<|x -> 1, {y} -> 1|>", None),
        ('assoc["x"]', None, "1", None),
        (
            "<|<|a -> v|> -> x, <|b -> y, a -> <|c -> z|>, {}, <||>|>, {d}|>[c]",
            None,
            "Association[Association[a -> v] -> x, Association[b -> y, a -> Association[c -> z], {}, Association[]], {d}][c]",
            None,
        ),
        (
            "<|<|a -> v|> -> x, <|b -> y, a -> <|c -> z|>, {d}|>, {}, <||>|>[a]",
            None,
            "Association[Association[a -> v] -> x, Association[b -> y, a -> Association[c -> z], {d}], {}, Association[]][a]",
            None,
        ),
        (
            "assoc=<|<|a -> v|> -> x, <|b -> y, a -> <|c -> z, {d}|>, {}, <||>|>, {}, <||>|>",
            None,
            "<|<|a -> v|> -> x, b -> y, a -> Association[c -> z, {d}]|>",
            None,
        ),
        ("assoc[a]", None, "Association[c -> z, {d}]", None),
        #        (
        #            "<|a -> x, b -> y, c -> <|d -> t|>|> // ToBoxes",
        #            None,
        #            "RowBox[{<|, RowBox[{RowBox[{a, ->, x}], ,, RowBox[{b, ->, y}], ,, RowBox[{c, ->, RowBox[{<|, RowBox[{d, ->, t}], |>}]}]}], |>}]",
        #            None,
        #        ),
        #        (
        #            "Association[a -> x, b -> y, c -> Association[d -> t, Association[e -> u]]] // ToBoxes",
        #            None,
        #            "RowBox[{<|, RowBox[{RowBox[{a, ->, x}], ,, RowBox[{b, ->, y}], ,, RowBox[{c, ->, RowBox[{<|, RowBox[{RowBox[{d, ->, t}], ,, RowBox[{e, ->, u}]}], |>}]}]}], |>}]",
        #            None,
        #        ),
        ("Keys[a -> x]", None, "a", None),
        (
            "Keys[{a -> x, a -> y, {a -> z, <|b -> t|>, <||>, {}}}]",
            None,
            "{a, a, {a, {b}, {}, {}}}",
            None,
        ),
        (
            "Keys[{a -> x, a -> y, <|a -> z, {b -> t}, <||>, {}|>}]",
            None,
            "{a, a, {a, b}}",
            None,
        ),
        (
            "Keys[<|a -> x, a -> y, <|a -> z, <|b -> t|>, <||>, {}|>|>]",
            None,
            "{a, b}",
            None,
        ),
        (
            "Keys[<|a -> x, a -> y, {a -> z, {b -> t}, <||>, {}}|>]",
            None,
            "{a, b}",
            None,
        ),
        (
            "Keys[<|a -> x, <|a -> y, b|>|>]",
            (
                "The argument Association[a -> x, Association[a -> y, b]] is not a valid Association or a list of rules.",
            ),
            "Keys[Association[a -> x, Association[a -> y, b]]]",
            None,
        ),
        (
            "Keys[<|a -> x, {a -> y, b}|>]",
            (
                "The argument Association[a -> x, {a -> y, b}] is not a valid Association or a list of rules.",
            ),
            "Keys[Association[a -> x, {a -> y, b}]]",
            None,
        ),
        (
            "Keys[{a -> x, <|a -> y, b|>}]",
            (
                "The argument Association[a -> y, b] is not a valid Association or a list of rules.",
            ),
            "Keys[{a -> x, Association[a -> y, b]}]",
            None,
        ),
        (
            "Keys[{a -> x, {a -> y, b}}]",
            ("The argument b is not a valid Association or a list of rules.",),
            "Keys[{a -> x, {a -> y, b}}]",
            None,
        ),
        (
            "Keys[a -> x, b -> y]",
            ("Keys called with 2 arguments; 1 argument is expected.",),
            "Keys[a -> x, b -> y]",
            None,
        ),
        ("Values[a -> x]", None, "x", None),
        (
            "Values[{a -> x, a -> y, {a -> z, <|b -> t|>, <||>, {}}}]",
            None,
            "{x, y, {z, {t}, {}, {}}}",
            None,
        ),
        (
            "Values[{a -> x, a -> y, <|a -> z, {b -> t}, <||>, {}|>}]",
            None,
            "{x, y, {z, t}}",
            None,
        ),
        (
            "Values[<|a -> x, a -> y, <|a -> z, <|b -> t|>, <||>, {}|>|>]",
            None,
            "{z, t}",
            None,
        ),
        (
            "Values[<|a -> x, a -> y, {a -> z, {b -> t}, <||>, {}}|>]",
            None,
            "{z, t}",
            None,
        ),
        (
            "Values[<|a -> x, <|a -> y, b|>|>]",
            (
                "The argument Association[a -> x, Association[a -> y, b]] is not a valid Association or a list of rules.",
            ),
            "Values[Association[a -> x, Association[a -> y, b]]]",
            None,
        ),
        (
            "Values[<|a -> x, {a -> y, b}|>]",
            (
                "The argument Association[a -> x, {a -> y, b}] is not a valid Association or a list of rules.",
            ),
            "Values[Association[a -> x, {a -> y, b}]]",
            None,
        ),
        (
            "Values[{a -> x, <|a -> y, b|>}]",
            (
                "The argument {a -> x, Association[a -> y, b]} is not a valid Association or a list of rules.",
            ),
            "Values[{a -> x, Association[a -> y, b]}]",
            None,
        ),
        (
            "Values[{a -> x, {a -> y, b}}]",
            (
                "The argument {a -> x, {a -> y, b}} is not a valid Association or a list of rules.",
            ),
            "Values[{a -> x, {a -> y, b}}]",
            None,
        ),
        (
            "Values[a -> x, b -> y]",
            ("Values called with 2 arguments; 1 argument is expected.",),
            "Values[a -> x, b -> y]",
            None,
        ),
        ("assoc=.;subassoc=.;", None, "Null", None),
    ],
)
def test_associations_private_doctests(
    str_expr, expected_messages, str_expected, assert_message
):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )
