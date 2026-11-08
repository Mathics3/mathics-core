# -*- coding: utf-8 -*-

import os
import sys
import threading
import time
from abc import ABC
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, overload

from mathics_scanner.errors import SyntaxError
from mathics_scanner.feed import LineFeeder

from mathics import settings
from mathics.core.atoms import Integer, String
from mathics.core.convert.python import from_python
from mathics.core.element import BaseElement, KeyComparable, ensure_context
from mathics.core.interrupt import (
    AbortInterrupt,
    BreakInterrupt,
    ContinueInterrupt,
    ReturnInterrupt,
    TimeConstrainedTimeout,
    TimeoutInterrupt,
    WLThrowInterrupt,
)
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import (
    SymbolAborted,
    SymbolBreak,
    SymbolContinue,
    SymbolFullForm,
    SymbolHold,
    SymbolIn,
    SymbolMathMLForm,
    SymbolMessageName,
    SymbolOut,
    SymbolOutputForm,
    SymbolOverflow,
    SymbolStandardForm,
    SymbolStringForm,
    SymbolTeXForm,
    SymbolThrow,
)

FORMATS = [
    "StandardForm",
    "FullForm",
    "TraditionalForm",
    "OutputForm",
    "InputForm",
    "TeXForm",
    "MathMLForm",
    "MatrixForm",
    "TableForm",
]

SymbolPre = Symbol("System`$Pre")
SymbolPrePrint = Symbol("System`$PrePrint")
SymbolPost = Symbol("System`$Post")

# MIN_RECURSION_LIMIT is the smallest value allowed for $RecursionLimit, as in WMA:
# $RecursionLimit = 10 there gives "value must be Infinity or an integer at least 20".

MIN_RECURSION_LIMIT = 20

# MAX_RECURSION_DEPTH gives the maximum value allowed for $RecursionLimit. it's usually set to its
# default settings.DEFAULT_MAX_RECURSION_DEPTH.

MAX_RECURSION_DEPTH = max(
    settings.DEFAULT_MAX_RECURSION_DEPTH,
    int(os.getenv("MATHICS_MAX_RECURSION_DEPTH", settings.DEFAULT_MAX_RECURSION_DEPTH)),
)


def python_recursion_depth(n) -> int:
    # convert Mathics3 recursion depth to Python recursion depth. this estimates how many Python calls
    # we need at worst to process one Mathics3 recursion. A recursive
    # definition matched through a Condition or PatternTest, as in
    # Combinatorica's DepthFirstTraversal, takes a little over 30.
    return 200 + 40 * n


def python_stack_size(n) -> int:  # n is a Mathics3 recursion depth
    # python_stack_frame_size is the C stack, in bytes, that one Python call takes on
    # average. Since Python 3.11 a call from Python code to Python code takes none,
    # so this is far below the size of a C frame. Measured on macOS arm64 with
    # Python 3.11 and 3.14: a Combinatorica DepthFirstTraversal, and a recursive
    # definition matched through PatternTest with a Module, take 0.7 to 1.4 KB
    # per Mathics3 level. 100 gives 4 KB per level, so 400 MB for 100000 levels:
    # address space reserved for the thread, only the part used is allocated.
    python_stack_frame_size = 100
    return python_recursion_depth(n) * python_stack_frame_size


# How deep a Python recursion can go is bounded by the C stack, not only by
# sys.setrecursionlimit: matching a pattern with a Condition, for instance,
# goes through C calls that take C stack on every Mathics3 level.
#
# - Python 3.11 does not check the C stack: running out of it crashes the
#   process with a segmentation fault.
# - Python 3.12 and 3.13 count C calls against a fixed limit, whatever the
#   size of the stack, and raise RecursionError when it is reached.
# - Python 3.14 checks the C stack against its real size and raises
#   RecursionError when it runs out.
#
# The main thread has a small stack, typically 8 MB: a recursive Combinatorica
# DepthFirstTraversal runs out of it before 3000 levels. Where a larger stack
# lets an evaluation go deeper, 3.11 and 3.14 on, Evaluation.evaluate() runs
# on a thread whose stack is sized for the deepest recursion allowed.

USE_EVALUATION_THREAD = sys.platform != "emscripten" and not (
    (3, 12) <= sys.version_info[:2] < (3, 14)
)

# MAX_INFINITE_RECURSION_DEPTH is how deep $RecursionLimit = Infinity lets an
# evaluation go. Without a thread on Python 3.11, nothing would stop a crash.

MAX_INFINITE_RECURSION_DEPTH = (
    max(MAX_RECURSION_DEPTH, settings.DEFAULT_MAX_INFINITE_RECURSION_DEPTH)
    if USE_EVALUATION_THREAD or sys.version_info >= (3, 12)
    else MAX_RECURSION_DEPTH
)

# threading.stack_size() takes only whole pages: round up to whole MiB.
_MIB = 2**20
_stack_size = python_stack_size(max(MAX_RECURSION_DEPTH, MAX_INFINITE_RECURSION_DEPTH))
EVALUATION_THREAD_STACK_SIZE = (_stack_size + _MIB - 1) // _MIB * _MIB


def set_python_recursion_limit(n) -> None:
    "Sets the required python recursion limit given $RecursionLimit value"
    python_depth = python_recursion_depth(n)
    sys.setrecursionlimit(python_depth)
    if sys.getrecursionlimit() != python_depth:
        raise OverflowError


class _Out(KeyComparable):
    def __init__(self) -> None:
        self.is_message = False
        self.is_print = False
        self.text = ""

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return (self.is_message, self.is_print, self.text)

    def get_sort_key(self):
        return self.element_order

    def get_data(self) -> Dict[str, Any]:
        raise NotImplementedError


class Evaluation:
    """An Evaluation object contains everyting about the evaluation
    environment, such as evaluation definitions, exception and
    formatting information, and a grab bag of other things.

    It is a rather fat object.
    """

    def __init__(
        self, definitions=None, output=None, format="text", catch_interrupt=True
    ) -> None:
        from mathics.core.definitions import Definitions

        if definitions is None:
            definitions = Definitions()
        self.current_expression: Optional[BaseElement] = None
        self.SymbolNull = SymbolNull

        # Used in ``mathics.builtin.numbers.constants.get_constant`` and
        # ``mathics.builtin.numeric.N``.
        self._preferred_n_method: List[str] = []

        self.catch_interrupt = catch_interrupt
        self.definitions: Definitions = definitions
        self.exc_result: Optional[Symbol] = self.SymbolNull
        self.format = format
        self.is_boxing = False

        # status of last evaluate
        self.last_eval = None

        self.listeners: Dict[str, List[Callable]] = {}
        self.options: Optional[Dict[str, Any]] = None
        self.out: List[_Out] = []
        self.output = output if output else Output()
        self.predetermined_out = None
        self.compound_out_depth = 1
        self.quiet_all = False
        self.recursion_depth = 0
        # The $RecursionLimit that inc_recursion_depth() last checked against,
        # for the message when Python itself runs out of stack.
        self.recursion_limit = MAX_RECURSION_DEPTH

        # A SIGINT that arrived while the evaluation runs on its own thread:
        # check_stopped() calls it, with the frame it was called from, in the
        # evaluating thread.
        self.interrupt_request: Optional[Callable] = None
        # True while the evaluating thread shows the interrupt menu.
        self.interrupt_menu_open = False
        # The thread _evaluate() runs on: the only one that takes an
        # interrupt_request.
        self.evaluating_thread: Optional[threading.Thread] = None

        # iteration is used to keep track of evaluation chains and is
        # compared against $IterationLimit.
        self.iteration_count = 0

        # Interrupt handlers may need access to the shell
        # that invoked the evaluation.
        self.shell: Optional[LineFeeder] = None

        self.stopped = False
        self.timeout = False
        self.timeout_queue: List[Tuple[float, float]] = []
        # time.time() after which the current evaluation is stopped, from the
        # timeout given to evaluate(); None for no limit.
        self.deadline: Optional[float] = None

        # A place for Trace and friends to store information about the
        # last evaluation
        self.trace_info: Optional[Any] = None

    def parse(self, query, src_name: str = ""):
        "Parse a single expression and print the messages."
        from mathics.core.parser import MathicsSingleLineFeeder

        return self.parse_feeder(MathicsSingleLineFeeder(query, src_name))

    def parse_evaluate(self, query, timeout=None):
        expr = self.parse(query)
        if expr is not None:
            return self.evaluate(expr, timeout)

    def parse_feeder(self, feeder):
        return self.parse_feeder_returning_code_and_messages(feeder)[0]

    def parse_feeder_returning_code(self, feeder) -> tuple:
        """
        Parse a single expression from feeder, print the messages it produces and
        return the result and the source code for this.
        """
        return self.parse_feeder_returning_code_and_messages(feeder)[:2]

    def parse_feeder_returning_code_and_messages(self, feeder) -> tuple:
        """
        Parse a single expression from feeder, print the messages it produces and
        return the result, the source code for this and evaluated
        messages created in evaluation.

        If there was a SyntaxError, the source code returned is "" and the result is None.
        """
        from mathics.core.parser.util import parse_returning_code

        try:
            result, source_code = parse_returning_code(self.definitions, feeder)
        except SyntaxError:
            result = None
            source_code = ""

        if result is None:
            self.recursion_depth = 0
            self.stopped = False
        messages = feeder.send_messages(self)
        return result, source_code, messages

    def evaluate(self, query, timeout=None, format=None):
        """
        Evaluate a Mathics3 expression and return the result of evaluation.

        On return self.exc_result will contain status of various
        exception type of result like $Aborted, Overflow, Break, or Continue.
        If none of the above applies self.exc_result is Null
        """
        if USE_EVALUATION_THREAD and not getattr(
            threading.current_thread(), "mathics3_evaluation", False
        ):
            return self._evaluate_on_thread(query, timeout, format)
        return self._evaluate(query, timeout, format)

    def _evaluate_on_thread(self, query, timeout, format):
        """
        Run _evaluate() on a thread whose stack holds the deepest recursion
        allowed, and wait for it. See USE_EVALUATION_THREAD.
        """
        outcome: Dict[str, Any] = {}

        def run():
            try:
                outcome["result"] = self._evaluate(query, timeout, format)
            except BaseException as exc:  # SystemExit from Quit[] included
                outcome["exception"] = exc

        try:
            previous_stack_size = threading.stack_size(EVALUATION_THREAD_STACK_SIZE)
            try:
                worker = threading.Thread(
                    target=run, name="Mathics3 evaluation", daemon=True
                )
                worker.mathics3_evaluation = True  # type: ignore[attr-defined]
                worker.start()
            finally:
                threading.stack_size(previous_stack_size)
        except (RuntimeError, ValueError, MemoryError):
            # No thread with that stack here: evaluate on this one.
            return self._evaluate(query, timeout, format)

        # A SIGINT handler that looks through the interrupted frames for a
        # local named "evaluation" finds it here, and sees from
        # evaluating_thread that it must hand the interrupt over.
        evaluation = self  # noqa: F841
        evaluating_thread = worker  # noqa: F841
        while True:
            try:
                worker.join()
                break
            except KeyboardInterrupt:
                # Signals reach only the main thread: pass it on.
                from timed_threads import async_raise

                if worker.is_alive() and worker.ident is not None:
                    try:
                        async_raise(worker.ident, KeyboardInterrupt)
                    except ValueError:
                        pass  # the thread has just finished

        if "exception" in outcome:
            raise outcome["exception"]
        return outcome["result"]

    def _evaluate(self, query, timeout=None, format=None):
        if self.evaluating_thread is None or not self.evaluating_thread.is_alive():
            self.evaluating_thread = threading.current_thread()
        from mathics.core.convert.expression import to_expression
        from mathics.core.expression import Expression
        from mathics.core.rules import RewriteRule

        self.start_time = time.time()
        self.iteration_count = 0
        self.recursion_depth = 0
        self.timeout = False
        self.stopped = False
        self.deadline = None if timeout is None else self.start_time + timeout
        self.exc_result = self.SymbolNull
        self.last_eval = None
        # A value left by an evaluation that was interrupted must not
        # become the Out[] of this one.
        self.predetermined_out = None
        # The recursion depth at which a CompoundExpression sets
        # predetermined_out (see CompoundExpression.eval).
        self.compound_out_depth = 1
        if format is None:
            format = self.format

        output_forms = self.definitions.outputforms

        line_no = self.definitions.get_line_no()

        history_length = self.definitions.get_history_length()

        result = None

        def check_io_hook(hook):
            return len(self.definitions.get_ownvalues(hook)) > 0

        def evaluate():
            if history_length > 0:
                self.definitions.add_rule(
                    "In",
                    RewriteRule(to_expression("In", line_no), query, evaluation=self),
                )
            if check_io_hook("System`$Pre"):
                self.last_eval = Expression(SymbolPre, query).evaluate(self)
            else:
                self.last_eval = query.evaluate(self)

            if check_io_hook("System`$Post"):
                self.last_eval = Expression(SymbolPost, self.last_eval).evaluate(self)
            if history_length > 0:
                if self.predetermined_out is not None:
                    out_result = self.predetermined_out
                    self.predetermined_out = None
                else:
                    out_result = self.last_eval

                stored_result = self.get_stored_result(out_result, output_forms)
                self.definitions.add_rule(
                    "Out",
                    RewriteRule(
                        Expression(SymbolOut, Integer(line_no)),
                        stored_result,
                        evaluation=self,
                    ),
                )

            if self.last_eval != self.SymbolNull:
                if check_io_hook("System`$PrePrint"):
                    self.last_eval = Expression(
                        SymbolPrePrint, self.last_eval
                    ).evaluate(self)
                return self.format_output(self.last_eval, format)
            else:
                self.exec_result = self.SymbolNull
                return None

        try:
            try:
                result = evaluate()
            except KeyboardInterrupt:
                if self.catch_interrupt:
                    self.exc_result = SymbolAborted
                else:
                    raise
            except ValueError as exc:
                text = str(exc)
                if (
                    text == "mpz.pow outrageous exponent"
                    or text == "mpq.pow outrageous exp num"  # noqa
                ):
                    self.message("General", "ovfl")
                    self.exc_result = Expression(SymbolOverflow)
                else:
                    raise
            except WLThrowInterrupt as ti:
                msg_expr = (
                    Expression(SymbolThrow, ti.value, ti.tag)
                    if ti.tag
                    else Expression(SymbolThrow, ti.value)
                )
                self.message("Throw", "nocatch", msg_expr)
                self.exc_result = Expression(SymbolHold, msg_expr)

            except BreakInterrupt:
                self.message("Break", "nofdw")
                self.exc_result = Expression(SymbolHold, Expression(SymbolBreak))
            except ContinueInterrupt:
                self.message("Continue", "nofdw")
                self.exc_result = Expression(SymbolHold, Expression(SymbolContinue))
            except TimeoutInterrupt:
                self.stopped = False
                self.deadline = None

                # Due to interrupt handling, we might have already
                # handled a timeout.
                if not self.timeout:
                    self.timeout = True
                    self.message("General", "timeout")

                # Clear shell interrupt if that exists.
                self.exc_result = SymbolAborted
            except AbortInterrupt:  # , error:
                self.exc_result = SymbolAborted
            except TimeConstrainedTimeout:
                # A TimeConstrained turns its own timeout into its failure
                # expression, so none should get here. Should one slip
                # through, the input is aborted rather than the session.
                self.exc_result = SymbolAborted
            except RecursionError:
                # Python ran out of stack before $RecursionLimit was
                # reached: report it the same way.
                # The limit in effect where it ran out, not the one
                # restored since by the Blocks that were left.
                self.message("$RecursionLimit", "reclim", self.recursion_limit)
                self.exc_result = SymbolAborted
            except ReturnInterrupt as ret:
                self.exc_result = ret.expr

                # Clear shell interrupt if that exists.
                if (
                    hasattr(self.shell, "is_inside_interrupt")
                    and self.shell.is_inside_interrupt
                ):
                    self.shell.is_inside_interrupt = False
                    raise

            if self.exc_result is not None:
                self.recursion_depth = 0
                if self.exc_result != self.SymbolNull:
                    result = self.format_output(self.exc_result, format)

            form = None
            if self.last_eval:
                head = self.last_eval.get_head()
                if head in output_forms:
                    form = self.definitions.shorten_name(head.name)

            result = Result(self.out, result, line_no, self.last_eval, form)
            self.out = []
        finally:
            self.stop()
            self.deadline = None
            # A Ctrl-C that came too late for this evaluation to take it
            # must not open the interrupt menu in the next one.
            self.interrupt_request = None
            # $Line could have changed during the evaluation.
            line_no = self.definitions.get_line_no()
            line_no += 1
            self.definitions.set_line_no(line_no)

        history_length = self.definitions.get_history_length()

        line = line_no - history_length - 1
        while line > 0:
            unset_in = self.definitions.unset("In", Expression(SymbolIn, Integer(line)))
            unset_out = self.definitions.unset(
                "Out", Expression(SymbolOut, Integer(line))
            )
            if not (unset_in or unset_out):
                break
            line -= 1
        return result

    def get_stored_result(self, eval_result, output_forms):
        """Return `eval_result` stripped of any format, e.g. FullForm, MathML, TeX
        that it might have been wrapped in.
        """
        if eval_result is None:
            return None
        head = eval_result.get_head()
        if head in output_forms:
            return eval_result.elements[0]

        return eval_result

    def stop(self) -> None:
        self.stopped = True

    @overload
    def format_output(
        self, expr: BaseElement, format: Optional[dict] = None
    ) -> dict: ...

    @overload
    def format_output(
        self, expr: BaseElement, format: Optional[str] = None
    ) -> Union[BaseElement, str, None]: ...

    def format_output(self, expr, format=None):
        """
        This function takes an expression `expr` and
        a format `format`. If `format` is None, then returns `expr`. Otherwise,
        produce an str with the proper format.

        Notice that this function can be overwritten by the front-ends, so it should not be
        used in Builtin classes where it is expected a front-end independent result.
        """
        from mathics.format.box import format_element

        if format is None:
            format = self.format

        if isinstance(format, dict):
            return dict((k, self.format_output(expr, f)) for k, f in format.items())

        from mathics.core.expression import BoxError, Expression

        if format == "text":
            result = format_element(expr, self, SymbolOutputForm)
        elif format == "xml":
            result = format_element(
                Expression(SymbolStandardForm, expr), self, SymbolMathMLForm
            )
        elif format == "latex":
            result = format_element(
                Expression(SymbolStandardForm, expr), self, SymbolTeXForm
            )
        elif format == "unformatted":
            self.exc_result = None
            return expr
        else:
            raise ValueError

        if result is None:
            return None

        try:
            encoding = self.definitions.get_ownvalue("System`$CharacterEncoding").value
        except AttributeError:
            encoding = "Unicode"

        try:
            # With the new implementation, if result is not a ``BoxExpression``
            # then we should raise a BoxError here.
            boxes = result.to_text(evaluation=self, encoding=encoding)
        except BoxError:
            self.message(
                "General", "notboxes", Expression(SymbolFullForm, result).evaluate(self)
            )
            boxes = None
        return boxes

    def set_quiet_messages(self, messages) -> None:
        from mathics.core.list import ListExpression

        value = ListExpression(*messages)
        self.definitions.set_ownvalue("Internal`$QuietMessages", value)

    def get_quiet_messages(self):
        from mathics.core.expression import Expression

        value = self.definitions.get_ownvalues("Internal`$QuietMessages")
        if value:
            try:
                value = value[0].replace
            except AttributeError:
                return []
        if not isinstance(value, Expression):
            return []
        return value.elements

    def message(self, symbol_name: str, tag: str, *msgs) -> Optional["Message"]:
        """
        Format message given its components, ``symbol_name``, ``tag``

        """
        from mathics.core.expression import Expression

        # Allow evaluation.message('MyBuiltin', ...) (assume
        # System`MyBuiltin)
        symbol = ensure_context(symbol_name)
        quiet_messages = set(self.get_quiet_messages())

        pattern = Expression(SymbolMessageName, Symbol(symbol), String(tag))

        if pattern in quiet_messages or self.quiet_all:
            return None

        # Shorten the symbol's name according to the current context
        # settings. This makes sure we print the context, if it would
        # be necessary to find the symbol that this message is
        # attached to.
        symbol_shortname = self.definitions.shorten_name(symbol)

        if settings.DEBUG_PRINT:
            print(f"MESSAGE: {symbol_shortname}::{tag} ({msgs})")

        try:
            text: BaseElement = self.definitions.get_value(
                symbol, "System`Messages", pattern, self
            )
        except ValueError:
            pattern = Expression(SymbolMessageName, Symbol("General"), String(tag))
            try:
                text = self.definitions.get_value(
                    "System`General", "System`Messages", pattern, self
                )
            except ValueError:
                text = String(f"Message {symbol_shortname}::{tag} not found.")

        formatted_text = self.format_output(
            Expression(SymbolStringForm, text, *(from_python(arg) for arg in msgs)),
            "text",
        )

        message = Message(symbol_shortname, tag, str(formatted_text))
        self.out.append(message)
        self.output.out(self.out[-1])
        return message

    def print_out(self, text) -> None:
        from mathics.core.convert.python import from_python

        if self.definitions.trace_evaluation:
            self.definitions.trace_evaluation = False
            text = self.format_output(from_python(text), "text")
            self.is_boxing = False
            self.definitions.trace_evaluation = True
        else:
            text = self.format_output(from_python(text), "text")

        self.out.append(Print(text))
        self.output.out(self.out[-1])
        if settings.DEBUG_PRINT:
            print("OUT: " + text)

    def error(self, symbol, tag, *msgs) -> None:
        # Temporarily reset the recursion limit, to allow the message being
        # formatted
        self.recursion_depth, depth = 0, self.recursion_depth
        try:
            self.message(symbol, tag, *msgs)
        finally:
            self.recursion_depth = depth
        raise AbortInterrupt

    def error_args(self, symbol, given, *needed) -> None:
        self.message_args(symbol, given, *needed)
        raise AbortInterrupt

    def message_args(self, symbol, given, *needed) -> None:
        from mathics.core.symbols import Symbol

        if len(needed) == 1:
            if given > 1 and needed[0] > 1:
                self.message(symbol, "argrx", Symbol(symbol), given, *needed)
            elif given == 1:
                self.message(symbol, "argr", Symbol(symbol), *needed)
            elif needed[0] == 1:
                self.message(symbol, "argx", Symbol(symbol), given)
        elif len(needed) == 2:
            if given == 1:
                self.message(symbol, "argtu", Symbol(symbol), *needed)
            else:
                self.message(symbol, "argt", Symbol(symbol), *needed)
        else:
            raise NotImplementedError

    def check_stopped(self) -> None:
        # The timeout of evaluate() is checked here, between evaluation
        # steps, so that it never interrupts a step halfway.
        if self.deadline is not None and time.time() > self.deadline:
            self.stopped = True
        if self.stopped:
            raise TimeoutInterrupt
        interrupt_request = self.interrupt_request
        if (
            interrupt_request is not None
            and threading.current_thread() is self.evaluating_thread
        ):
            self.interrupt_request = None
            interrupt_request(sys._getframe(1))

    def inc_recursion_depth(self) -> None:
        self.check_stopped()
        limit = self.definitions.get_config_value(
            "System`$RecursionLimit", MAX_RECURSION_DEPTH
        )
        if limit is None:
            # $RecursionLimit is Infinity, as in Block[{$RecursionLimit = Infinity}, ...],
            # which does not go through the assignment that sets the Python limit.
            # Go as deep as the stack is set up to hold.
            limit = MAX_INFINITE_RECURSION_DEPTH
            if sys.getrecursionlimit() < python_recursion_depth(limit):
                set_python_recursion_limit(limit)
        limit = max(limit, MIN_RECURSION_LIMIT)
        self.recursion_limit = limit
        self.recursion_depth += 1
        if self.recursion_depth > limit:
            self.error("$RecursionLimit", "reclim", limit)

    def dec_recursion_depth(self) -> None:
        self.recursion_depth -= 1

    def add_listener(self, tag: str, listener: Callable) -> None:
        existing = self.listeners.get(tag)
        if existing is None:
            existing = self.listeners[tag] = []
        existing.insert(0, listener)

    def remove_listener(self, tag: str, listener: Callable) -> None:
        self.listeners.get(tag, []).remove(listener)

    def publish(self, tag: str, *args, **kwargs) -> None:
        listeners = self.listeners.get(tag, [])
        for listener in listeners:
            if listener(*args, **kwargs):
                break


# TODO: rethink what we want/need here
class Message(_Out):
    def __init__(self, symbol: Union[Symbol, str], tag: str, text: str) -> None:
        """
        A Mathics3 message of some sort. ``symbol`` can either
        be a symbol or a string.

        ``symbol``: classifies which predefined or variable this comes
        from? If there is none use a string.

        ``tag``: a short slug string that indicates the kind of message

        In Django we need to use a string for symbol, since we need
        something that is JSON serializable and a Mathics3 Symbol is
        not like this.
        """
        super(Message, self).__init__()
        self.is_message = True  # Why do we need this?
        self.symbol = symbol
        self.tag = tag
        self.text = text

    def __str__(self) -> str:
        return f"{self.symbol}::{self.tag}: {self.text}"

    def __eq__(self, other) -> bool:
        return self.is_message == other.is_message and self.text == other.text

    def get_data(self):
        return {
            "message": True,
            "symbol": self.symbol,
            "tag": self.tag,
            "prefix": f"{self.symbol}::{self.tag}",
            "text": self.text,
        }


class Print(_Out):
    def __init__(self, text) -> None:
        super(Print, self).__init__()
        self.is_print = True
        self.text = text

    def __str__(self) -> str:
        return self.text

    def __eq__(self, other) -> bool:
        return self.is_message == other.is_message and self.text == other.text

    def get_data(self):
        return {
            "message": False,
            "text": self.text,
        }


class Output(ABC):
    """
    Base class for Mathics3 output history.
    This needs to be subclassed.
    """

    def max_stored_size(self, output_settings) -> int:
        """
        Return the largeet number of history items allowed.
        """
        return output_settings.MAX_STORED_SIZE

    def out(self, out):
        pass

    def clear(self, wait):
        raise NotImplementedError

    def display(self, data, metadata):
        raise NotImplementedError


OutputLines = List[str]


class Result:
    """
    A structure containing the result of an evaluation.

    In particular, there are the following fields:

    result: the actual result produced.

    out: a list of additional output strings. These are warning or
         error messages. See "form" for exactly what they are.

    form: is the *format* of the result which tags the kind of result .
          Think of this as something like a mime/type. Some formats:

      * SyntaxErrors
      * SVG images
      * PNG images
      * text
      * MathML
      * None - defaults to text

    In the future "form" will be renamed "format" or something like this.
    """

    def __init__(
        self, out: List[_Out], result, line_no: int, last_eval=None, form=None
    ) -> None:
        self.out = out
        self.result = result
        self.line_no = line_no
        self.last_eval = last_eval
        self.form = form

    # FIXME: consider using a named tuple
    def get_data(self) -> dict:
        return {
            "out": [out.get_data() for out in self.out],
            "result": self.result,
            "line": self.line_no,
            "form": self.form,
        }
