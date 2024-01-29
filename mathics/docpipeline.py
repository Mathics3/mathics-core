#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FIXME: combine with same thing in Django
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
import mathics.settings
from mathics import settings, version_string
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation, Output
from mathics.core.load_builtin import _builtins, import_and_load_builtins
from mathics.core.parser import MathicsSingleLineFeeder
from mathics.doc.common_doc import (
    DocGuideSection,
    DocTests,
    MathicsMainDocumentation,
    Tests,
)
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


MAX_TESTS = 100000  # Number than the total number of tests


def doctest_compare(result: Optional[str], wanted: Optional[str]) -> bool:
    """
    Performs a doctest comparison between ``result`` and ``wanted`` and returns
    True if the test should be considered a success.
    """
    if wanted in ("...", result):
        return True

    if result is None or wanted is None:
        return False
    result = result.splitlines()
    wanted = wanted.splitlines()
    if result == [] and wanted == ["#<--#"]:
        return True

    if len(result) != len(wanted):
        return False

    for res, want in zip(result, wanted):
        wanted_re = re.escape(want.strip())
        wanted_re = wanted_re.replace("\\.\\.\\.", ".*?")
        wanted_re = f"^{wanted_re}$"
        if not re.match(wanted_re, res.strip()):
            return False
    return True


def print_and_log(*args):
    """
    Print a message and also log it to global LOGFILE.
    """
    msg_lines = [a.decode("utf-8") if isinstance(a, bytes) else a for a in args]
    string = "".join(msg_lines)
    print(string)
    if LOGFILE is not None:
        LOGFILE.write(string)


def test_case(
    test: str,
    index: int = 0,
    subindex: int = 0,
    quiet: bool = False,
    section_name: str = "",
    section_for_print="",
    format_output="text",
    chapter_name: str = "",
    part: str = "",
) -> bool:
    """
    Run a single test cases ``test``. Return True if test succeeds and False if it
    fails. ``index``gives the global test number count, while ``subindex`` counts
    from the beginning of the section or subsection.
    """

    global CHECK_PARTIAL_ELAPSED_TIME
    test, wanted_out, wanted = test.test, test.outs, test.result

    # All the doctests reference results are in text format, so this parameter
    # format_output does not make sense in this function.
    format_output = "text"

    def fail(why):
        print_and_log(
            f"""{SEP}Test failed: in {part} / {chapter_name} / {section_name}
{part}
{why}
""".encode(
                "utf-8"
            )
        )
        return False

    if not quiet:
        if section_for_print:
            print(f"{STARS} {section_for_print} {STARS}")
        print(f"{index:4d} ({subindex:2d}): TEST {test}")

    feeder = MathicsSingleLineFeeder(test, "<test>")
    evaluation = Evaluation(
        DEFINITIONS, catch_interrupt=False, output=TestOutput(), format=format_output
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


def create_output(
    tests: Union[list, Tests], doctest_data: dict, format_output: str = "latex"
):
    """
    Populates `doctest_data` with the tests and the results of its evaluation
    in latex format.
    """
    # Check
    assert isinstance(
        tests,
        (
            list,
            Tests,
        ),
    )
    if DEFINITIONS is None:
        print_and_log("Definitions are not initialized.")
        return

    DEFINITIONS.reset_user_definitions()
    if isinstance(tests, Tests):
        tests = tests.tests
    for test in tests:
        if test.private:
            continue
        key = test.key
        evaluation = Evaluation(
            DEFINITIONS, format=format_output, catch_interrupt=True, output=TestOutput()
        )
        try:
            result = evaluation.parse_evaluate(test.test)
        except Exception:  # noqa
            result = None
        if result is None:
            result = []
        else:
            result_data = result.get_data()
            result_data["form"] = format_output
            result = [result_data]

        doctest_data[key] = {
            "query": test.test,
            "results": result,
        }


def show_test_summary(
    index: int,
    failed: int,
    entity_name: str,
    entities_searched: str,
    keep_going: bool,
    format_output: str,
    generate_output: bool,
    output_data,
):
    """
    Print and log test summary results.

    If ``generate_output`` is True, we will also generate output data
    to ``output_data``.
    """

    print()
    if index == 0:
        print_and_log(f"No {entity_name} found with a name in: {entities_searched}.")
        if "MATHICS_DEBUG_TEST_CREATE" not in os.environ:
            print(f"Set environment MATHICS_DEBUG_TEST_CREATE to see {entity_name}.")
    elif failed > 0:
        print(SEP)
        if format_output != "latex":
            print_and_log(f"""{failed} test{'s' if failed != 1 else ''} failed.""")
    else:
        print_and_log("All tests passed.")

    if generate_output and (failed == 0 or keep_going):
        save_doctest_data(output_data)
    return


def test_section_in_chapter_or_guide_section(
    section,
    total: int,
    failed: int,
    quiet,
    stop_on_failure,
    prev_key: list,
    format_output,
) -> Tuple[int, int, int, list]:
    """
    Runs a tests for section ``section`` under a chapter or guide section.
    Note that both of these contain a collection of section tests underneath.

    ``total`` and ``failed`` give running tallies on the number of tests run and
    the number of tests respectively.

    If ``quiet`` is True, the progress and results of the tests are shown.
    If ``stop_on_failure`` is true then the remaining tests in a section are skipped when a test
    fails.
    """
    index = 0
    for test in section.tests:
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

        if isinstance(test, DocTests):
            for doctest in test.tests:
                index += 1
                total += 1
                if not test_case(
                    doctest,
                    total,
                    index,
                    quiet=quiet,
                    section_name=section.title,
                    section_for_print=section_name_for_print,
                    chapter_name=doctest.chapter,
                    part=doctest.part,
                    # in the doctests, the reference output
                    # is always in  "text" form,
                    format_output="text"
                    # format_output=format_output,
                ):
                    failed += 1
                    if stop_on_failure:
                        break
        elif test.ignore:
            continue

        else:
            index += 1
            total += 1
            if not test_case(
                test,
                total,
                index,
                quiet=quiet,
                section_name=section.section,
                section_for_print=section_name_for_print,
                chapter_name=test.chapter,
                part=test.part,
                format_output=format_output,
            ):
                failed += 1
                if stop_on_failure:
                    break
                pass
            pass
        pass
    return index, total, failed, prev_key


# When 3.8 is base, the below can be a Literal type.
INVALID_TEST_GROUP_SETUP = (None, None, None)


def validate_group_setup(
    include_set: set, entity_name: Optional[str], reload: bool, generate_output: bool
) -> tuple:
    """
    Common things that need to be done before running a group of doctests.
    """

    if DOCUMENTATION is None:
        print_and_log("Documentation is not initialized.")
        return INVALID_TEST_GROUP_SETUP

    if entity_name is not None:
        include_names = ", ".join(include_set)
        print(f"Testing {entity_name}(s): {include_names}")
    else:
        include_names = None

    output_data = load_doctest_data() if reload else {}
    format_output = "latex" if generate_output else "text"

    # For consistency set the character encoding ASCII which is
    # the lowest common denominator available on all systems.
    mathics.settings.SYSTEM_CHARACTER_ENCODING = "ASCII"

    if DEFINITIONS is None:
        print_and_log("Definitions are not initialized.")
        return INVALID_TEST_GROUP_SETUP

    # Start with a clean variables state from whatever came before.
    # In the test suite however, we may set new variables.
    DEFINITIONS.reset_user_definitions()
    return output_data, format_output, include_names


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

    total = index = failed = skipped = 0
    prev_key = []
    failed_symbols = set()

    output_data, format_output, names = validate_group_setup(
        set(),
        None,
        reload,
        generate_output,
    )
    if (output_data, format_output, names) == INVALID_TEST_GROUP_SETUP:
        return total, failed, skipped, failed_symbols, index

    count = 0
    count_exceeded = False

    for chapter in DOCUMENTATION.chapters:

        # FIXME Guide sections are getting added twice somehow.
        # This is a workaround to skip testing the duplicate.
        seen_sections = set()

        for tests in chapter.get_tests():

            # Some Guide sections can return a single DocTests.

            # FIXME: decide the return tyoe of chapter.get_tests()
            test_collection = [tests] if isinstance(tests, Tests) else tests
            # In the meantime, if tests is a generator, convert it into a list.
            if not isinstance(
                test_collection,
                (
                    list,
                    Tests,
                ),
            ):
                tests = [t for t in tests]

            for section in test_collection:

                section_key = (
                    section.part,
                    section.chapter,
                    section.section,
                    section.subsection,
                )
                # See FIXME above.
                if section_key in seen_sections:
                    continue

                seen_sections.add(section_key)

                DEFINITIONS.reset_user_definitions()
                section_name = section.section
                if section_name not in excludes:
                    if isinstance(section, DocGuideSection):
                        (
                            index,
                            total,
                            failed,
                            prev_key,
                        ) = test_section_in_chapter_or_guide_section(
                            section,
                            total,
                            failed,
                            quiet,
                            stop_on_failure,
                            prev_key,
                            format_output,
                        )
                        if generate_output and failed == 0:
                            create_output(tests, output_data)
                            pass
                        pass

                    else:
                        for test in section.tests:
                            # Get key dropping off test index number
                            key = list(test.key)[1:-1]
                            if prev_key != key:
                                prev_key = key
                                section_name_for_print = " / ".join(key)
                                if quiet:
                                    print(f"Testing section: {section_name_for_print}")
                                index = 0
                            else:
                                # Null out section name, so that on the next iteration we do not print a section header.
                                section_name_for_print = ""

                            if isinstance(test, DocTests):
                                for doctest in test.tests:
                                    index += 1

                                    if index < start_at:
                                        skipped += 1
                                        continue

                                    total += 1

                                    if count >= max_tests:
                                        break
                                    count += 1

                                    if not test_case(
                                        doctest,
                                        total,
                                        index,
                                        quiet=quiet,
                                        section_name=test.section,
                                        section_for_print=section_name_for_print,
                                        chapter_name=doctest.chapter,
                                        part=doctest.part,
                                        format_output=format_output,
                                    ):
                                        failed += 1
                                        if stop_on_failure:
                                            break

                            elif test.ignore:
                                continue

                            else:
                                index += 1

                                if index < start_at:
                                    skipped += 1
                                    continue

                                total += 1
                                if count >= max_tests:
                                    break
                                count += 1

                                if not test_case(
                                    test,
                                    total,
                                    index,
                                    quiet=quiet,
                                    section_name=test.section,
                                    section_for_print=section_name_for_print,
                                    chapter_name=test.chapter,
                                    part=test.part,
                                    format_output=format_output,
                                ):
                                    failed += 1
                                    if stop_on_failure:
                                        break
                                    pass
                                pass

                        if generate_output and (failed == 0 or keep_going):
                            create_output(
                                tests, output_data, format_output=format_output
                            )
                            pass
                        pass
                    pass
                pass
            pass
        if count_exceeded:
            break
        pass

    print()
    if index == 0:
        print_and_log("No tests found.")
        if "MATHICS_DEBUG_TEST_CREATE" not in os.environ:
            print("Set environment MATHICS_DEBUG_TEST_CREATE to see structure.")
    elif failed > 0:
        print(SEP)
        if not (keep_going and format_output == "latex"):
            print_and_log(f"{failed} test%s failed." % "s" if failed != 1 else "")
    else:
        print_and_log(
            f"{total} Tests, {total - failed} passed, {failed} failed, {skipped} "
            "skipped."
        )

    if generate_output and (failed == 0 or keep_going):
        save_doctest_data(output_data)
    return total, failed, skipped, failed_symbols, index


def test_chapters(
    include_chapters: set,
    quiet=False,
    stop_on_failure=False,
    generate_output=False,
    reload=False,
    keep_going=False,
) -> int:
    """
    Runs a group of related tests for the set specified in ``chapters``.

    If ``quiet`` is True, the progress and results of the tests are shown.

    If ``stop_on_failure`` is true then the remaining tests in a section are skipped when a test
    fails.
    """
    failed = index = total = 0

    output_data, format_output, chapter_names = validate_group_setup(
        include_chapters, "chapters", reload, generate_output
    )
    if (output_data, format_output, chapter_names) == INVALID_TEST_GROUP_SETUP:
        return total

    prev_key = []
    seen_chapters = set()
    last_chapter_name = None

    for chapter in DOCUMENTATION.chapters:
        chapter_name = chapter.title

        if chapter_name not in include_chapters:
            continue

        # FIXME Guide sections are getting added twice somehow.
        # This is a workaround to skip testing the duplicate.
        seen_sections = set()

        for tests in chapter.get_tests():
            # Some Guide sections can return a single DocTests.

            test_collection = [tests] if isinstance(tests, Tests) else tests

            for section in test_collection:

                section_key = (
                    section.part,
                    section.chapter,
                    section.section,
                    section.subsection,
                )
                # See FIXME above.
                if section_key in seen_sections:
                    continue

                seen_sections.add(section_key)

                DEFINITIONS.reset_user_definitions()
                (
                    index,
                    total,
                    failed,
                    prev_key,
                ) = test_section_in_chapter_or_guide_section(
                    section,
                    total,
                    failed,
                    quiet,
                    stop_on_failure,
                    prev_key,
                    format_output,
                )
                if generate_output and failed == 0:
                    create_output(tests, output_data)
                    pass
                pass

            if last_chapter_name != chapter_name:
                if seen_chapters == include_chapters:
                    break
                if chapter_name in include_chapters:
                    seen_chapters.add(chapter_name)
                last_chapter_name = chapter_name
            pass

    show_test_summary(
        index,
        failed,
        "chapters",
        chapter_names,
        keep_going,
        format_output,
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

    total = index = failed = 0
    prev_key = []

    output_data, format_output, section_names = validate_group_setup(
        include_sections, "section", reload, generate_output
    )
    if (output_data, format_output, section_names) == INVALID_TEST_GROUP_SETUP:
        return total

    seen_sections = set()
    seen_last_section = False
    last_section_name = None
    section_name_for_finish = None

    for chapter in DOCUMENTATION.chapters:
        for tests in chapter.get_tests():

            # Some Guide sections can return a single DocTests.
            test_collection = [tests] if isinstance(tests, Tests) else tests

            for section in test_collection:
                section_name_for_finish = section_name = section.section
                if section_name in include_sections:
                    if isinstance(section, DocGuideSection):
                        (
                            index,
                            total,
                            prev_key,
                        ) = test_section_in_chapter_or_guide_section(
                            section,
                            total,
                            failed,
                            quiet,
                            stop_on_failure,
                            prev_key,
                            format_output,
                        )
                        if generate_output and failed == 0:
                            create_output(tests, output_data)
                            pass
                        pass

                    else:
                        for test in section.tests:
                            # Get key dropping off test index number
                            key = list(test.key)[1:-1]
                            if prev_key != key:
                                prev_key = key
                                section_name_for_print = " / ".join(key)
                                if not quiet:
                                    print(f"Testing section: {section_name_for_print}")
                                index = 0
                            else:
                                # Null out section name, so that on the next iteration we do not print a section header.
                                section_name_for_print = ""

                            if isinstance(test, DocTests):
                                for doctest in test.tests:
                                    index += 1
                                    total += 1
                                    if not test_case(
                                        doctest,
                                        total,
                                        index,
                                        quiet=quiet,
                                        section_name=section_name_for_print,
                                        chapter_name=doctest.chapter,
                                        part=doctest.part,
                                        format_output=format_output,
                                    ):
                                        failed += 1
                                        if stop_on_failure:
                                            break

                            elif test.ignore:
                                continue

                            else:
                                index += 1
                                total += 1
                                if not test_case(
                                    test,
                                    total,
                                    index,
                                    quiet=quiet,
                                    section_name=section_name_for_print,
                                    chapter_name=test.chapter,
                                    part=test.part,
                                    format_output=format_output,
                                ):
                                    failed += 1
                                    if stop_on_failure:
                                        break
                                    pass
                                pass

                        if generate_output and (failed == 0 or keep_going):
                            create_output(
                                tests, output_data, format_output=format_output
                            )
                            pass
                        pass

                if generate_output and (failed == 0 or keep_going):
                    create_output(tests, output_data, format=format)
                    pass
                pass
            if last_section_name != section_name_for_finish:
                if seen_sections == include_sections:
                    seen_last_section = True
                    break
                if section_name_for_finish in include_sections:
                    seen_sections.add(section_name_for_finish)
                last_section_name = section_name_for_finish
            pass

        if seen_last_section:
            break
        pass

    show_test_summary(
        index,
        failed,
        "sections",
        section_names,
        keep_going,
        format_output,
        generate_output,
        output_data,
    )
    return total


def open_ensure_dir(f, *args, **kwargs):
    try:
        return open(f, *args, **kwargs)
    except (IOError, OSError):
        d = osp.dirname(f)
        if d and not osp.exists(d):
            os.makedirs(d)
        return open(f, *args, **kwargs)


def test_all(
    quiet=False,
    generate_output=True,
    stop_on_failure=False,
    start_at=0,
    count=MAX_TESTS,
    doc_even_if_error=False,
    excludes: set = set(),
) -> int:
    if not quiet:
        print(f"Testing {version_string}")

    try:
        index = 0
        total = failed = skipped = 0
        failed_symbols = set()
        output_data = {}
        sub_total, sub_failed, sub_skipped, symbols, index = test_tests(
            index,
            quiet=quiet,
            stop_on_failure=stop_on_failure,
            start_at=start_at,
            max_tests=count,
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
    if count == MAX_TESTS:
        print_and_log(
            f"{total} Tests for {builtin_total} built-in symbols, {total-failed} "
            f"passed, {failed} failed, {skipped} skipped."
        )
    else:
        print_and_log(
            f"{total} Tests, {total - failed} passed, {failed} failed, {skipped} "
            "skipped."
        )
    if failed_symbols:
        if stop_on_failure:
            print_and_log("(not all tests are accounted for due to --stop-on-failure)")
        print_and_log("Failed:")
        for part, chapter, section in sorted(failed_symbols):
            print_and_log(f"  - {section} in {part} / {chapter}")

    if generate_output and (failed == 0 or doc_even_if_error):
        save_doctest_data(output_data)
        return total

    if failed == 0:
        print("\nOK")
    else:
        print("\nFAILED")
        sys.exit(1)  # Travis-CI knows the tests have failed
    return total


def load_doctest_data() -> Dict[tuple, dict]:
    """
    Load doctest tests and test results from Python PCL file.

    See ``save_doctest_data()`` for the format of the loaded PCL data
    (a dict).
    """
    doctest_latex_data_path = settings.get_doctest_latex_data_path(
        should_be_readable=True
    )
    print(f"Loading internal doctest data from {doctest_latex_data_path}")
    with open_ensure_dir(doctest_latex_data_path, "rb") as doctest_data_file:
        return pickle.load(doctest_data_file)


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
        for module_name in args.pymathics.split(","):
            try:
                eval_LoadModule(module_name, DEFINITIONS)
            except PyMathicsLoadException:
                print(f"Python module {module_name} is not a Mathics3 module.")

            except Exception as e:
                print(f"Python import errors with: {e}.")
            else:
                print(f"Mathics3 Module {module_name} loaded")

    DOCUMENTATION.gather_doctest_data()

    start_time = None
    total = 0

    if args.sections:
        sections = set(args.sections.split(","))

        start_time = datetime.now()
        total = test_sections(
            sections,
            stop_on_failure=args.stop_on_failure,
            generate_output=args.output,
            reload=args.reload,
            keep_going=args.keep_going,
        )
    elif args.chapters:
        start_time = datetime.now()
        chapters = set(args.chapters.split(","))

        total = test_chapters(
            chapters, stop_on_failure=args.stop_on_failure, reload=args.reload
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
                count=args.count,
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
