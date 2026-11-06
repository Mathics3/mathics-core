# -*- coding: utf-8 -*-
"""
The interrupt menu's "inspect" dialog evaluates its input with the
evaluation that was interrupted. Leaving the dialog (Ctrl-D) must give that
evaluation back as it was, so that it goes on; it used to stop at its next
check with "Timeout reached" and give $Aborted.
"""

import pytest

from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.load_builtin import import_and_load_builtins
from mathics.interrupt import inspect_eval_loop
from mathics.repl import TerminalShell


def test_leaving_the_dialog_resumes_the_interrupted_evaluation(capsys):
    import_and_load_builtins()
    definitions = Definitions(add_builtin=True)
    shell = TerminalShell(
        definitions, "NoColor", want_readline=False, want_completion=False, autoload=False
    )
    script = ["1+1", EOFError()]

    def read_line(prompt):
        step = script.pop(0)
        if isinstance(step, BaseException):
            raise step
        return step

    shell.read_line = read_line
    evaluation = Evaluation(definitions)
    evaluation.shell = shell
    # The interrupted evaluation, as it is while it runs.
    evaluation.stopped = False
    evaluation.timeout = False
    evaluation.deadline = None
    evaluation.recursion_depth = 7
    pending = evaluation.out

    with pytest.raises(EOFError):  # Ctrl-D: the menu takes it as "leave the dialog"
        inspect_eval_loop(evaluation)

    assert "= 2" in capsys.readouterr().out, "the dialog did not evaluate 1+1"
    assert evaluation.stopped is False
    assert evaluation.recursion_depth == 7
    assert evaluation.out is pending
    evaluation.check_stopped()  # must not raise TimeoutInterrupt
