import importlib

from mathics.core.load_builtin import (
    _builtins,
    add_builtins_from_builtin_module,
    import_and_load_builtins,
)
from mathics.session import MathicsSession


def test_add_builtins_from_builtin_module():
    """
    Test that add_builtins_from_module() loads a single Builtin module
    and updates definitions.
    """
    # Set up a session with all but one module.
    # Then evaluate a builtin in that module and see that we
    # now have the function defined.

    # First, load in many modules except quantum_mechanics.
    _builtins = {}
    import_and_load_builtins(exclude_files={"quantum_mechanics"}, clean_all=True)

    # Create a session, evaluate an expression using a missing Builtin function
    # and see that it is not defined...
    session = MathicsSession(character_encoding="ASCII")
    assert str(session.evaluate("PauliMatrix[0]")) == "Global`PauliMatrix[0]"
    assert (
        str(session.evaluate("SixJSymbol[{1,2,3}, {1,2,3}]"))
        == "Global`SixJSymbol[{1,2,3}, {1,2,3}]"
    )
    # Finally add in the module and see that when we use Builtin functions
    # in that module work.
    angular_module = importlib.import_module(
        "mathics.builtin.quantum_mechanics.angular"
    )
    add_builtins_from_builtin_module(angular_module)

    # Note that adding more builtins does not update the session, so we need a new one.
    session = MathicsSession(character_encoding="ASCII")
    assert str(session.evaluate("PauliMatrix[0]")) == "{{1,0},{0,1}}"
    assert str(session.evaluate("SixJSymbol[{1, 2, 3}, {1, 2, 3}]")) == "1/105"
