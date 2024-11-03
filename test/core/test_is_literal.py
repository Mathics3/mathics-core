# -*- coding: utf-8 -*-
"""
Test mathics.core property on BaseElement is_literal.
"""

from mathics.core.parser import MathicsSingleLineFeeder
from mathics.core.parser.convert import convert
from mathics.core.parser.parser import Parser
from mathics.session import MathicsSession

session = MathicsSession(add_builtin=False, catch_interrupt=True)
parser = Parser()


def test_is_literal():
    """
    Tests properties literalness of expressions
    coming out of initial conversion are set accurately.
    """

    for str_expression, is_literal, value, assert_msg in [
        # fmt: off
        # expr                  is_literal? Python      assert message
        ("5",                   True,       5,          "an atomic Integer is a literals"),
        ('"5"',                 True,       "5",        "an atomic String is a literal"),
        ("1/2",                 False,      None,       "a ratio is not a literal"),
        ("X",                   False,      None,       "a variable symbol is not a literal"),
        ("{1, 2, 3}",           True,       (1, 2, 3),  "a list of Integers is a literal"),
        ("{1, 2, Pi}",          False,      None,       "a list with a symbolic constant is not a literal"),
        ('{"x", {2, 3}, 1/2}',  False,      None,       "a nested list containing a ratio is not a literal "),
        ('{"x", 2, 3.0}',       True,       ("x", 2, 3.0),          "a list of literals is a literal"),
        ('{"x", {2, 3, {}}}',   True,       ("x", (2, 3, tuple())), "a nested list of literals is a literal"),
    ]:
        # fmt: on
        session.evaluation.out.clear()
        feeder = MathicsSingleLineFeeder(str_expression)
        ast = parser.parse(feeder)
        # print("XXX", ast)

        # convert() creates the initial Expression. In that various properties should
        # be set.
        expr = convert(ast, session.definitions)
        assert expr.is_literal == is_literal, assert_msg
        if value is not None:
            assert expr.value == value
