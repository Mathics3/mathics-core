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
from typing import Dict, Optional, Set, Tuple, Union

import mathics
from mathics import settings, version_string
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation, Output
from mathics.core.load_builtin import _builtins, import_and_load_builtins
from mathics.core.parser import MathicsSingleLineFeeder
from mathics.doc.common_doc import DocGuideSection, DocSection, MathicsMainDocumentation
from mathics.doc.doc_entries import DocTest, DocTests
from mathics.doc.utils import load_doctest_data, print_and_log, slugify
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

    for test in tests:
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


def load_pymathics_modules(module_names: set):
    """
    Load pymathics modules

    PARAMETERS
    ==========

    module_names: set
         a set of modules to be loaded.

    Return
    ======
    loaded_modules : set
        the set of successfully loaded modules.
    """
    loaded_modules = []
    for module_name in module_names:
        try:
            eval_LoadModule(module_name, DEFINITIONS)
        except PyMathicsLoadException:
            print(f"Python module {module_name} is not a Mathics3 module.")

        except Exception as e:
            print(f"Python import errors with: {e}.")
        else:
            print(f"Mathics3 Module {module_name} loaded")
            loaded_modules.append(module_name)

    return set(loaded_modules)


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


#
#  TODO: Split and simplify this section
#
#
def test_section_in_chapter(
    section: Union[DocSection, DocGuideSection],
    total: int,
    failed: int,
    quiet,
    stop_on_failure,
    prev_key: list,
    include_sections: Optional[Set[str]] = None,
    start_at: int = 0,
    skipped: int = 0,
    max_tests: int = MAX_TESTS,
) -> Tuple[int, int, list, set]:
    """
    Runs a tests for section ``section`` under a chapter or guide section.
    Note that both of these contain a collection of section tests underneath.

    ``total`` and ``failed`` give running tallies on the number of tests run and
    the number of tests respectively.

    If ``quiet`` is True, the progress and results of the tests are shown.
    If ``stop_on_failure`` is true then the remaining tests in a section are skipped when a test
    fails.
    """
    failed_sections = set()
    section_name = section.title

    # Start out assuming all subsections will be tested
    include_subsections = None

    if include_sections is not None and section_name not in include_sections:
        # use include_section to filter subsections
        include_subsections = include_sections

    chapter = section.chapter
    chapter_name = chapter.title
    part_name = chapter.part.title
    index = 0
    if len(section.subsections) > 0:
        subsections = section.subsections
    else:
        subsections = [section]

    if chapter.doc:
        subsections = [chapter.doc] + subsections

    for subsection in subsections:
        if (
            include_subsections is not None
            and subsection.title not in include_subsections
        ):
            continue

        DEFINITIONS.reset_user_definitions()
        for test in subsection.get_tests():
            # Get key dropping off test index number
            key = list(test.key)[1:-1]
            if prev_key != key:
                prev_key = key
                section_name_for_print = " / ".join(key)
                if quiet:
                    # We don't print with stars inside in test_case(), so print here.
                    print(f"Testing section: {section_name_for_print}")
                index = 0
            else:
                # Null out section name, so that on the next iteration we do not print a section header
                # in test_case().
                section_name_for_print = ""

            tests = test.tests if isinstance(test, DocTests) else [test]

            for doctest in tests:
                if doctest.ignore:
                    continue

                index += 1
                total += 1
                if index < start_at:
                    skipped += 1
                    continue

                if not test_case(
                    doctest,
                    total,
                    index,
                    quiet=quiet,
                    section_name=section_name,
                    section_for_print=section_name_for_print,
                    chapter_name=chapter_name,
                    part=part_name,
                ):
                    failed += 1
                    failed_sections.add(
                        (
                            part_name,
                            chapter_name,
                            key[-1],
                        )
                    )
                    if stop_on_failure:
                        return total, failed, prev_key, failed_sections

    return total, failed, prev_key, failed_sections


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
    index: int,
    quiet: bool = False,
    stop_on_failure: bool = False,
    start_at: int = 0,
    max_tests: int = MAX_TESTS,
    excludes: Set[str] = set(),
    generate_output: bool = False,
    reload: bool = False,
    keep_going: bool = False,
) -> Tuple[int, int, int, set, int]:
    """
    Runs a group of related tests, ``Tests`` provided that the section is not listed in ``excludes`` and
    the global test count given in ``index`` is not before ``start_at``.

    Tests are from a section or subsection (when the section is a guide section),

    If ``quiet`` is True, the progress and results of the tests are shown.

    ``index`` has the current count. We will stop on the first failure if ``stop_on_failure`` is true.

    """

    total = failed = skipped = 0
    prev_key = []
    failed_symbols = set()

    # For consistency set the character encoding ASCII which is
    # the lowest common denominator available on all systems.
    settings.SYSTEM_CHARACTER_ENCODING = "ASCII"
    DEFINITIONS.reset_user_definitions()

    output_data, names = validate_group_setup(
        set(),
        None,
        reload,
    )
    if (output_data, names) == INVALID_TEST_GROUP_SETUP:
        return total, failed, skipped, failed_symbols, index

    def show_and_return():
        """Show the resume and build the tuple to return"""
        show_test_summary(
            total,
            failed,
            "chapters",
            names,
            keep_going,
            generate_output,
            output_data,
        )

        if generate_output and (failed == 0 or keep_going):
            save_doctest_data(output_data)

        return total, failed, skipped, failed_symbols, index

    # Loop over the whole documentation.
    for part in DOCUMENTATION.parts:
        for chapter in part.chapters:
            for section in chapter.all_sections:
                section_name = section.title
                if section_name in excludes:
                    continue

                if total >= max_tests:
                    return show_and_return()
                (total, failed, prev_key, new_failed_symbols) = test_section_in_chapter(
                    section,
                    total,
                    failed,
                    quiet,
                    stop_on_failure,
                    prev_key,
                    start_at=start_at,
                    max_tests=max_tests,
                )
                if failed:
                    failed_symbols.update(new_failed_symbols)
                    if stop_on_failure:
                        return show_and_return()
                else:
                    if generate_output:
                        create_output(section.doc.get_tests(), output_data)

    return show_and_return()

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
    failed_symbols = set()

    output_data, chapter_names = validate_group_setup(
        include_chapters, "chapters", reload
    )
    if (output_data, chapter_names) == INVALID_TEST_GROUP_SETUP:
        return total

    prev_key = []
    seen_chapters = set()

    def show_and_return():
        """Show the resume and return"""
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

    for chapter_name in include_chapters:
        chapter_slug = slugify(chapter_name)
        for part in DOCUMENTATION.parts:
            chapter = part.chapters_by_slug.get(chapter_slug, None)
            if chapter is None:
                continue
            for section in chapter.all_sections:
                (
                    total,
                    failed,
                    prev_key,
                    failed_symbols,
                ) = test_section_in_chapter(
                    section,
                    total,
                    failed,
                    quiet,
                    stop_on_failure,
                    prev_key,
                    start_at=start_at,
                    max_tests=max_tests,
                )
                if generate_output and failed == 0:
                    create_output(section.doc.get_tests(), output_data)
                    pass
                pass

    return show_and_return()


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
    if (output_data, section_names) == INVALID_TEST_GROUP_SETUP:
        return total

    seen_sections = set()
    seen_last_section = False
    last_section_name = None
    section_name_for_finish = None
    prev_key = []

    def show_and_return():
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

    for part in DOCUMENTATION.parts:
        for chapter in part.chapters:
            for section in chapter.all_sections:
                (
                    total,
                    failed,
                    prev_key,
                    failed_symbols,
                ) = test_section_in_chapter(
                    section=section,
                    total=total,
                    quiet=quiet,
                    failed=failed,
                    stop_on_failure=stop_on_failure,
                    prev_key=prev_key,
                    include_sections=include_sections,
                )

                if generate_output and failed == 0:
                    create_output(section.doc.get_tests(), output_data)

                if last_section_name != section_name_for_finish:
                    if seen_sections == include_sections:
                        seen_last_section = True
                        break
                    if section_name_for_finish in include_sections:
                        seen_sections.add(section_name_for_finish)
                    last_section_name = section_name_for_finish

                if seen_last_section:
                    return show_and_return()

    return show_and_return()


def test_all(
    quiet=False,
    generate_output=True,
    stop_on_failure=False,
    start_at=0,
    max_tests: int = MAX_TESTS,
    texdatafolder=None,
    doc_even_if_error=False,
    excludes: set = set(),
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

    total = failed = skipped = 0
    try:
        index = 0
        failed_symbols = set()
        output_data = {}
        sub_total, sub_failed, sub_skipped, symbols, index = test_tests(
            index,
            quiet=quiet,
            stop_on_failure=stop_on_failure,
            start_at=start_at,
            max_tests=max_tests,
            excludes=excludes,
            generate_output=generate_output,
            reload=False,
            keep_going=not stop_on_failure,
        )

        total += sub_total
        failed += sub_failed
        skipped += sub_skipped
        failed_symbols.update(symbols)
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
        required_modules = set(args.pymathics.split(","))
        load_pymathics_modules(required_modules)

    DOCUMENTATION.load_documentation_sources()

    start_time = None
    total = 0

    if args.sections:
        include_sections = set(args.sections.split(","))

        start_time = datetime.now()
        total = test_sections(
            include_sections,
            stop_on_failure=args.stop_on_failure,
            generate_output=args.output,
            reload=args.reload,
            keep_going=args.keep_going,
        )
    elif args.chapters:
        start_time = datetime.now()
        start_at = args.skip + 1
        include_chapters = set(args.chapters.split(","))

        total = test_chapters(
            include_chapters,
            stop_on_failure=args.stop_on_failure,
            generate_output=args.output,
            reload=args.reload,
            start_at=start_at,
            max_tests=args.count,
        )
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
            pass
        pass

    if total > 0 and start_time is not None:
        end_time = datetime.now()
        print("Test evalation took ", end_time - start_time)

    if LOGFILE:
        LOGFILE.close()
    if args.show_statistics:
        show_lru_cache_statistics()


if __name__ == "__main__":
    main()
