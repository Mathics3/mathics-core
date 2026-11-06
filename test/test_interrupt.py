# -*- coding: utf-8 -*-
"""
Ctrl-C while an evaluation runs on its own thread (see
Evaluation._evaluate_on_thread).

The unit tests hand an interrupt request to an evaluation directly. The
terminal tests run the mathics CLI in a pseudo-terminal and press Ctrl-C
there, so that the terminal driver sends SIGINT exactly as for a person at
the keyboard, then answer the interrupt> menu.
"""

import os
import re
import sys
import threading
import time

import pytest

from mathics.core import evaluation as core_evaluation
from mathics.session import MathicsSession


# ---- unit tests ---------------------------------------------------------------


def test_pause_takes_a_pending_interrupt():
    """Pause[] runs the interrupt menu when Ctrl-C comes in its sleep, as a
    signal cut into the sleep when the evaluation ran on the main thread."""
    session = MathicsSession()
    evaluation = session.evaluation
    taken = []

    def request(frame):
        taken.append(time.time())
        from mathics.core.interrupt import AbortInterrupt

        raise AbortInterrupt

    def press_ctrl_c():
        time.sleep(0.5)
        evaluation.interrupt_request = request

    threading.Thread(target=press_ctrl_c, daemon=True).start()
    start = time.time()
    result = session.evaluate_as_in_cli("Pause[10]; 7")
    assert result.result == "$Aborted"
    assert taken and taken[0] - start < 3, "the menu waited for the pause to end"


def test_interrupt_left_after_an_evaluation_is_dropped(monkeypatch):
    """A Ctrl-C that came too late for one evaluation (after its last check)
    does not open the menu in the next one."""
    session = MathicsSession()
    evaluation = session.evaluation
    taken = []
    original_stop = core_evaluation.Evaluation.stop

    def stop_with_a_late_ctrl_c(self):
        original_stop(self)
        self.interrupt_request = lambda frame: taken.append(frame)

    monkeypatch.setattr(core_evaluation.Evaluation, "stop", stop_with_a_late_ctrl_c)
    session.evaluate_as_in_cli("1 + 1")
    monkeypatch.setattr(core_evaluation.Evaluation, "stop", original_stop)
    assert evaluation.interrupt_request is None
    assert session.evaluate_as_in_cli("Pause[0.2]; 2 + 2").result == "4"
    assert taken == []


def test_other_threads_do_not_take_the_interrupt():
    """Only the evaluating thread runs the menu: formatting output on
    another thread (as the interrupt notice once did) must not."""
    session = MathicsSession()
    evaluation = session.evaluation
    session.evaluate_as_in_cli("1")
    taken = []
    evaluation.interrupt_request = lambda frame: taken.append(frame)
    other = threading.Thread(target=evaluation.check_stopped)
    other.start()
    other.join()
    assert taken == [] and evaluation.interrupt_request is not None
    evaluation.interrupt_request = None


# ---- terminal tests -----------------------------------------------------------

pty = pytest.importorskip("pty")
needs_terminal = pytest.mark.skipif(
    sys.platform.startswith("win") or not core_evaluation.USE_EVALUATION_THREAD,
    reason="needs a pseudo-terminal and the evaluation thread",
)


class Terminal:
    """The mathics CLI in a pseudo-terminal."""

    def __init__(self):
        import select  # noqa: F401  (checked here: no select, no terminal tests)

        env = dict(os.environ, TERM="dumb", COLUMNS="200")
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execve(
                sys.executable,
                [sys.executable, "-m", "mathics", "--no-completion", "--colors", "NoColor"],
                env,
            )
        self.buf = b""

    def wait_for(self, pattern, timeout, start=0):
        import select

        rx = re.compile(pattern.encode())
        end = time.time() + timeout
        while True:
            m = rx.search(self.buf, start)
            if m or time.time() >= end:
                return m
            ready, _, _ = select.select([self.fd], [], [], min(0.2, end - time.time()))
            if ready:
                try:
                    data = os.read(self.fd, 65536)
                except OSError:
                    return rx.search(self.buf, start)
                self.buf += data

    def pause(self, seconds):
        self.wait_for("(?!x)x", seconds)  # keep reading while waiting

    def type(self, line):
        # readline flushes what is typed before it has set the terminal up,
        # and a person does not type within milliseconds of the prompt.
        self.pause(0.8)
        mark = len(self.buf)
        os.write(self.fd, line.encode() + b"\r")
        assert self.wait_for(re.escape(line[:10]), 5, mark), f"{line!r} was not echoed"

    def key(self, ch):
        self.pause(0.5)
        os.write(self.fd, ch.encode())

    def screen(self, start=0):
        return self.buf[start:].decode(errors="replace").replace("\r", "")

    def close(self):
        import signal

        try:
            os.kill(self.pid, signal.SIGKILL)
            os.waitpid(self.pid, 0)
        except (ProcessLookupError, ChildProcessError):
            pass


@pytest.fixture
def terminal():
    t = Terminal()
    assert t.wait_for(r"In\[1\]:= ", 60), "no prompt: " + t.screen()[-300:]
    yield t
    t.close()


def interrupt(t, workload, run_for=2.0):
    t.type(workload)
    t.pause(run_for)
    mark = len(t.buf)
    pressed = time.time()
    t.key("\x03")
    assert t.wait_for("interrupt> ", 20, mark), "no menu: " + t.screen(mark)
    return mark, time.time() - pressed


@needs_terminal
def test_abort_a_loop(terminal):
    mark, waited = interrupt(terminal, "Do[i, {i, 10^8}]")
    assert waited < 2
    terminal.type("a")
    assert terminal.wait_for(r"Out\[1\]= \$Aborted", 15, mark), terminal.screen(mark)
    terminal.type("6*7")
    assert terminal.wait_for(r"Out\[2\]= 42", 15, mark), terminal.screen(mark)


@pytest.mark.parametrize("answer", ["c", "s"])
@needs_terminal
def test_continue_or_show_during_pause(terminal, answer):
    mark, waited = interrupt(terminal, "Pause[6]; 7")
    assert waited < 2, "the menu waited for the pause to end"
    terminal.type(answer)
    assert terminal.wait_for(r"Out\[1\]= 7", 20, mark), terminal.screen(mark)


@needs_terminal
def test_second_ctrl_c_opens_no_second_menu(terminal):
    mark, _ = interrupt(terminal, "Do[i, {i, 10^8}]")
    terminal.key("\x03")
    terminal.type("a")
    assert terminal.wait_for(r"Out\[1\]= \$Aborted", 15, mark), terminal.screen(mark)
    terminal.pause(1.5)
    assert terminal.screen(mark).count("interrupt> ") == 1, terminal.screen(mark)


@needs_terminal
def test_abort_a_long_step(terminal):
    """A step that does not check for interrupts (a long Expand in SymPy)
    delays the menu; a notice says Ctrl-C was seen."""
    mark, waited = interrupt(terminal, "Length[Expand[(x+y+z+w)^40]]", run_for=1.0)
    if waited > 0.6:
        assert "(interrupt:" in terminal.screen(mark)
    terminal.type("a")
    assert terminal.wait_for(r"Out\[1\]= \$Aborted", 30, mark), terminal.screen(mark)
