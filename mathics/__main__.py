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
import os.path as osp
import sys
from typing import Optional

from mathics import __version__, license_string, settings, version_string
from mathics.builtin.tuning_debug.trace import TraceBuiltins, traced_apply_function
from mathics.core.definitions import Definitions, Symbol
from mathics.core.evaluation import Evaluation
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.parser import MathicsFileLineFeeder
from mathics.core.rules import FunctionApplyRule
from mathics.core.symbols import SymbolNull
from mathics.eval.files_io.files import set_input_var
from mathics.repl import TerminalOutput, TerminalShell, eval_loop, interactive_eval_loop
from mathics.settings import DATA_DIR, USER_PACKAGE_DIR, ensure_directory
from mathics.timing import show_lru_cache_statistics

# from mathics.timing import TimeitContextManager
# with TimeitContextManager("import_and_load_builtins()"):
#     import_and_load_builtins()

import_and_load_builtins()


class VersionAction(argparse.Action):
    def __init__(self, option_strings, version=Optional[str], **kwargs):
        super().__init__(option_strings=option_strings, nargs=0, **kwargs)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        print(version_string)
        parser.exit()


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
        "-f",
        "-file",
        "--file",
        nargs="?",
        metavar="PATH",
        type=argparse.FileType("r"),
        help="execute commands from PATH",
    )

    argparser.add_argument(
        "--help", "-help", "-h", help="show this help message and exit", action="help"
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
        "--code",
        "-code",
        "-c",
        action="append",
        metavar="TEXT",
        help="evaluate TEXT before processing any input files (may be given "
        "multiple times)",
    )

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
        "--version",
        "-v",
        action=VersionAction,
        version="%(prog)s " + __version__,
        help="show program's version number and version of important software used, and exit",
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

    if args.file is not None:
        set_input_var(args.file.name)
        definitions.set_inputfile(args.file.name)
        feeder = MathicsFileLineFeeder(args.file)
        eval_loop(feeder, shell)

        if args.persist:
            definitions.set_line_no(0)
        elif not args.code:
            return exit_rc

    if args.code:

        def run_it():
            evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))
            return evaluation.parse_evaluate(expr, timeout=settings.TIMEOUT), evaluation

        for expr in args.code:
            if args.cprofile:
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
