"""
Test how builtins are loaded
"""

from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.builtin import Builtin
from mathics.core.definitions import Definitions


def test_contribute_builtin():
    """Test for Builtin.contribute."""

    definitions = Definitions()
    MakeBoxes.context = "System`"
    MakeBoxes(expression=False).contribute(definitions)

    class TestBuiltin(Builtin):
        """
        <dl>
          <dt>'TestBuiltin'[$x$]
          <dd>nothing
        </dl>
        """

        messages = {
            "nomsg": "Test message `1`.",
        }

        def eval_downvalue(self, expr, evaluation):
            """expr: TestBuiltin[_:Symbol]"""
            return

        def eval_upvalue(self, expr, x, evaluation):
            """expr: G[TestBuiltin[x_:Symbol]]"""
            return

        def format_parm1(self, expr, x, evaluation):
            """(CustomForm,): expr: F[x_:Symbol]"""
            return

        def format_parm2(self, expr, x, y, evaluation):
            """(MakeBoxes, ):expr: G[x_:Symbol,
            y_]
            """
            return

        def format_parmb(self, expr, x, y, evaluation):
            """(OutputForm,): expr: G[x_:Symbol,
            y:P|Q]
            """
            return

    TestBuiltin(expression=False).contribute(definitions)
    assert "System`TestBuiltin" in definitions.builtin.keys()
    definition = definitions.get_definition("System`TestBuiltin")
    # Check that the formats are loaded into the right places.
    assert "System`MakeBoxes" in definition.formatvalues
    assert "System`CustomForm" in definition.formatvalues
    assert "System`OutputForm" in definition.formatvalues
    # Test if the rules are loaded into the right place.
    assert definition.upvalues
    assert definition.downvalues
    assert definition.messages
