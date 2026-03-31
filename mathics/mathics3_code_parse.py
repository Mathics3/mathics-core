"""
A command-line routine to see how Mathics3 parser parses text.
This is analogous (but not exactly the same as) the CodeParse[]
function in the WMA CoderParser package.
"""

import argparse
import sys

from mathics_scanner.feed import FileLineFeeder
from mathics_scanner.tokeniser import Tokeniser
from mathics_scanner.version import __version__

from mathics.__main__ import TerminalOutput, TerminalShell
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.parser import MathicsFileLineFeeder


def parser_loop(feeder: MathicsFileLineFeeder):
    """
    A read eval/loop for things having file input `feeder`.
    """
    while not feeder.empty():
        tokeniser = Tokeniser(feeder)
        print(f"Line: {feeder.lineno}:")
        while True:
            token = tokeniser.next()
            if token.tag == "END":
                break
            else:
                print("  ", token)


def interactive_eval_loop(shell: TerminalShell):
    """
    A read eval/loop for an interactive session.
    `shell` is a shell session
    """
    while True:
        try:
            evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))
            query, source_code = evaluation.parse_feeder_returning_code(shell)
            print(query)
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


def main():
    argparser = argparse.ArgumentParser(
        prog="mathics3-code-parse",
        usage="%(prog)s [options] [FILE]",
        add_help=False,
        description="A command-line utility to show how Mathics3 parses. Similar to CodeParser`Codeparse",
    )

    argparser.add_argument(
        "FILE",
        nargs="?",
        type=argparse.FileType("r"),
        help="parse tokens from FILE",
    )

    argparser.add_argument(
        "--help", "-h", help="show this help message and exit", action="help"
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
        "--post-mortem",
        help="go to post-mortem debug on a terminating system exception (needs trepan3k)",
        action="store_true",
    )

    argparser.add_argument(
        "--quiet", "-q", help="don't print message at startup", action="store_true"
    )

    argparser.add_argument(
        "--no-readline",
        help="disable line editing",
        action="store_true",
    )

    argparser.add_argument(
        "--version", "-v", action="version", version="%(prog)s " + __version__
    )

    args, _ = argparser.parse_known_args()

    definitions = Definitions(add_builtin=False, extension_modules=tuple())
    definitions.set_line_no(0)
    shell = TerminalShell(
        definitions,
        args.colors,
        want_readline=not (args.no_readline),
        want_completion=not (args.no_completion),
        autoload=False,
    )

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
        feeder = FileLineFeeder(args.FILE)
        parser_loop(feeder, shell)

    else:
        interactive_eval_loop(shell)


if __name__ == "__main__":
    sys.exit(main())
