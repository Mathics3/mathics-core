#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simpler Command-line interface to Mathics3.

See also mathicsscript for a more sophisticated, and full
featured CLI, which uses in more add-on Python packages and modules
to assist in command-line behavior.
"""

import argparse
import atexit
import cProfile
import locale
import os
import os.path as osp
import re
import subprocess
import sys
from typing import List

import mathics.core as mathics_core
from mathics import __version__, license_string, settings, version_string
from mathics.builtin.trace import TraceBuiltins, traced_apply_function
from mathics.core.atoms import String
from mathics.core.definitions import Definitions, Symbol
from mathics.core.evaluation import Evaluation, Output
from mathics.core.expression import Expression
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.parser import MathicsFileLineFeeder, MathicsLineFeeder
from mathics.core.rules import FunctionApplyRule
from mathics.core.streams import stream_manager
from mathics.core.symbols import SymbolNull, strip_context
from mathics.eval.files_io.files import set_input_var
from mathics.eval.files_io.read import channel_to_stream
from mathics.session import autoload_files
from mathics.settings import DATA_DIR, USER_PACKAGE_DIR, ensure_directory
from mathics.timing import show_lru_cache_statistics

# from mathics.timing import TimeitContextManager
# with TimeitContextManager("import_and_load_builtins()"):
#     import_and_load_builtins()

import_and_load_builtins()


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


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


class TerminalShell(MathicsLineFeeder):
    def __init__(
        self,
        definitions,
        colors,
        want_readline,
        want_completion,
        autoload=False,
        in_prefix: str = "In",
        out_prefix: str = "Out",
    ):
        super(TerminalShell, self).__init__("<stdin>")
        self.input_encoding = locale.getpreferredencoding()
        self.lineno = 0
        self.in_prefix = in_prefix
        self.out_prefix = out_prefix

        # Try importing readline to enable arrow keys support etc.
        self.using_readline = False
        try:
            if want_readline:
                import readline

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

    def get_last_line_number(self):
        return self.definitions.get_line_no()

    def get_in_prompt(self):
        next_line_number = self.get_last_line_number() + 1
        if self.lineno > 0:
            return " " * len("{0}[{1}]:= ".format(self.in_prefix, next_line_number))
        else:
            return "{2}{0}[{3}{1}{4}]:= {5}".format(
                self.in_prefix, next_line_number, *self.incolors
            )

    def get_out_prompt(self, form=None):
        line_number = self.get_last_line_number()
        if form:
            return "{3}{0}[{4}{1}{5}]//{2}= {6}".format(
                self.out_prefix, line_number, form, *self.outcolors
            )
        return "{2}{0}[{3}{1}{4}]= {5}".format(
            self.out_prefix, line_number, *self.outcolors
        )

    def to_output(self, text, form=None):
        line_number = self.get_last_line_number()
        newline = "\n" + " " * len("Out[{0}]= ".format(line_number))
        if form:
            newline += (len(form) + 2) * " "
        return newline.join(text.splitlines())

    def out_callback(self, out, fmt=None):
        print(self.to_output(str(out), fmt))

    def read_line(self, prompt):
        if self.using_readline:
            return self.rl_read_line(prompt)
        return input(prompt)

    def print_result(self, result, no_out_prompt=False, strict_wl_output=False):
        if result is None:
            # FIXME decide what to do here
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

    def rl_read_line(self, prompt):
        # Wrap ANSI colour sequences in \001 and \002, so readline
        # knows that they're nonprinting.
        prompt = self.ansi_color_re.sub(lambda m: "\001" + m.group(0) + "\002", prompt)

        return input(prompt)

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

    def get_completion_candidates(self, text):
        matches = self.definitions.get_matching_names(text + "*")
        if "`" not in text:
            matches = [strip_context(m) for m in matches]
        return matches

    def reset_lineno(self):
        self.lineno = 0

    def feed(self):
        result = self.read_line(self.get_in_prompt()) + "\n"
        if result == "\n":
            return ""  # end of input
        self.lineno += 1
        return result

    def empty(self):
        return False


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
    shell: TerminalShell, full_form: bool, strict_wl_output: bool
):
    """
    A read eval/loop for an interactive session.
    `shell` is a shell session
    """
    while True:
        try:
            evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))
            query, source_code = evaluation.parse_feeder_returning_code(shell)
            if mathics_core.PRE_EVALUATION_HOOK is not None:
                mathics_core.PRE_EVALUATION_HOOK(query, evaluation)

            show_echo(source_code, evaluation)
            if len(source_code) and source_code[0] == "!":
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
            print("\n\nGoodbye!\n")
            # raise to pass the error code on, e.g. Quit[1]
            raise
        finally:
            shell.reset_lineno()


def main() -> int:
    """
    Command-line entry.

    Return exit code we want to give status of
    """
    exit_rc = 0
    argparser = argparse.ArgumentParser(
        prog="mathics",
        usage="%(prog)s [options] [FILE]",
        add_help=False,
        description="A simple command-line interface to Mathics",
        epilog="""For a more extensive command-line interface see "mathicsscript".
Please contribute to Mathics!""",
    )

    argparser.add_argument(
        "FILE",
        nargs="?",
        type=argparse.FileType("r"),
        help="execute commands from FILE",
    )

    argparser.add_argument(
        "--help", "-h", help="show this help message and exit", action="help"
    )

    argparser.add_argument(
        "--full-form",
        "-F",
        help="Show how input was parsed to FullForm",
        action="store_true",
    )

    # --initfile is different from the combination FILE --persist since the first one
    # leaves the history empty and sets the current $Line to 1.
    argparser.add_argument(
        "--initfile",
        help="the same that FILE and --persist together",
        type=argparse.FileType("r"),
    )

    argparser.add_argument(
        "--persist",
        help="go to interactive shell after evaluating FILE or -e",
        action="store_true",
    )

    argparser.add_argument(
        "--post-mortem",
        help="go to post-mortem debug on a terminating system exception (needs trepan3k)",
        action="store_true",
    )

    argparser.add_argument(
        "--pyextensions",
        "-l",
        action="append",
        metavar="PYEXT",
        help="directory to load extensions in python",
    )

    argparser.add_argument(
        "--quiet", "-q", help="don't print message at startup", action="store_true"
    )

    argparser.add_argument(
        "-script", help="run a mathics file in script mode", action="store_true"
    )

    argparser.add_argument(
        "--execute",
        "-e",
        action="append",
        metavar="EXPR",
        help="evaluate EXPR before processing any input files (may be given "
        "multiple times)",
    )

    # Python 3.7 does not support cProfile as a context manager
    if sys.version_info >= (3, 8):
        argparser.add_argument(
            "--cprofile",
            help="run cProfile on --execute argument",
            action="store_true",
        )

    argparser.add_argument(
        "--colors",
        nargs="?",
        help=(
            "interactive shell colors. Use value 'NoColor' or 'None' to disable "
            "ANSI color decoration"
        ),
    )

    argparser.add_argument(
        "--no-completion", help="disable tab completion", action="store_true"
    )

    argparser.add_argument(
        "--no-readline",
        help="disable line editing (implies --no-completion)",
        action="store_true",
    )

    argparser.add_argument(
        "--version", "-v", action="version", version="%(prog)s " + __version__
    )

    argparser.add_argument(
        "--strict-wl-output",
        help="Most WL-output compatible (at the expense of usability).",
        action="store_true",
    )

    argparser.add_argument(
        "--trace-builtins",
        "-T",
        help="Trace Built-in call counts and elapsed time",
        action="store_true",
    )

    argparser.add_argument(
        "--show-statistics",
        action="store_true",
        help="print cache statistics",
    )

    args, _ = argparser.parse_known_args()

    quit_command = "CTRL-BREAK" if sys.platform in ("win32", "nt") else "CONTROL-D"

    extension_modules = []
    if args.pyextensions:
        for ext in args.pyextensions:
            extension_modules.append(ext)
    else:
        from mathics.settings import default_pymathics_modules

        extension_modules = default_pymathics_modules

    if args.trace_builtins:
        FunctionApplyRule.apply_rule = traced_apply_function  # type: ignore[method-assign]

        def dump_tracing_stats():
            TraceBuiltins.dump_tracing_stats(sort_by="count", evaluation=None)

        atexit.register(dump_tracing_stats)

    if args.show_statistics:
        atexit.register(show_lru_cache_statistics)

    definitions = Definitions(
        add_builtin=True, extension_modules=tuple(extension_modules)
    )
    definitions.set_line_no(0)

    shell = TerminalShell(
        definitions,
        args.colors,
        want_readline=not (args.no_readline),
        want_completion=not (args.no_completion),
        autoload=True,
    )

    if args.initfile:
        feeder = MathicsFileLineFeeder(args.initfile)
        eval_loop(feeder, shell)
        definitions.set_line_no(0)

    if args.post_mortem:
        try:
            from trepan.post_mortem import post_mortem_excepthook
        except ImportError:
            print(
                "trepan3k is needed for post-mortem debugging --post-mortem option ignored."
            )
            print("And you may want also trepan3k-mathics3-plugin as well.")
        else:
            sys.excepthook = post_mortem_excepthook

    if args.FILE is not None:
        set_input_var(args.FILE.name)
        definitions.set_inputfile(args.FILE.name)
        feeder = MathicsFileLineFeeder(args.FILE)
        eval_loop(feeder, shell)

        if args.persist:
            definitions.set_line_no(0)
        elif not args.execute:
            return exit_rc

    if args.execute:

        def run_it():
            evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))
            return evaluation.parse_evaluate(expr, timeout=settings.TIMEOUT), evaluation

        for expr in args.execute:
            if sys.version_info >= (3, 8) and args.cprofile:
                with cProfile.Profile() as pr:
                    result, evaluation = run_it()
                    pr.print_stats()
            else:
                result, evaluation = run_it()

            shell.print_result(
                result, no_out_prompt=True, strict_wl_output=args.strict_wl_output
            )
            if evaluation.exc_result is SymbolNull:
                exit_rc = 0
            elif evaluation.exc_result is Symbol("$Aborted"):
                exit_rc = -1
            elif evaluation.exc_result is Symbol("Overflow"):
                exit_rc = -2
            else:
                exit_rc = -3

        if not args.persist:
            return exit_rc

    if not args.quiet:
        print()
        print(version_string + "\n")
        print(license_string + "\n")
        print(f"Quit by evaluating Quit[] or by pressing {quit_command}.\n")

    ensure_directory(DATA_DIR)
    ensure_directory(USER_PACKAGE_DIR)
    interactive_eval_loop(shell, args.full_form, args.strict_wl_output)
    return exit_rc


if __name__ == "__main__":
    sys.exit(main())
