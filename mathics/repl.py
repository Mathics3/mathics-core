"""
Terminal handling for command-line REPL. Also used by Dialog[] in mathics-core,
but not used by other front-ends.

"""

import atexit
import locale
import os
import os.path as osp
import re
import subprocess
import sys
from typing import Any, List

import mathics_scanner.location
from mathics_scanner.location import ContainerKind

import mathics.core as mathics_core
from mathics import settings
from mathics.core.atoms import String
from mathics.core.evaluation import Evaluation, Output
from mathics.core.expression import Expression
from mathics.core.parser import MathicsFileLineFeeder, MathicsLineFeeder
from mathics.core.streams import stream_manager
from mathics.core.symbols import SymbolNull, strip_context
from mathics.eval.files_io.read import channel_to_stream
from mathics.interrupt import setup_signal_handler
from mathics.session import SessionShell, autoload_files

try:
    import readline
except ImportError:
    have_readline = False
else:
    have_readline = True

    # Set up mathics3 configuration directory
    CONFIGHOME = os.environ.get("XDG_CONFIG_HOME", osp.expanduser("~/.config"))
    CONFIGDIR = osp.join(CONFIGHOME, "Mathics3")
    os.makedirs(CONFIGDIR, exist_ok=True)
    HISTFILE = os.environ.get("MATHICS3_HISTFILE", osp.join(CONFIGDIR, "history"))

    def user_write_history_file():
        try:
            # print(f"Writing {HISTFILE}")
            readline.write_history_file(HISTFILE)
        except:  # noqa
            pass


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


class TerminalShell(MathicsLineFeeder, SessionShell):

    def __init__(
        self,
        definitions,
        colors: str,
        want_readline: bool,
        want_completion: bool,
        autoload=False,
        in_prefix: str = "In",
        out_prefix: str = "Out",
    ):
        super(TerminalShell, self).__init__([], ContainerKind.STREAM)
        self.input_encoding = locale.getpreferredencoding()

        # is_inside_interrupt is set True when shell has been
        # interrupted via an interrupt handler.
        self.is_inside_interrupt = False

        self.lineno = 0
        self.in_prefix = in_prefix
        self.out_prefix = out_prefix

        # Keep track of whether input of a command spans more than one line.
        # In prompting we omit "In[x]:= after the first line.
        self.multiline_input = False

        if want_readline:
            want_readline = have_readline

        if want_completion:
            want_completion = have_readline

        # Try importing readline to enable arrow keys support etc.
        self.using_readline = False
        try:
            if want_readline:
                try:
                    # Load history from file
                    readline.read_history_file(HISTFILE)
                    atexit.register(user_write_history_file)
                except FileNotFoundError:
                    # Create an empty history file.
                    with open(HISTFILE, "w"):
                        pass
                    atexit.register(user_write_history_file)
                except IOError:
                    pass
                except:  # noqa
                    # PyPy read_history_file fails
                    pass
                self.using_readline = sys.stdin.isatty() and sys.stdout.isatty()
                self.ansi_color_re = re.compile("\033\\[[0-9;]+m")
                if want_completion:
                    readline.set_completer(
                        lambda text, state: self.complete_symbol_name(text, state)
                    )

                    # Make _ a delimiter, but not $ or `
                    readline.set_completer_delims(
                        " \t\n_~!@#%^&*()-=+[{]}\\|;:'\",<>/?"
                    )

                    readline.parse_and_bind("tab: complete")
                    self.completion_candidates: List[str] = []

        except ImportError:
            pass

        # Try importing colorama to escape ansi sequences for cross platform
        # colors
        try:
            from colorama import init as colorama_init
        except ImportError:
            colors = "NoColor"
        else:
            colorama_init()
            if colors is None:
                terminal_supports_color = (
                    sys.stdout.isatty() and os.getenv("TERM") != "dumb"
                )
                colors = "Linux" if terminal_supports_color else "NoColor"

        color_schemes = {
            "NOCOLOR": (["", "", "", ""], ["", "", "", ""]),
            "NONE": (["", "", "", ""], ["", "", "", ""]),
            "LINUX": (
                ["\033[32m", "\033[1m", "\033[0m\033[32m", "\033[39m"],
                ["\033[31m", "\033[1m", "\033[0m\033[31m", "\033[39m"],
            ),
            "LIGHTBG": (
                ["\033[34m", "\033[1m", "\033[22m", "\033[39m"],
                ["\033[31m", "\033[1m", "\033[22m", "\033[39m"],
            ),
        }

        # Handle any case by using .upper()
        term_colors = color_schemes.get(colors.upper())
        if term_colors is None:
            out_msg = "The 'colors' argument must be {0} or None"
            print(out_msg.format(repr(list(color_schemes.keys()))))
            sys.exit()

        self.incolors, self.outcolors = term_colors
        self.definitions = definitions
        if autoload:
            autoload_files(definitions, get_srcdir(), "autoload-cli")

    def complete_symbol_name(self, text, state):
        try:
            return self._complete_symbol_name(text, state)
        except Exception:
            # any exception thrown inside the completer gets silently
            # thrown away otherwise
            print("Unhandled error in readline completion")

    def _complete_symbol_name(self, text, state):
        # The readline module calls this function repeatedly,
        # increasing 'state' each time and expecting one string to be
        # returned per call.

        if state == 0:
            self.completion_candidates = self.get_completion_candidates(text)

        try:
            return self.completion_candidates[state]
        except IndexError:
            return None

    def empty(self):
        return False

    def feed(self):
        """
        Prompt for and read another line of input.
        Keep track of the line number and note, after reading,
        in self.multiline_input that if we need to read again, we have already prompted
        for the input.
        """
        result = self.read_line(self.in_prompt) + "\n"
        self.multiline_input = True
        if mathics_scanner.location.TRACK_LOCATIONS:
            self.container.append(self.source_text)
        if result == "\n":
            return ""  # end of input
        self.lineno += 1
        return result

    def get_completion_candidates(self, text):
        matches = self.definitions.get_matching_names(text + "*")
        if "`" not in text:
            matches = [strip_context(m) for m in matches]
        return matches

    @property
    def in_prompt(self) -> str:
        """
        Return the prompt string to be shown before reading input.
        If this is a continuation line for some logical input,
        the prefix returned contains spaces only.
        """
        line_number = self.last_line_number
        if self.multiline_input:
            indent = len(f"In[{line_number}]:= ")
            return " " * indent
        else:
            return "{2}{0}[{3}{1}{4}]:= {5}".format(
                self.in_prefix, line_number, *self.incolors
            )

    @property
    def last_line_number(self):
        """
        Return the line number associated with the next input to be read.
        """
        return self.definitions.get_line_no()

    def get_out_prompt(self, form=None) -> str:
        """
        Return a prompt string to be shown before showing output.
        """
        line_number = self.last_line_number
        if form:
            return "{3}{0}[{4}{1}{5}]//{2}= {6}".format(
                self.out_prefix, line_number, form, *self.outcolors
            )
        return "{2}{0}[{3}{1}{4}]= {5}".format(
            self.out_prefix, line_number, *self.outcolors
        )

    def out_callback(self, out, fmt=None):
        print(self.to_output(str(out), fmt))

    def print_result(self, result, no_out_prompt=False, strict_wl_output=False):
        if result is None or result.last_eval is SymbolNull:
            # Following WMA CLI, if the result is `SymbolNull`, just print an empty line.
            print("")
            return

        form = result.form
        last_eval = result.last_eval

        eval_type = None
        if last_eval is not None:
            try:
                eval_type = last_eval.get_head_name()
            except Exception:
                print(sys.exc_info()[1])
                return

        out_str = str(result.result)
        if eval_type == "System`String" and not strict_wl_output:
            out_str = '"' + out_str.replace('"', r"\"") + '"'
        if eval_type == "System`Graph":
            out_str = "-Graph-"

        output = self.to_output(out_str, form)
        mess = self.get_out_prompt(form) if not no_out_prompt else ""
        print(mess + output + "\n")

    def reset_lineno(self):
        self.lineno = 0

    def read_line(self, prompt: str) -> str:
        """
        Show prompt and read a line of input.
        """
        if self.using_readline:
            return self.rl_read_line(prompt)
        return input(prompt)

    def rl_read_line(self, prompt):
        # Wrap ANSI color sequences in \001 and \002, so readline
        # knows that they're nonprinting.
        prompt = self.ansi_color_re.sub(lambda m: "\001" + m.group(0) + "\002", prompt)

        return input(prompt)

    def to_output(self, text, form=None):
        line_number = self.last_line_number
        newline = "\n" + " " * len("Out[{0}]= ".format(line_number))
        if form:
            newline += (len(form) + 2) * " "
        return newline.join(text.splitlines())


class TerminalOutput(Output):
    def max_stored_size(self, output_settings):
        return None

    def __init__(self, shell):
        self.shell = shell

    def out(self, out):
        return self.shell.out_callback(out)


def eval_loop(feeder: MathicsFileLineFeeder, shell: TerminalShell):
    """
    A read eval/loop for things having file input `feeder`.
    `shell` is a shell session
    """
    try:
        while not feeder.empty():
            evaluation = Evaluation(
                shell.definitions,
                output=TerminalOutput(shell),
                catch_interrupt=False,
            )

            query = evaluation.parse_feeder(feeder)
            if query is None:
                continue
            evaluation.evaluate(query, timeout=settings.TIMEOUT)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")


def interactive_eval_loop(
    shell: TerminalShell,
    full_form: bool,
    strict_wl_output: bool,
    init_signal_handler: bool = True,
    evaluation: Evaluation | None = None,
) -> Any:
    """
    A read eval/loop for an interactive session.
    `shell` is a shell session
    """

    if init_signal_handler:
        setup_signal_handler()

    result = None
    while True:
        try:
            if evaluation is None:
                evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))

                # Store shell into the evaluation so that an interrupt handler
                # has access to this
                evaluation.shell = shell

            shell.multiline_input = False
            query, source_code = evaluation.parse_feeder_returning_code(shell)
            if mathics_core.PRE_EVALUATION_HOOK is not None:
                mathics_core.PRE_EVALUATION_HOOK(query, evaluation)

            show_echo(source_code, evaluation)
            if len(source_code) and source_code[0] == "!":
                if not settings.ENABLE_SYSTEM_COMMANDS:
                    evaluation.message("Run", "dis")
                else:
                    subprocess.run(source_code[1:], shell=True)
                shell.definitions.increment_line_no(1)
                continue
            if query is None:
                continue
            if full_form:
                print(query)
            result = evaluation.evaluate(query, timeout=settings.TIMEOUT)
            if result is not None:
                shell.print_result(result, strict_wl_output=strict_wl_output)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except EOFError:
            print("\n\nGoodbye!\n")
            break
        except SystemExit:
            # raise to pass the error code on, e.g. Quit[1]
            raise
        finally:
            shell.reset_lineno()
    return result


def show_echo(query, evaluation):
    echovar = evaluation.definitions.get_ownvalue("System`$Echo")
    if not isinstance(echovar, Expression) or not echovar.has_form("List", None):
        return

    for element in echovar.elements:
        if isinstance(element, String) and element.value == "stdout":
            stream = stream_manager.lookup_stream(1)
        else:
            strm = channel_to_stream(element, mode="w")
            if strm is None:
                continue
            stream = stream_manager.lookup_stream(strm.elements[1].value)
            if stream is None or stream.io is None or stream.io.closed:
                continue
        if stream is not None and stream.io is not None:
            stream.io.write(query + "\n")
