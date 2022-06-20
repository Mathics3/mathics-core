# -*- coding: utf-8 -*-

from mathics.core.parser import MathicsSingleLineFeeder
from mathics.core.parser.convert import convert
from mathics.core.parser.parser import Parser
from mathics.session import MathicsSession

session = MathicsSession(add_builtin=False, catch_interrupt=True)
parser = Parser()


def test_elements_properties():
    """
    Tests that properties regarding elements of a (compound) Expression
    coming out of initial conversion are set accurately.
    """

    for str_expression, full_eval, is_flat, is_ordered in [
        # fmt: off
        # expr          fully evaluated?  flat?  ordered?
        ("Plus[1, 1, 1]",          True,  True,  True),
        ("List[]",                 True,  True,  True),
        ('List["a", "a", "b"]',    True,  True,  True),
        ('List["b", "a", "a"]',    True,  True,  False),

        ('List["a", 2, 3]',        True,  True,  False),
        ("Plus[1, 2, 3]",          True,  True,  True),
        ("Plus[x]",                False, True,  True),
        ("Plus[Plus[x]]",          False, False, True),
        ("Plus[x, y]",             False, True,  True),

        ("Plus[Plus[x], Plus[x]]", False, False, True),

        ("Plus[Plus[y], Plus[x]]", False, False, False),

        # Is sorted is true here since we have the same symbol repeated
        ('List[a, a, a]',          False,  True,  True),

        ('Plus["x", Plus["x"]]',   False, False, True),
    ]:
        # fmt: on
        session.evaluation.out.clear()
        feeder = MathicsSingleLineFeeder(str_expression)
        ast = parser.parse(feeder)

        # convert() creates the initial Expression. In that various properties should
        # be set.
        expr = convert(ast, session.definitions)
        expr._build_elements_properties()
        # print("XXX", str_expression, expr)
        assert (
            expr.elements_properties.elements_fully_evaluated == full_eval
        ), str_expression
        assert expr.elements_properties.is_ordered == is_ordered, str_expression
        assert expr.elements_properties.is_flat == is_flat, str_expression
