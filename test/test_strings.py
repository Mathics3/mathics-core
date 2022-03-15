# -*- coding: utf-8 -*-
from .helper import check_evaluation


def test_string_matchq():
    for str_expr, str_expected in (
        ('StringMatchQ[".12", NumberString]', "True"),
        ('StringMatchQ["12.", NumberString]', "True"),
        ('StringMatchQ["12.31.31", NumberString]', "False"),
        ('StringMatchQ[".", NumberString]', "False"),
        ('StringMatchQ["-1.23", NumberString]', "True"),
        ('StringMatchQ["+.2", NumberString]', "True"),
        ('StringMatchQ["1.2e4", NumberString]', "False"),
        ('StringMatchQ["abc", "ABC"]', "False"),
        ('StringMatchQ["abc", "ABC", IgnoreCase -> True]', "True"),
        # ('StringMatchQ["abc1", LetterCharacter]', "False"),
    ):
        check_evaluation(str_expr, str_expected)


def test_digitq():
    for str_expr, str_expected in (
        ('DigitQ[""]', "True"),
        ('DigitQ["."]', "False"),
        ("DigitQ[1==2]", "False"),
        ("DigitQ[a=1]", "False"),
    ):
        check_evaluation(str_expr, str_expected)


def test_string_split():
    for str_expr, str_expected in (
        ('StringSplit["a bbb  cccc aa   d"]', "{a, bbb, cccc, aa, d}"),
        ('StringSplit["a--bbb---ccc--dddd", "--"]', "{a, bbb, -ccc, dddd}"),
        ('StringSplit["the cat in the hat"]', "{the, cat, in, the, hat}"),
        ('StringSplit["192.168.0.1", "."]', "{192, 168, 0, 1}"),
        ('StringSplit["123  2.3  4  6", WhitespaceCharacter ..]', "{123, 2.3, 4, 6}"),
        (
            'StringSplit[StringSplit["11:12:13//21:22:23//31:32:33", "//"], ":"]',
            "{{11, 12, 13}, {21, 22, 23}, {31, 32, 33}}",
        ),
        (
            'StringSplit["A tree, an apple, four pears. And more: two sacks", RegularExpression["\\W+"]]',
            "{A, tree, an, apple, four, pears, And, more, two, sacks}",
        ),
        (
            'StringSplit["primes: 2 two 3 three 5 five ...",  Whitespace ~~ RegularExpression["\\d"] ~~ Whitespace]',
            "{primes:, two, three, five ...}",
        ),
        ('StringSplit["a-b:c-d:e-f-g", {":", "-"}]', "{a, b, c, d, e, f, g}"),
        ('StringSplit["a-b:c-d:e-f-g", ":" | "-"]', "{a, b, c, d, e, f, g}"),
        (
            'StringSplit[{"a:b:c:d", "listable:element"}, ":"]',
            "{{a, b, c, d}, {listable, element}}",
        ),
        (
            'StringSplit["cat Cat hat CAT", "c", IgnoreCase -> True]',
            "{at , at hat , AT}",
        ),
        (
            'StringSplit["This is a sentence, which goes on.",  Except[WordCharacter] ..]',
            "{This, is, a, sentence, which, goes, on}",
        )
        # #  FIXME: these forms are not implemented yet:
        # ('StringSplit["11a22b3", _?LetterQ]', '{11, 22, 3}'),
        # ('StringSplit["a b::c d::e f g", "::" -> "--"]'), '{a, b, --, c d, --, e f g}'),
        # ('StringSplit["a--b c--d e", x : "--" :> x]', {a, --, b c, --, d e}),
        # ('StringSplit[":a:b:c:", ":", All]', '{"", "a", "b", "c", ""}'),
    ):
        check_evaluation(
            str_expr,
            str_expected,
            to_string_expr=True,
            hold_expected=True,
            to_string_expected=True,
        )
