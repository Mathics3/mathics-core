"""
Message-related functions.
"""

import typing
from typing import Any

from mathics.core.atoms import String
from mathics.core.attributes import A_HOLD_ALL, A_HOLD_FIRST, A_LOCKED, A_PROTECTED
from mathics.core.builtin import Builtin, InfixOperator, Predefined
from mathics.core.evaluation import Evaluation, Message as EvaluationMessage
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolMessageName, SymbolQuiet


class Aborted(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/Aborted.html</url>

    <dl>
    <dt>'\$Aborted'
        <dd>is returned by a calculation that has been aborted.
    </dl>
    """

    attributes = A_LOCKED | A_PROTECTED
    summary_text = "return value for aborted evaluations"
    name = "$Aborted"


class Check(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Check.html</url>

    <dl>
      <dt>'Check'[$expr$, $failexpr$]
      <dd>evaluates $expr$, and returns the result, unless messages were \
          generated, in which case it evaluates and $failexpr$ will be returned.
      <dt>'Check'[$expr$, $failexpr$, {s1::t1,s2::t2,...}]
      <dd>checks only for the specified messages.
    </dl>

    Return err when a message is generated:
    >> Check[1/0, err]
     : Infinite expression 1 / 0 encountered.
     = err

    Check only for specific messages:
    >> Check[Sin[0^0], err, Sin::argx]
     : Indeterminate expression 0 ^ 0 encountered.
     = Indeterminate

    >> Check[1/0, err, Power::infy]
     : Infinite expression 1 / 0 encountered.
     = err


    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "argmu": "Check called with 1 argument; 2 or more arguments are expected.",
        "name": "Message name `1` is not of the form symbol::name or symbol::name::language.",
    }

    summary_text = "discard the result if the evaluation produced messages"

    def eval(self, expr, evaluation: Evaluation):
        "Check[expr_]"
        evaluation.message("Check", "argmu")

    def eval_with_fail(self, expr, failexpr, params, evaluation: Evaluation):
        "Check[expr_, failexpr_, params___]"

        # Todo: To implement the third form of this function , we need to implement the function $MessageGroups first
        # <dt>'Check'[$expr$, $failexpr$, "name"]
        # <dd>checks only for messages in the named message group.

        def get_msg_list(exprs):
            messages = []
            for expr in exprs:
                if expr.has_form("List", None):
                    messages.extend(get_msg_list(expr.elements))
                elif check_message(expr):
                    messages.append(expr)
                else:
                    raise Exception(expr)
            return messages

        check_messages = set(evaluation.get_quiet_messages())
        display_fail_expr = False

        params = params.get_sequence()
        if len(params) == 0:
            result = expr.evaluate(evaluation)
            if len(evaluation.out):
                display_fail_expr = True
        else:
            try:
                msgs = get_msg_list(params)
                for x in msgs:
                    check_messages.add(x)
            except Exception as inst:
                evaluation.message("Check", "name", inst.args[0])
                return
            curr_msg = len(evaluation.out)
            result = expr.evaluate(evaluation)
            own_messages = evaluation.out[curr_msg:]
            for out_msg in own_messages:
                if type(out_msg) is not EvaluationMessage:
                    continue
                pattern = Expression(
                    SymbolMessageName, Symbol(out_msg.symbol), String(out_msg.tag)
                )
                if pattern in check_messages:
                    display_fail_expr = True
                    break
        return failexpr if display_fail_expr is True else result


class Failed(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$Failed.html</url>
    <dl>
    <dt>'\$Failed'
        <dd>is returned by some functions in the event of an error.
    </dl>
    """

    summary_text = "retrieved result for failed evaluations"
    name = "$Failed"


class Failure(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Failure.html</url>

    <dl>
      <dt>Failure[$tag$, $assoc$]
      <dd> represents a failure of a type indicated by $tag$, with details \
           given by the association $assoc$.
    </dl>
    """

    summary_text = "a failure at the level of the interpreter"


class General(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/General.html</url>

    <dl>
      <dt>'General'
      <dd>is a symbol to which all general-purpose messages are assigned.
    </dl>

    >> General::argr
     = `1` called with 1 argument; `2` arguments are expected.
    >> Message[Rule::argr, Rule, 2]
     : Rule called with 1 argument; 2 arguments are expected.
    """

    messages = {
        "argb": (
            "`1` called with `2` arguments; "
            "between `3` and `4` arguments are expected."
        ),
        "argct": "`1` called with `2` arguments.",
        "argctu": "`1` called with 1 argument.",
        "argr": "`1` called with 1 argument; `2` arguments are expected.",
        "argrx": "`1` called with `2` arguments; `3` arguments are expected.",
        "argx": "`1` called with `2` arguments; 1 argument is expected.",
        "argt": (
            "`1` called with `2` arguments; " "`3` or `4` arguments are expected."
        ),
        "argtu": ("`1` called with 1 argument; `2` or `3` arguments are expected."),
        "base": "Requested base `1` in `2` should be between 2 and `3`.",
        "boxfmt": "`1` is not a box formatting type.",
        "charcode": "The character encoding `1` is not supported. Use $CharacterEncodings to list supported encodings.",
        "color": "`1` is not a valid color or gray-level specification.",
        "cxt": "`1` is not a valid context name.",
        "divz": "The argument `1` should be nonzero.",
        "digit": "Digit at position `1` in `2` is too large to be used in base `3`.",
        "exact": "Argument `1` is not an exact number.",
        "fnsym": (
            "First argument in `1` is not a symbol " "or a string naming a symbol."
        ),
        "heads": "Heads `1` and `2` are expected to be the same.",
        "ilsnn": (
            "Single or list of non-negative integers expected at " "position `1`."
        ),
        "indet": "Indeterminate expression `1` encountered.",
        "innf": "Non-negative integer or Infinity expected at position `1` in `2`",
        "int": "Integer expected.",
        "intp": "Positive integer expected.",
        "intnn": "Non-negative integer expected.",
        "intnm": "Non-negative machine-sized integer expected at position `1` in `2`.",
        "iterb": "Iterator does not have appropriate bounds.",
        "ivar": "`1` is not a valid variable.",
        "level": ("Level specification `1` is not of the form n, " "{n}, or {m, n}."),
        "locked": "Symbol `1` is locked.",
        "matsq": "Argument `1` is not a non-empty square matrix.",
        "newpkg": "In WL, there is a new package for this.",
        "noopen": "Cannot open `1`.",
        "nord": "Invalid comparison with `1` attempted.",
        "normal": "Nonatomic expression expected at position `1` in `2`.",
        "noval": ("Symbol `1` in part assignment does not have an immediate value."),
        "obspkg": "In WL, this package is obsolete.",
        "openx": "`1` is not open.",
        "optb": "Optional object `1` in `2` is not a single blank.",
        "ovfl": "Overflow occurred in computation.",
        "partd": "Part specification is longer than depth of object.",
        "partw": "Part `1` of `2` does not exist.",
        "plld": "Endpoints in `1` must be distinct machine-size real numbers.",
        "plln": "Limiting value `1` in `2` is not a machine-size real number.",
        "pspec": (
            "Part specification `1` is neither an integer nor " "a list of integer."
        ),
        "psl": "Position specification `1` in `2` is not a machine-sized integer or a list of machine-sized integers.",
        "rvalue": "`1` is not a variable with a value, so its value cannot be changed.",
        "seqs": "Sequence specification expected, but got `1`.",
        "setp": "Part assignment to `1` could not be made",
        "setps": "`1` in the part assignment is not a symbol.",
        "span": "`1` is not a valid Span specification.",
        "ssym": "`1` is not a symbol or a string.",
        "stream": "`1` is not string, InputStream[], or OutputStream[]",
        "string": "String expected.",
        "strse": "String or list of strings expected at position `1` in `2`.",
        "sym": "Argument `1` at position `2` is expected to be a symbol.",
        "tag": "Rule for `1` can only be attached to `2`.",
        "take": "Cannot take positions `1` through `2` in `3`.",
        "ucdec": "An invalid unicode sequence was encountered and ignored.",
        "vrule": (
            "Cannot set `1` to `2`, " "which is not a valid list of replacement rules."
        ),
        "write": "Tag `1` in `2` is Protected.",
        "wrsym": "Symbol `1` is Protected.",
        # TODO: someone please explain why these are different...
        # Self-defined messages
        "rep": "`1` is not a valid replacement rule.",
        "options": "`1` is not a valid list of option rules.",
        "timeout": "Timeout reached.",
        "syntax": "`1`",
        "invalidargs": "Invalid arguments.",
        "notboxes": "`1` is not a valid box structure.",
        "pyimport": '`1`[] is not available. Python module "`2`" is not installed.',
    }
    summary_text = "general-purpose messages"


class Message(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Message.html</url>

    <dl>
      <dt>'Message'[$symbol$::$msg$, $expr_1$, $expr_2$, ...]
      <dd>displays the specified message, replacing placeholders in
        the message text with the corresponding expressions.
    </dl>

    >> a::b = "Hello world!"
     = Hello world!
    >> Message[a::b]
     : Hello world!
    >> a::c := "Hello `1`, Mr 00`2`!"
    >> Message[a::c, "you", 3 + 4]
     : Hello you, Mr 007!
    """

    attributes = A_HOLD_FIRST | A_PROTECTED

    messages = {
        "name": "Message name `1` is not of the form symbol::name or symbol::name::language."
    }
    summary_text = "display a message"

    def eval(self, symbol: Symbol, tag: String, params, evaluation: Evaluation):
        "Message[MessageName[symbol_Symbol, tag_String], params___]"

        params = params.get_sequence()
        evaluation.message(symbol.name, tag.value, *params)
        return SymbolNull


def check_message(expr) -> bool:
    "checks if an expression is a valid message"
    if expr.has_form("MessageName", 2):
        symbol, tag = expr.elements
        if symbol.get_name() and tag.get_string_value():
            return True
    return False


class MessageName(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MessageName.html</url>

    <dl>
      <dt>'MessageName'[$symbol$, $tag$]
      <dt>'$symbol$::$tag$'
      <dd>identifies a message.
    </dl>

    'MessageName' is the head of message IDs of the form 'symbol::tag'.
    >> FullForm[a::b]
     = MessageName[a, "b"]

    The second parameter 'tag' is interpreted as a string.
    >> FullForm[a::"b"]
     = MessageName[a, "b"]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    default_formats = False
    formats: typing.Dict[str, Any] = {}
    messages = {"messg": "Message cannot be set to `1`. It must be set to a string."}
    rules = {
        "MakeBoxes[MessageName[symbol_Symbol, tag_String], "
        "f:StandardForm|TraditionalForm|OutputForm]": (
            'RowBox[{MakeBoxes[symbol, f], "::", MakeBoxes[tag, f]}]'
        ),
        "MakeBoxes[MessageName[symbol_Symbol, tag_String], InputForm]": (
            'RowBox[{MakeBoxes[symbol, InputForm], "::", tag}]'
        ),
    }
    summary_text = "associate a message name with a tag"

    def eval(self, symbol: Symbol, tag: String, evaluation: Evaluation):
        "MessageName[symbol_Symbol, tag_String]"

        pattern = Expression(SymbolMessageName, symbol, tag)
        try:
            return evaluation.definitions.get_value(
                symbol.get_name(), "System`Messages", pattern, evaluation
            )
        except ValueError:
            return None


class Off(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Off.html</url>

    <dl>
      <dt>'Off'[$symbol$::$tag$]
      <dd>turns a message off so it is no longer printed.
    </dl>

    >> Off[Power::infy]
    >> 1 / 0
     = ComplexInfinity

    >> Off[Power::indet, Syntax::com]
    >> {0 ^ 0,}
     = {Indeterminate, Null}
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "turn off a message for printing"

    def eval(self, expr, evaluation: Evaluation):
        "Off[expr___]"

        seq = expr.get_sequence()
        quiet_messages = set(evaluation.get_quiet_messages())

        if not seq:
            # TODO Off[s::trace] for all symbols
            return

        for e in seq:
            if isinstance(e, Symbol):
                quiet_messages.add(Expression(SymbolMessageName, e, String("trace")))
            elif check_message(e):
                quiet_messages.add(e)
            else:
                evaluation.message("Message", "name", e)
            evaluation.set_quiet_messages(quiet_messages)

        return SymbolNull


class On(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/On.html</url>

    <dl>
      <dt>'On'[$symbol$::$tag$]
      <dd>turns a message on for printing.
    </dl>

    >> Off[Power::infy]
    >> 1 / 0
     = ComplexInfinity
    >> On[Power::infy]
    >> 1 / 0
     : Infinite expression 1 / 0 encountered.
     = ComplexInfinity
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "turn on a message for printing"

    def eval(self, expr, evaluation: Evaluation):
        "On[expr___]"

        seq = expr.get_sequence()
        quiet_messages = set(evaluation.get_quiet_messages())

        if not seq:
            # TODO On[s::trace] for all symbols
            return

        for e in seq:
            if isinstance(e, Symbol):
                quiet_messages.discard(
                    Expression(SymbolMessageName, e, String("trace"))
                )
            elif check_message(e):
                quiet_messages.discard(e)
            else:
                evaluation.message("Message", "name", e)
            evaluation.set_quiet_messages(quiet_messages)
        return SymbolNull


class Quiet(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Quiet.html</url>

    <dl>
      <dt>'Quiet'[$expr$, {$s_1$::$t_1$, ...}]
      <dd>evaluates $expr$, without messages '{$s_1$::$t_1$, ...}' being displayed.
      <dt>'Quiet'[$expr$, All]
      <dd>evaluates $expr$, without any messages being displayed.
      <dt>'Quiet'[$expr$, None]
      <dd>evaluates $expr$, without all messages being displayed.
      <dt>'Quiet'[$expr$, $off$, $on$]
      <dd>evaluates $expr$, with messages $off$ being suppressed, but messages $on$ being displayed.
    </dl>

    Evaluate without generating messages:
    >> Quiet[1/0]
     = ComplexInfinity

    Same as above:
    >> Quiet[1/0, All]
     = ComplexInfinity

    >> a::b = "Hello";
    >> Quiet[x+x, {a::b}]
     = 2 x

    >> Quiet[Message[a::b]; x+x, {a::b}]
     = 2 x

    >> Message[a::b]; y=Quiet[Message[a::b]; x+x, {a::b}]; Message[a::b]; y
     : Hello
     : Hello
     = 2 x

    >> Quiet[x + x, {a::b}, {a::b}]
     : In Quiet[x + x, {a::b}, {a::b}] the message name(s) {a::b} appear in both the list of messages to switch off and the list of messages to switch on.
     = Quiet[x + x, {a::b}, {a::b}]
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "anmlist": (
            "Argument `1` of `2` should be All, None, a message name, "
            "or a list of message names."
        ),
        "allall": "Arguments 2 and 3 of `1` should not both be All.",
        "conflict": (
            "In `1` the message name(s) `2` appear in both the list of "
            "messages to switch off and the list of messages to switch on."
        ),
    }

    rules = {
        "Quiet[expr_]": "Quiet[expr, All]",
        "Quiet[expr_, moff_]": "Quiet[expr, moff, None]",
    }
    summary_text = "evaluate without showing messages"

    def eval(self, expr, moff, mon, evaluation: Evaluation):
        "Quiet[expr_, moff_, mon_]"

        def get_msg_list(expr):
            if check_message(expr):
                expr = ListExpression(expr)
            if expr.get_name() == "System`All":
                all = True
                messages = []
            elif expr.get_name() == "System`None":
                all = False
                messages = []
            elif expr.has_form("List", None):
                all = False
                messages = []
                for item in expr.elements:
                    if check_message(item):
                        messages.append(item)
                    else:
                        raise ValueError
            else:
                raise ValueError
            return all, messages

        old_quiet_all = evaluation.quiet_all
        old_quiet_messages = set(evaluation.get_quiet_messages())
        quiet_messages = old_quiet_messages.copy()
        try:
            quiet_expr = Expression(SymbolQuiet, expr, moff, mon)
            try:
                off_all, off_messages = get_msg_list(moff)
            except ValueError:
                evaluation.message("Quiet", "anmlist", 2, quiet_expr)
                return
            try:
                on_all, on_messages = get_msg_list(mon)
            except ValueError:
                evaluation.message("Quiet", "anmlist", 2, quiet_expr)
                return
            if off_all and on_all:
                evaluation.message("Quiet", "allall", quiet_expr)
                return
            evaluation.quiet_all = off_all
            conflict = []
            for off in off_messages:
                if off in on_messages:
                    conflict.append(off)
                    break
            if conflict:
                evaluation.message(
                    "Quiet", "conflict", quiet_expr, ListExpression(*conflict)
                )
                return
            for off in off_messages:
                quiet_messages.add(off)
            for on in on_messages:
                quiet_messages.discard(on)
            if on_all:
                quiet_messages = set()
            evaluation.set_quiet_messages(quiet_messages)

            return expr.evaluate(evaluation)
        finally:
            evaluation.quiet_all = old_quiet_all
            evaluation.set_quiet_messages(old_quiet_messages)


# Consider removing. If this was this added just to test some expressions,
# this should be done in pytests instead.
class Syntax(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/guide/Syntax.html</url>

    <dl>
      <dt>'Syntax'
      <dd>is a symbol to which all syntax messages are assigned.
    </dl>

    >> 1 +
     : Incomplete expression; more input is needed (line 1 of "<test-Syntax-1>").

    >> Sin[1)
     : "Sin[1" cannot be followed by ")" (line 1 of "<test-Syntax-2>").

    >> ^ 2
     : Expression cannot begin with "^ 2" (line 1 of "<test-Syntax-3>").

    >> 1.5``
     : "1.5`" cannot be followed by "`" (line 1 of "<test-Syntax-4>").
    """

    # Extension: WMA does not provide lineno and filename in its error messages
    messages = {
        "bktmch": "`1` must be followed by `2`, not `3` (line `4` of `5`).",
        "bktwrn": "`1` represents multiplication; use `2` to represent a function (line `4` of `5`).",  # TODO
        "com": "Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line `4` of `5`).",
        "snthex": r"4 hexadecimal digits are required after \: to construct a 16-bit character (line `4` of `5`).",
        "sntoct1": r"3 octal digits are required after \ to construct an 8-bit character.",
        "sntoct2": r"2 hexadecimal digits are required after \. to construct an 8-bit character.",
        "sntue": "Unexpected end of file; probably unfinished expression (line `4` of `5`).",
        "sntufn": "Unknown unicode longname `1` (line `4` of `5`).",
        "sntxb": "Expression cannot begin with `1` (line `4` of `5`).",
        "sntxf": "`1` cannot be followed by `2` (line `4` of `5`).",
        "sntxi": "Incomplete expression; more input is needed (line `4` of `5`).",
        "stresc": "Unknown string escape `1`",
    }
    summary_text = "syntax messages"
