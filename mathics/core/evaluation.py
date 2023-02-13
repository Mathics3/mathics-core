# -*- coding: utf-8 -*-

import os
import sys
import time
from queue import Queue
from threading import Thread, stack_size as set_thread_stack_size
from typing import List, Optional, Tuple, Union

from mathics_scanner import TranslateError

from mathics import settings
from mathics.core.atoms import Integer, String
from mathics.core.convert.python import from_python
from mathics.core.element import BaseElement, KeyComparable, ensure_context
from mathics.core.interrupt import (
    AbortInterrupt,
    BreakInterrupt,
    ContinueInterrupt,
    ReturnInterrupt,
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


def _thread_target(request, queue) -> None:
    try:
        result = request()
        queue.put((True, result))
    except BaseException:
        exc_info = sys.exc_info()
        queue.put((False, exc_info))


# MAX_RECURSION_DEPTH gives the maximum value allowed for $RecursionLimit. it's usually set to its
# default settings.DEFAULT_MAX_RECURSION_DEPTH.

MAX_RECURSION_DEPTH = max(
    settings.DEFAULT_MAX_RECURSION_DEPTH,
    int(os.getenv("MATHICS_MAX_RECURSION_DEPTH", settings.DEFAULT_MAX_RECURSION_DEPTH)),
)


def python_recursion_depth(n) -> int:
    # convert Mathics3 recursion depth to Python recursion depth. this estimates how many Python calls
    # we need at worst to process one Mathics3 recursion.
    return 200 + 30 * n


def python_stack_size(n) -> int:  # n is a Mathics3 recursion depth
    # python_stack_frame_size is the (maximum) number of bytes Python needs for one call on the stack.
    python_stack_frame_size = 512  # value estimated experimentally
    return python_recursion_depth(n) * python_stack_frame_size


def set_python_recursion_limit(n) -> None:
    "Sets the required python recursion limit given $RecursionLimit value"
    python_depth = python_recursion_depth(n)
    sys.setrecursionlimit(python_depth)
    if sys.getrecursionlimit() != python_depth:
        raise OverflowError


def run_with_timeout_and_stack(request, timeout, evaluation):
    """
    interrupts evaluation after a given time period. Provides a suitable stack environment.
    """

    # only use set_thread_stack_size if max recursion depth was changed via the environment variable
    # MATHICS_MAX_RECURSION_DEPTH. if it is set, we always use a thread, even if timeout is None, in
    # order to be able to set the thread stack size.

    if MAX_RECURSION_DEPTH > settings.DEFAULT_MAX_RECURSION_DEPTH:
        set_thread_stack_size(python_stack_size(MAX_RECURSION_DEPTH))
    elif timeout is None:
        return request()

    queue = Queue(maxsize=1)  # stores the result or exception
    thread = Thread(target=_thread_target, args=(request, queue))
    thread.start()

    # Thead join(timeout) can leave zombie threads (we are the parent)
    # when a time out occurs, but the thread hasn't terminated.  See
    # https://docs.python.org/3/library/multiprocessing.shared_memory.html
    # for a detailed discussion of this.
    #
    # To reduce this problem, we make use of specific properties of
    # the Mathics3 evaluator: if we set "evaluation.timeout", the
    # next call to "Expression.evaluate" in the thread will finish it
    # immediately.
    #
    # However this still will not terminate long-running processes
    # in Sympy or or libraries called by Mathics3 that might hang or run
    # for a long time.
    thread.join(timeout)
    if thread.is_alive():
        evaluation.timeout = True
        while thread.is_alive():
            pass
        evaluation.timeout = False
        evaluation.stopped = False
        raise TimeoutInterrupt()

    success, result = queue.get()
    if success:
        return result
    else:
        raise result[0].with_traceback(result[1], result[2])


class _Out(KeyComparable):
    def __init__(self) -> None:
        self.is_message = False
        self.is_print = False
        self.text = ""

    def get_sort_key(self) -> Tuple[bool, bool, str]:
        return (self.is_message, self.is_print, self.text)


class Evaluation:
    def __init__(
        self, definitions=None, output=None, format="text", catch_interrupt=True
    ) -> None:
        from mathics.core.definitions import Definitions

        if definitions is None:
            definitions = Definitions()
        self.definitions = definitions
        self.recursion_depth = 0
        self.timeout = False
        self.timeout_queue = []
        self.stopped = False
        self.out = []
        self.output = output if output else Output()
        self.listeners = {}
        self.options = None
        self.predetermined_out = None

        self.quiet_all = False
        self.format = format
        self.catch_interrupt = catch_interrupt
        self.SymbolNull = SymbolNull

        # status of last evaluate
        self.exc_result = self.SymbolNull
        self.last_eval = None
        # Used in ``mathics.builtin.numbers.constants.get_constant`` and
        # ``mathics.builtin.numeric.N``.
        self._preferred_n_method = []

    def parse(self, query):
        "Parse a single expression and print the messages."
        from mathics.core.parser import MathicsSingleLineFeeder

        return self.parse_feeder(MathicsSingleLineFeeder(query))

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
        """
        from mathics.core.parser.util import parse_returning_code

        try:
            result, source_code = parse_returning_code(self.definitions, feeder)
        except TranslateError:
            self.recursion_depth = 0
            self.stopped = False
            source_code = ""
            result = None
        messages = feeder.send_messages(self)
        return result, source_code, messages

    def evaluate(self, query, timeout=None, format=None):
        """
        Evaluate a Mathics3 expression and return the result of evaluation.

        On return self.exc_result will contain status of various
        exception type of result like $Aborted, Overflow, Break, or Continue.
        If none of the above applies self.exc_result is Null
        """
        from mathics.core.convert.expression import to_expression
        from mathics.core.expression import Expression
        from mathics.core.rules import Rule

        self.start_time = time.time()
        self.recursion_depth = 0
        self.timeout = False
        self.stopped = False
        self.exc_result = self.SymbolNull
        self.last_eval = None
        if format is None:
            format = self.format

        output_forms = self.definitions.outputforms

        line_no = self.definitions.get_line_no()
        line_no += 1
        self.definitions.set_line_no(line_no)

        history_length = self.definitions.get_history_length()

        result = None

        def check_io_hook(hook):
            return len(self.definitions.get_ownvalues(hook)) > 0

        def evaluate():
            if history_length > 0:
                self.definitions.add_rule(
                    "In", Rule(to_expression("In", line_no), query)
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
                    "Out", Rule(Expression(SymbolOut, Integer(line_no)), stored_result)
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
                result = run_with_timeout_and_stack(evaluate, timeout, self)
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
                if ti.tag:
                    self.exc_result = Expression(
                        SymbolHold, Expression(SymbolThrow, ti.value, ti.tag)
                    )
                else:
                    self.exc_result = Expression(
                        SymbolHold, Expression(SymbolThrow, ti.value)
                    )
                self.message("Throw", "nocatch", self.exc_result)
            #            except OverflowError:
            #                print("Catch the overflow")
            #                self.message("General", "ovfl")
            #                self.exc_result = Expression(SymbolOverflow)
            except BreakInterrupt:
                self.message("Break", "nofdw")
                self.exc_result = Expression(SymbolHold, Expression(SymbolBreak))
            except ContinueInterrupt:
                self.message("Continue", "nofdw")
                self.exc_result = Expression(SymbolHold, Expression(SymbolContinue))
            except TimeoutInterrupt:
                self.stopped = False
                self.timeout = True
                self.message("General", "timeout")
                self.exc_result = SymbolAborted
            except AbortInterrupt:  # , error:
                self.exc_result = SymbolAborted
            except ReturnInterrupt as ret:
                self.exc_result = ret.expr

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

        history_length = self.definitions.get_history_length()

        line = line_no - history_length
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
        head = eval_result.get_head()
        if head in output_forms:
            return eval_result.elements[0]

        return eval_result

    def stop(self) -> None:
        self.stopped = True

    def format_output(
        self, expr: BaseElement, format: Optional[str] = None
    ) -> Union[BaseElement, str]:
        """
        This function takes an expression `expr` and
        a format `format`. If `format` is None, then returns `expr`. Otherwise,
        produce an str with the proper format.

        Notice that this function can be overwritten by the front-ends, so it should not be
        used in Builtin classes where it is expected a front-end independent result.
        """
        from mathics.eval.makeboxes import format_element

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

        try:
            # With the new implementation, if result is not a ``BoxExpression``
            # then we should raise a BoxError here.
            boxes = result.boxes_to_text(evaluation=self)
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

        value = self.definitions.get_definition("Internal`$QuietMessages").ownvalues
        if value:
            try:
                value = value[0].replace
            except AttributeError:
                return []
        if not isinstance(value, Expression):
            return []
        return value.elements

    def message(self, symbol_name: str, tag, *msgs) -> "Message":
        """
        Format message given its components, ``symbol``, ``tag``


        """
        from mathics.core.expression import Expression

        # Allow evaluation.message('MyBuiltin', ...) (assume
        # System`MyBuiltin)
        symbol = ensure_context(symbol_name)
        quiet_messages = set(self.get_quiet_messages())

        pattern = Expression(SymbolMessageName, Symbol(symbol), String(tag))

        if pattern in quiet_messages or self.quiet_all:
            return

        # Shorten the symbol's name according to the current context
        # settings. This makes sure we print the context, if it would
        # be necessary to find the symbol that this message is
        # attached to.
        symbol_shortname = self.definitions.shorten_name(symbol)

        if settings.DEBUG_PRINT:
            print("MESSAGE: %s::%s (%s)" % (symbol_shortname, tag, msgs))

        text = self.definitions.get_value(symbol, "System`Messages", pattern, self)
        if text is None:
            pattern = Expression(SymbolMessageName, Symbol("General"), String(tag))
            text = self.definitions.get_value(
                "System`General", "System`Messages", pattern, self
            )

        if text is None:
            text = String("Message %s::%s not found." % (symbol_shortname, tag))

        text = self.format_output(
            Expression(SymbolStringForm, text, *(from_python(arg) for arg in msgs)),
            "text",
        )

        message = Message(symbol_shortname, tag, text)
        self.out.append(message)
        self.output.out(self.out[-1])
        return message

    def print_out(self, text) -> None:
        from mathics.core.convert.python import from_python

        if self.definitions.trace_evaluation:
            self.definitions.trace_evaluation = False
            text = self.format_output(from_python(text), "text")
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
            needed = needed[0]
            if given > 1 and needed > 1:
                self.message(symbol, "argrx", Symbol(symbol), given, needed)
            elif given == 1:
                self.message(symbol, "argr", Symbol(symbol), needed)
            elif needed == 1:
                self.message(symbol, "argx", Symbol(symbol), given)
        elif len(needed) == 2:
            if given == 1:
                self.message(symbol, "argtu", Symbol(symbol), *needed)
            else:
                self.message(symbol, "argt", Symbol(symbol), *needed)
        else:
            raise NotImplementedError

    def check_stopped(self) -> None:
        if self.stopped:
            raise TimeoutInterrupt

    def inc_recursion_depth(self) -> None:
        self.check_stopped()
        limit = self.definitions.get_config_value(
            "$RecursionLimit", MAX_RECURSION_DEPTH
        )
        if limit is not None:
            if limit < 20:
                limit = 20
            self.recursion_depth += 1
            if self.recursion_depth > limit:
                self.error("$RecursionLimit", "reclim", limit)

    def dec_recursion_depth(self) -> None:
        self.recursion_depth -= 1

    def add_listener(self, tag, listener) -> None:
        existing = self.listeners.get(tag)
        if existing is None:
            existing = self.listeners[tag] = []
        existing.insert(0, listener)

    def remove_listener(self, tag, listener) -> None:
        self.listeners.get(tag).remove(listener)

    def publish(self, tag, *args, **kwargs) -> None:
        listeners = self.listeners.get(tag, [])
        for listener in listeners:
            if listener(*args, **kwargs):
                break


# TODO: rethink what we want/need here
class Message(_Out):
    def __init__(self, symbol: Union[Symbol, str], tag: str, text: str) -> None:
        """
        A Mathics3 message of some sort. symbol_or_string can either be a symbol or a
        string.

        Symbol: classifies which predefined or variable this comes from? If there is none
                use a string.
        tag: a short slug string that indicates the kind of message

        In Django we need to use a string for symbol, since we need something that is JSON serializable
        and a Mathics3 Symbol is not like this.
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
            "prefix": "%s::%s" % (self.symbol, self.tag),
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


class Output:
    def max_stored_size(self, settings) -> int:
        return settings.MAX_STORED_SIZE

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
    out: a list of additional output strings. These are warning or error messages. See "form"
         for exactly what they are.
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
        self, out: OutputLines, result, line_no: int, last_eval=None, form=None
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
