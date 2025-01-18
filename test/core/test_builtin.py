"""
Test how builtins are loaded
"""

from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.builtin import Builtin
from mathics.core.definitions import Definitions
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.symbols import SymbolTrue


class TrialBuiltin(Builtin):
    """
    <dl>
      <dt>'TrialBuiltin'[$x$]
      <dd>nothing
    </dl>
    """

    options = {
        "FakeOption": "True",
    }
    messages = {
        "nomsg": "Test message `1`.",
    }

    # A Downvalue
    def eval_downvalue(self, expr, evaluation):
        """expr: TrialBuiltin[_:Symbol]"""
        return

    # An Upvalue
    def eval_upvalue(self, expr, x, evaluation):
        """expr: G[TrialBuiltin[x_:Symbol]]"""
        return

    # A format rule for a custom format
    def format_parm1(self, expr, x, evaluation):
        """(CustomForm,): expr: TrialBuiltin[x_:Symbol]"""
        return

    # A MakeBoxes rule, using a name pattern,
    # with a line break.
    def format_parm2(self, expr, x, y, evaluation):
        """(MakeBoxes, ):expr: TrialBuiltin[x_:Symbol,
        y_]
        """
        return

    # A format rule for OutputForm
    def format_parmb(self, expr, x, y, evaluation):
        """(OutputForm,): expr: TrialBuiltin[x_:Symbol,
        y:P|Q]
        """
        return

    # A general format rule.
    def format_parm_general(self, expr, x, y, evaluation):
        """expr: TrialBuiltin[x_:Symbol,
        y:P|Q]
        """
        return


# This happens before any call to import_and_load_builtins
DEFINITIONS = Definitions()
EVALUATION = Evaluation(DEFINITIONS)
MakeBoxes(expression=False).contribute(DEFINITIONS)
TrialBuiltin(expression=False).contribute(DEFINITIONS)


def test_other_attributes_builtin():
    import_and_load_builtins()
    definitions = Definitions(add_builtin=True)
    definition = definitions.builtin["System`Plus"]

    builtin = definition.builtin
    assert builtin.context == "System`"
    assert builtin.get_name() == "System`Plus"
    assert builtin.get_name(short=True) == "Plus"


def test_builtin_get_functions():
    definitions = DEFINITIONS
    MakeBoxes.context = "System`"
    MakeBoxes(expression=False).contribute(definitions)
    builtin = definitions.builtin["System`TrialBuiltin"].builtin
    evalrules = list(builtin.get_functions("eval"))
    for r in evalrules:
        assert isinstance(r, tuple) and len(r) == 2
        assert isinstance(r[0], BaseElement)

    evalrules = list(builtin.get_functions("format_"))
    for r in evalrules:
        assert isinstance(r, tuple) and len(r) == 2
        # For formatvalues, the pattern can be both a BaseElement
        # or a tuple of a string with a format name and a BaseElement.
        if isinstance(r[0], tuple):
            assert len(r[0]) == 2
            assert isinstance(r[0][0], list)
            assert isinstance(r[0][1], BaseElement)
        else:
            assert isinstance(r[0], BaseElement)


def test_contribute_builtin():
    """Test for Builtin.contribute."""

    definitions = Definitions()
    evaluation = Evaluation(definitions)
    MakeBoxes(expression=False).contribute(definitions)

    TrialBuiltin(expression=False).contribute(definitions)
    assert "System`TrialBuiltin" in definitions.builtin.keys()
    definition = definitions.get_definition("System`TrialBuiltin")
    # Check that the formats are loaded into the right places.
    assert "System`MakeBoxes" in definition.formatvalues
    assert "System`CustomForm" in definition.formatvalues
    assert "System`OutputForm" in definition.formatvalues
    # Test if the rules are loaded into the right place.
    assert definition.upvalues
    assert definition.downvalues
    assert definition.messages
    assert definition.options
    builtin = definition.builtin
    assert builtin.get_option_string(definition.options, "FakeOption", evaluation) == (
        "True",
        SymbolTrue,
    )
