# -*- coding: utf-8 -*-
"""
An abort that reaches the CLI's read-eval loop while it reads input: the
interrupt menu's "abort" with no evaluation running. The input being typed
is dropped and the session goes on with a new prompt; it used to end with an
AbortInterrupt traceback.

The SIGINT handler runs the menu inside input(), so the AbortInterrupt comes
out of the shell's read_line(); the test makes read_line() raise it.
"""

from mathics.core.definitions import Definitions
from mathics.core.interrupt import AbortInterrupt
from mathics.core.load_builtin import import_and_load_builtins
from mathics.repl import TerminalShell, interactive_eval_loop


def test_abort_while_reading_input_keeps_the_session(capsys, monkeypatch):
    import mathics.core as mathics_core

    # test_main_preeval.py leaves a hook of its own installed
    monkeypatch.setattr(mathics_core, "PRE_EVALUATION_HOOK", None)
    import_and_load_builtins()
    definitions = Definitions(add_builtin=True)
    shell = TerminalShell(
        definitions,
        "NoColor",
        want_readline=False,
        want_completion=False,
        autoload=False,
    )
    script = [AbortInterrupt(), "6*7", EOFError()]

    def read_line(prompt):
        step = script.pop(0)
        if isinstance(step, BaseException):
            raise step
        return step

    shell.read_line = read_line
    interactive_eval_loop(
        shell, full_form=False, strict_wl_output=False, init_signal_handler=False
    )
    out = capsys.readouterr().out
    assert script == [], "the session ended before reading all its input"
    assert "= 42" in out, out
