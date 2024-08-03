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

    for str_expression, is_literal, assert_msg in [
        # fmt: off
        # expr                  is_literal? assert message
        ("5",                   True,       "an atomic Integer is a literals"),
        ('"5"',                 True,       "an atomic String is a literal"),
        ("1/2",                 False,      "a ratio is not a literal"),
        ("X",                   False,      "a variable symbol is not a literal"),
        ("{1, 2, 3}",           True,       "a list of Integers is a literal"),
        ("{1, 2, Pi}",          False,      "a list with a symbolic constant is not a literal"),
        ('{"x", 2, 3.0}',       True,       "a list of literals is a literal"),
        ('{"x", {2, 3, {}}}',   True,       "a nested list of literals is a literal"),
        ('{"x", {2, 3}, 1/2}',  False,      "a nested list containing a ratio is not a literal "),
    ]:
        # fmt: on
        session.evaluation.out.clear()
        feeder = MathicsSingleLineFeeder(str_expression)
        ast = parser.parse(feeder)

        # convert() creates the initial Expression. In that various properties should
        # be set.
        expr = convert(ast, session.definitions)
        assert expr.is_literal == is_literal, assert_msg
