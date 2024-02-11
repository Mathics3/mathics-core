#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FIXME: combine with same thing in Mathics Django
"""
Does 2 things which can either be done independently or
as a pipeline:

1. Extracts tests and runs them from static mdoc files and docstrings from Mathics
   built-in functions
2. Creates/updates internal documentation data
"""

import os
import os.path as osp
import pickle
import re
import sys
from argparse import ArgumentParser
from datetime import datetime
from typing import Dict, Optional

import mathics
from mathics import settings, version_string
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation, Output
from mathics.core.load_builtin import _builtins, import_and_load_builtins
from mathics.core.parser import MathicsSingleLineFeeder
from mathics.doc.common_doc import (
    DocGuideSection,
    DocSection,
    DocTest,
    DocTests,
    MathicsMainDocumentation,
)
from mathics.doc.utils import load_doctest_data, print_and_log
from mathics.eval.pymathics import PyMathicsLoadException, eval_LoadModule
from mathics.timing import show_lru_cache_statistics


class TestOutput(Output):
    def max_stored_size(self, _):
        return None


# Global variables

# FIXME: After 3.8 is the minimum Python we can turn "str" into a Literal
SEP: str = "-" * 70 + "\n"
STARS: str = "*" * 10

DEFINITIONS = None
DOCUMENTATION = None
CHECK_PARTIAL_ELAPSED_TIME = False
LOGFILE = None

MAX_TESTS = 100000  # A number greater than the total number of tests.


def doctest_compare(result: Optional[str], wanted: Optional[str]) -> bool:
    """
    Performs a doctest comparison between ``result`` and ``wanted`` and returns
    True if the test should be considered a success.
    """
    if wanted in ("...", result):
        return True

    if result is None or wanted is None:
        return False
    result_list = result.splitlines()
    wanted_list = wanted.splitlines()
    if result_list == [] and wanted_list == ["#<--#"]:
        return True

    if len(result_list) != len(wanted_list):
        return False

    for res, want in zip(result_list, wanted_list):
        wanted_re = re.escape(want.strip())
        wanted_re = wanted_re.replace("\\.\\.\\.", ".*?")
        wanted_re = f"^{wanted_re}$"
        if not re.match(wanted_re, res.strip()):
            return False
    return True


def test_case(
    test: DocTest,
    index: int = 0,
    subindex: int = 0,
    quiet: bool = False,
    section_name: str = "",
    section_for_print="",
    chapter_name: str = "",
    part: str = "",
) -> bool:
    """
    Run a single test cases ``test``. Return True if test succeeds and False if it
    fails. ``index``gives the global test number count, while ``subindex`` counts
    from the beginning of the section or subsection.

    The test results are assumed to be foramtted to ASCII text.
    """
    assert isinstance(index, int)
    assert isinstance(subindex, int)
    global CHECK_PARTIAL_ELAPSED_TIME
    test_str, wanted_out, wanted = test.test, test.outs, test.result

    def fail(why):
        print_and_log(
            LOGFILE,
            f"""{SEP}Test failed: in {part} / {chapter_name} / {section_name}
{part}
{why}
""".encode(
                "utf-8"
            ),
        )
        return False

    if not quiet:
        if section_for_print:
            print(f"{STARS} {section_for_print} {STARS}")
        print(f"{index:4d} ({subindex:2d}): TEST {test_str}")

    feeder = MathicsSingleLineFeeder(test_str, filename="<test>")
    evaluation = Evaluation(
        DEFINITIONS, catch_interrupt=False, output=TestOutput(), format="text"
    )
    try:
        time_parsing = datetime.now()
        query = evaluation.parse_feeder(feeder)
        if CHECK_PARTIAL_ELAPSED_TIME:
            print("   parsing took", datetime.now() - time_parsing)
        if query is None:
            # parsed expression is None
            result = None
            out = evaluation.out
        else:
            result = evaluation.evaluate(query)
            if CHECK_PARTIAL_ELAPSED_TIME:
                print("   evaluation took", datetime.now() - time_parsing)
            out = result.out
            result = result.result
    except Exception as exc:
        fail(f"Exception {exc}")
        info = sys.exc_info()
        sys.excepthook(*info)
        return False

    time_comparing = datetime.now()
    comparison_result = doctest_compare(result, wanted)

    if CHECK_PARTIAL_ELAPSED_TIME:
        print("   comparison took ", datetime.now() - time_comparing)
    if not comparison_result:
        print("result != wanted")
        fail_msg = f"Result: {result}\nWanted: {wanted}"
        if out:
            fail_msg += "\nAdditional output:\n"
            fail_msg += "\n".join(str(o) for o in out)
        return fail(fail_msg)
    output_ok = True
    time_comparing = datetime.now()
    if len(wanted_out) == 1 and wanted_out[0].text == "...":
        # If we have ... don't check
        pass
    elif len(out) != len(wanted_out):
        # Mismatched number of output lines, and we don't have "..."
        output_ok = False
    else:
        # Need to check all output line by line
        for got, wanted in zip(out, wanted_out):
            if not got == wanted and wanted.text != "...":
                output_ok = False
                break
    if CHECK_PARTIAL_ELAPSED_TIME:
        print("   comparing messages took ", datetime.now() - time_comparing)
    if not output_ok:
        return fail(
            "Output:\n%s\nWanted:\n%s"
            % ("\n".join(str(o) for o in out), "\n".join(str(o) for o in wanted_out))
        )
    return True


def create_output(tests, doctest_data, output_format="latex"):
    """
    Populate ``doctest_data`` with the results of the
    ``tests`` in the format ``output_format``
    """
    if DEFINITIONS is None:
        print_and_log(LOGFILE, "Definitions are not initialized.")
        return

    DEFINITIONS.reset_user_definitions()

    for test in tests.tests:
        if test.private:
            continue
        key = test.key
        evaluation = Evaluation(
            DEFINITIONS, format=output_format, catch_interrupt=True, output=TestOutput()
        )
        try:
            result = evaluation.parse_evaluate(test.test)
        except Exception:  # noqa
            result = None
        if result is None:
            result = []
        else:
            result_data = result.get_data()
            result_data["form"] = output_format
            result = [result_data]

        doctest_data[key] = {
            "query": test.test,
            "results": result,
        }


def show_test_summary(
    total: int,
    failed: int,
    entity_name: str,
    entities_searched: str,
    keep_going: bool,
    generate_output: bool,
    output_data,
):
    """
    Print and log test summary results.

    If ``generate_output`` is True, we will also generate output data
    to ``output_data``.
    """

    print()
    if total == 0:
        print_and_log(
            LOGFILE, f"No {entity_name} found with a name in: {entities_searched}."
        )
        if "MATHICS_DEBUG_TEST_CREATE" not in os.environ:
            print(f"Set environment MATHICS_DEBUG_TEST_CREATE to see {entity_name}.")
    elif failed > 0:
        print(SEP)
        if not generate_output:
            print_and_log(
                LOGFILE, f"""{failed} test{'s' if failed != 1 else ''} failed."""
            )
    else:
        print_and_log(LOGFILE, "All tests passed.")

    if generate_output and (failed == 0 or keep_going):
        save_doctest_data(output_data)
    return


def test_chapters(
    include_chapters: set,
    quiet=False,
    stop_on_failure=False,
    generate_output=False,
    reload=False,
    keep_going=False,
    start_at: int = 0,
    max_tests: int = MAX_TESTS,
) -> int:
    """
    Runs a group of related tests for the set specified in ``chapters``.

    If ``quiet`` is True, the progress and results of the tests are shown.

    If ``stop_on_failure`` is true then the remaining tests in a section are skipped when a test
    fails.
    """
    failed = total = 0
    index = 0

    output_data, chapter_names = validate_group_setup(
        include_chapters, "chapters", reload
    )
    if (output_data, chapter_names) == INVALID_TEST_GROUP_SETUP:
        return total

    prev_key = []
    for tests in DOCUMENTATION.get_tests():
        if tests.chapter in include_chapters:
            for test in tests.tests:
                key = list(test.key)[1:-1]
                if prev_key != key:
                    prev_key = key
                    print(f'Testing section: {" / ".join(key)}')
                    index = 0
                if test.ignore:
                    continue
                index += 1
                total += 1
                if not test_case(test, index, quiet=quiet):
                    failed += 1
                    if stop_on_failure:
                        break
            if generate_output and failed == 0:
                create_output(tests, output_data)

    print()
    if index == 0:
        print_and_log(LOGFILE, f"No chapters found named {chapter_names}.")
    elif failed > 0:
        if not (keep_going and format == "latex"):
            print_and_log(
                LOGFILE, "%d test%s failed." % (failed, "s" if failed != 1 else "")
            )
    else:
        print_and_log(LOGFILE, "All tests passed.")

    show_test_summary(
        total,
        failed,
        "chapters",
        chapter_names,
        keep_going,
        generate_output,
        output_data,
    )
    return total


def test_sections(
    include_sections: set,
    quiet=False,
    stop_on_failure=False,
    generate_output=False,
    reload=False,
    keep_going=False,
) -> int:
    """Runs a group of related tests for the set specified in ``sections``.

    If ``quiet`` is True, the progress and results of the tests are shown.

    ``index`` has the current count. If ``stop_on_failure`` is true
    then the remaining tests in a section are skipped when a test
    fails. If ``keep_going`` is True and there is a failure, the next
    section is continued after failure occurs.
    """

    total = failed = 0
    prev_key = []

    output_data, section_names = validate_group_setup(
        include_sections, "section", reload
    )

    index = 0
    format = "latex" if generate_output else "text"
    for tests in DOCUMENTATION.get_tests():
        if tests.section in include_sections:
            for test in tests.tests:
                key = list(test.key)[1:-1]
                if prev_key != key:
                    prev_key = key
                    print(f'Testing section: {" / ".join(key)}')
                    index = 0
                if test.ignore:
                    continue
                index += 1
                total += 1
                if not test_case(test, index, quiet=quiet):
                    failed += 1
                    if stop_on_failure:
                        break
            if generate_output and (failed == 0 or keep_going):
                create_output(tests, output_data, format=format)

    print()
    if index == 0:
        print_and_log(LOGFILE, f"No sections found named {section_names}.")
    elif failed > 0:
        if not (keep_going and format == "latex"):
            print_and_log(
                LOGFILE, "%d test%s failed." % (failed, "s" if failed != 1 else "")
            )
    else:
        print_and_log(LOGFILE, "All tests passed.")
    if generate_output and (failed == 0 or keep_going):
        save_doctest_data(output_data)

    show_test_summary(
        total,
        failed,
        "sections",
        section_names,
        keep_going,
        generate_output,
        output_data,
    )
    return total


def test_all(
    quiet=False,
    generate_output=True,
    stop_on_failure=False,
    start_at=0,
    max_tests: int = MAX_TESTS,
    texdatafolder=None,
    doc_even_if_error=False,
    excludes=[],
) -> int:
    if not quiet:
        print(f"Testing {version_string}")

    if generate_output:
        if texdatafolder is None:
            texdatafolder = osp.dirname(
                settings.get_doctest_latex_data_path(
                    should_be_readable=False, create_parent=True
                )
            )
    try:
        index = 0
        total = failed = skipped = 0
        failed_symbols = set()
        output_data = {}
        for tests in DOCUMENTATION.get_tests():
            sub_total, sub_failed, sub_skipped, symbols, index = test_tests(
                tests,
                index,
                quiet=quiet,
                stop_on_failure=stop_on_failure,
                start_at=start_at,
                max_tests=max_tests,
                excludes=excludes,
            )
            if generate_output:
                create_output(tests, output_data)
            total += sub_total
            failed += sub_failed
            skipped += sub_skipped
            failed_symbols.update(symbols)
            if sub_failed and stop_on_failure:
                break
            if total >= max_tests:
                break
        builtin_total = len(_builtins)
    except KeyboardInterrupt:
        print("\nAborted.\n")
        return total

    if failed > 0:
        print(SEP)
    if max_tests == MAX_TESTS:
        print_and_log(
            LOGFILE,
            f"{total} Tests for {builtin_total} built-in symbols, {total-failed} "
            f"passed, {failed} failed, {skipped} skipped.",
        )
    else:
        print_and_log(
            LOGFILE,
            f"{total} Tests, {total - failed} passed, {failed} failed, {skipped} "
            "skipped.",
        )
    if failed_symbols:
        if stop_on_failure:
            print_and_log(
                LOGFILE, "(not all tests are accounted for due to --stop-on-failure)"
            )
        print_and_log(LOGFILE, "Failed:")
        for part, chapter, section in sorted(failed_symbols):
            print_and_log(LOGFILE, f"  - {section} in {part} / {chapter}")

    if generate_output and (failed == 0 or doc_even_if_error):
        save_doctest_data(output_data)
        return total

    if failed == 0:
        print("\nOK")
    else:
        print("\nFAILED")
        sys.exit(1)  # Travis-CI knows the tests have failed
    return total


def save_doctest_data(output_data: Dict[tuple, dict]):
    """
    Save doctest tests and test results to a Python PCL file.

    ``output_data`` is a dictionary of test results. The key is a tuple
    of:
    * Part name,
    * Chapter name,
    * [Guide Section name],
    * Section name,
    * Subsection name,
    * test number
    and the value is a dictionary of a Result.getdata() dictionary.
    """
    doctest_latex_data_path = settings.get_doctest_latex_data_path(
        should_be_readable=False, create_parent=True
    )
    print(f"Writing internal document data to {doctest_latex_data_path}")
    i = 0
    for key in output_data:
        i = i + 1
        print(key, output_data[key])
        if i > 9:
            break
    with open(doctest_latex_data_path, "wb") as output_file:
        pickle.dump(output_data, output_file, 4)


# When 3.8 is base, the below can be a Literal type.
INVALID_TEST_GROUP_SETUP = (None, None)


def validate_group_setup(
    include_set: set,
    entity_name: Optional[str],
    reload: bool,
) -> tuple:
    """
    Common things that need to be done before running a group of doctests.
    """

    if DOCUMENTATION is None:
        print_and_log(LOGFILE, "Documentation is not initialized.")
        return INVALID_TEST_GROUP_SETUP

    if entity_name is not None:
        include_names = ", ".join(include_set)
        print(f"Testing {entity_name}(s): {include_names}")
    else:
        include_names = None

    if reload:
        doctest_latex_data_path = settings.get_doctest_latex_data_path(
            should_be_readable=True
        )
        output_data = load_doctest_data(doctest_latex_data_path)
    else:
        output_data = {}

    # For consistency set the character encoding ASCII which is
    # the lowest common denominator available on all systems.
    settings.SYSTEM_CHARACTER_ENCODING = "ASCII"

    if DEFINITIONS is None:
        print_and_log(LOGFILE, "Definitions are not initialized.")
        return INVALID_TEST_GROUP_SETUP

    # Start with a clean variables state from whatever came before.
    # In the test suite however, we may set new variables.
    DEFINITIONS.reset_user_definitions()
    return output_data, include_names


def test_tests(
    tests,
    index,
    quiet=False,
    stop_on_failure=False,
    start_at=0,
    max_tests=MAX_TESTS,
    excludes=[],
):
    # For consistency set the character encoding ASCII which is
    # the lowest common denominator available on all systems.
    settings.SYSTEM_CHARACTER_ENCODING = "ASCII"
    DEFINITIONS.reset_user_definitions()
    total = failed = skipped = 0
    failed_symbols = set()
    section = tests.section
    if section in excludes:
        return total, failed, len(tests.tests), failed_symbols, index
    count = 0
    print(tests.chapter, "/", section)
    for subindex, test in enumerate(tests.tests):
        index += 1
        if test.ignore:
            continue
        if index < start_at:
            skipped += 1
            continue
        elif count >= max_tests:
            break

        total += 1
        count += 1
        if not test_case(test, index, subindex + 1, quiet, section):
            failed += 1
            failed_symbols.add((tests.part, tests.chapter, tests.section))
            if stop_on_failure:
                break

        section = None
    return total, failed, skipped, failed_symbols, index


def write_doctest_data(quiet=False, reload=False):
    """
    Get doctest information, which involves running the tests to obtain
    test results and write out both the tests and the test results.
    """
    if not quiet:
        print(f"Extracting internal doc data for {version_string}")
        print("This may take a while...")

    try:
        output_data = load_doctest_data() if reload else {}
        for tests in DOCUMENTATION.get_tests():
            create_output(tests, output_data)
    except KeyboardInterrupt:
        print("\nAborted.\n")
        return

    print("done.\n")
    save_doctest_data(output_data)


def main():
    global DEFINITIONS
    global LOGFILE
    global CHECK_PARTIAL_ELAPSED_TIME

    import_and_load_builtins()
    DEFINITIONS = Definitions(add_builtin=True)

    parser = ArgumentParser(description="Mathics test suite.", add_help=False)
    parser.add_argument(
        "--help", "-h", help="show this help message and exit", action="help"
    )
    parser.add_argument(
        "--version", "-v", action="version", version="%(prog)s " + mathics.__version__
    )
    parser.add_argument(
        "--chapters",
        "-c",
        dest="chapters",
        metavar="CHAPTER",
        help="only test CHAPTER(s). "
        "You can list multiple chapters by adding a comma (and no space) in between chapter names.",
    )
    parser.add_argument(
        "--sections",
        "-s",
        dest="sections",
        metavar="SECTION",
        help="only test SECTION(s). "
        "You can list multiple sections by adding a comma (and no space) in between section names.",
    )
    parser.add_argument(
        "--exclude",
        "-X",
        default="",
        dest="exclude",
        metavar="SECTION",
        help="exclude SECTION(s). "
        "You can list multiple sections by adding a comma (and no space) in between section names.",
    )
    parser.add_argument(
        "--logfile",
        "-f",
        dest="logfilename",
        metavar="LOGFILENAME",
        help="stores the output in [logfilename]. ",
    )
    parser.add_argument(
        "--load-module",
        "-l",
        dest="pymathics",
        metavar="MATHIC3-MODULES",
        help="load Mathics3 module MATHICS3-MODULES. "
        "You can list multiple Mathics3 Modules by adding a comma (and no space) in between "
        "module names.",
    )
    parser.add_argument(
        "--time-each",
        "-d",
        dest="elapsed_times",
        action="store_true",
        help="check the time that take each test to parse, evaluate and compare.",
    )

    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        action="store_true",
        help="generate pickled internal document data",
    )
    parser.add_argument(
        "--doc-only",
        dest="doc_only",
        action="store_true",
        help="generate pickled internal document data without running tests; Can't be used with --section or --reload.",
    )
    parser.add_argument(
        "--reload",
        "-r",
        dest="reload",
        action="store_true",
        help="reload pickled internal document data, before possibly adding to it",
    )
    parser.add_argument(
        "--quiet", "-q", dest="quiet", action="store_true", help="hide passed tests"
    )
    parser.add_argument(
        "--keep-going",
        "-k",
        dest="keep_going",
        action="store_true",
        help="create documentation even if there is a test failure",
    )
    parser.add_argument(
        "--stop-on-failure", "-x", action="store_true", help="stop on failure"
    )
    parser.add_argument(
        "--skip",
        metavar="N",
        dest="skip",
        type=int,
        default=0,
        help="skip the first N tests",
    )
    parser.add_argument(
        "--count",
        metavar="N",
        dest="count",
        type=int,
        default=MAX_TESTS,
        help="run only  N tests",
    )
    parser.add_argument(
        "--show-statistics",
        action="store_true",
        help="print cache statistics",
    )
    global LOGFILE

    args = parser.parse_args()

    if args.elapsed_times:
        CHECK_PARTIAL_ELAPSED_TIME = True
    # If a test for a specific section is called
    # just test it
    if args.logfilename:
        LOGFILE = open(args.logfilename, "wt")

    global DOCUMENTATION
    DOCUMENTATION = MathicsMainDocumentation()

    # LoadModule Mathics3 modules
    if args.pymathics:
        for module_name in args.pymathics.split(","):
            try:
                eval_LoadModule(module_name, DEFINITIONS)
            except PyMathicsLoadException:
                print(f"Python module {module_name} is not a Mathics3 module.")

            except Exception as e:
                print(f"Python import errors with: {e}.")
            else:
                print(f"Mathics3 Module {module_name} loaded")

    DOCUMENTATION.load_documentation_sources()

    start_time = None
    total = 0

    if args.sections:
        include_sections = set(sec.strip() for sec in args.sections.split(","))

        total = test_sections(
            include_sections,
            stop_on_failure=args.stop_on_failure,
            generate_output=args.output,
            reload=args.reload,
            keep_going=args.keep_going,
        )
        assert isinstance(total, int)
    elif args.chapters:
        start_time = datetime.now()
        start_at = args.skip + 1
        include_chapters = set(chap.strip() for chap in args.chapters.split(","))

        total = test_chapters(
            include_chapters,
            stop_on_failure=args.stop_on_failure,
            generate_output=args.output,
            reload=args.reload,
            start_at=start_at,
            max_tests=args.count,
        )
        assert isinstance(total, int)
    else:
        if args.doc_only:
            write_doctest_data(
                quiet=args.quiet,
                reload=args.reload,
            )
        else:
            excludes = set(args.exclude.split(","))
            start_at = args.skip + 1
            start_time = datetime.now()
            total = test_all(
                quiet=args.quiet,
                generate_output=args.output,
                stop_on_failure=args.stop_on_failure,
                start_at=start_at,
                max_tests=args.count,
                doc_even_if_error=args.keep_going,
                excludes=excludes,
            )
            assert isinstance(total, int)

    end_time = datetime.now()
    if total > 0 and start_time is not None:
        print("Tests took ", end_time - start_time)

    if LOGFILE:
        LOGFILE.close()
    if args.show_statistics:
        show_lru_cache_statistics()


if __name__ == "__main__":
    main()
