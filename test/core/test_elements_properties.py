from mathics.core.expression import Expression
from mathics.core.symbols import Symbol

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

    for str_expression, full_eval, is_flat, is_sorted in [
        # fmt: off
     # expr          fully evaluated?  flat?  sorted?
     ("Plus[1, 1, 1]",          True,  True,  True),
     ("List[]",                 True,  True,  True),
     ('List["a", "a", "a"]',    True,  True,  True),
     ('List["a", 2, 3]',        True,  True,  False),
     ("Plus[1, 2, 3]",          True,  True,  False),
     ("Plus[x]",                False, True,  True),
     ("Plus[x, y]",             False, True,  False),
     ("Plus[Plus[x], Plus[x]]", False, False, True),
     ('Plus["x", Plus["x"]]',   False, False, False),
    ]:
        # fmt: on
        session.evaluation.out.clear()
        feeder = MathicsSingleLineFeeder(str_expression)
        ast = parser.parse(feeder)
        # print("XXX", str_expression)

        # convert() creates the initial Expression. In that various properties should
        # be set.
        expr = convert(ast, session.definitions)
        assert expr._elements_fully_evaluated == full_eval, str_expression
        assert expr._is_sorted == is_sorted, str_expression
        assert expr._is_flat == is_flat, str_expression
