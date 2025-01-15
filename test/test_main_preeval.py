# -*- coding: utf-8 -*-
import mathics.core as mathics_core
from mathics.core.atoms import Integer1, Integer2
from mathics.core.definitions import Definitions
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.main import TerminalShell, interactive_eval_loop

hook_was_called = False


def test_pre_evaluation_hook():
    """
    Test that we can set a PRE_EVALUATION_HOOK function and
    that this gets called in the interactive_eval_loop()
    of mathics.main.main()
    """

    def pre_evaluation_hook(query: BaseElement, evaluation: Evaluation):
        """
        hook to see that pre-evalution hook gets called
        """
        assert query == Integer1 + Integer2
        global hook_was_called
        hook_was_called = True
        # Leave interactive evaluation loop.
        raise EOFError

    def mock_read_line(self, prompt=""):
        """
        Replacement for reading a line of input from stdin.
        Note that the particular expression is tied into the
        assert test we make in pre_evaluation_hook.
        """
        return "1+2\n"

    # Set up a pre-evaluation hook.
    mathics_core.PRE_EVALUATION_HOOK = pre_evaluation_hook

    definitions = Definitions(add_builtin=False, extension_modules=tuple())

    # Mock patch in our own terminal shell, but with a replace read_line()
    # routine we can use for testing.
    shell = TerminalShell(
        definitions,
        colors=None,
        want_readline=False,
        want_completion=False,
        autoload=False,
    )
    shell.read_line = mock_read_line

    interactive_eval_loop(shell, False, False)
    assert hook_was_called, "Should have called pre_evaluation_hook()"
