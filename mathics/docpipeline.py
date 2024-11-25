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
import sys
from argparse import ArgumentParser
from collections import namedtuple
from datetime import datetime
from typing import Callable, Dict, Generator, List, Optional, Set, Union

import mathics
from mathics import settings, version_string
from mathics.core.evaluation import Output
from mathics.core.load_builtin import _builtins, import_and_load_builtins
from mathics.doc.doc_entries import DocTest, DocumentationEntry
from mathics.doc.structure import (
    DocGuideSection,
    DocSection,
    DocSubsection,
    MathicsMainDocumentation,
)
from mathics.doc.utils import load_doctest_data, print_and_log, slugify
from mathics.eval.pymathics import PyMathicsLoadException, eval_LoadModule
from mathics.session import MathicsSession
from mathics.settings import get_doctest_latex_data_path
from mathics.timing import show_lru_cache_statistics

# Global variables

# FIXME: After 3.8 is the minimum Python we can turn "str" into a Literal
SEP: str = "-" * 70 + "\n"
STARS: str = "*" * 10
MAX_TESTS = 100000  # A number greater than the total number of tests.
# When 3.8 is base, the below can be a Literal type.
INVALID_TEST_GROUP_SETUP = (None, None)

TestParameters = namedtuple(
    "TestParameters",
    [
        "check_partial_elapsed_time",
        "data_path",
        "keep_going",
        "max_tests",
        "quiet",
        "output_format",
        "reload",
        "start_at",
    ],
)


# Dummy breakpoint for doctests
def dummy_breakpoint():
    print("Dummy breakpoint() reached! Returning.")


class TestOutput(Output):
    """Output class for tests"""

    def max_stored_size(self, _):
        return None


class DocTestPipeline:
    """
    This class gathers all the information required to process
    the doctests and generate the data for the documentation.
    """

    def __init__(self, args, output_format="latex", data_path: Optional[str] = None):
        self.session = MathicsSession()
        self.output_data: Dict[tuple, dict] = {}

        # LoadModule Mathics3 modules
        if args.pymathics:
            required_modules = set(args.pymathics.split(","))
            load_pymathics_modules(required_modules, self.session.definitions)

        self.builtin_total = len(_builtins)
        self.documentation = MathicsMainDocumentation()
        self.documentation.load_documentation_sources()
        self.logfile = open(args.logfilename, "wt") if args.logfilename else None

        self.parameters = TestParameters(
            check_partial_elapsed_time=args.elapsed_times,
            data_path=data_path,
            keep_going=args.keep_going and not args.stop_on_failure,
            max_tests=args.count + args.skip,
            quiet=args.quiet,
            output_format=output_format,
            reload=args.reload and not (args.chapters or args.sections),
            start_at=args.skip + 1,
        )
        self.status = TestStatus(data_path, self.parameters.quiet)

    def reset_user_definitions(self):
        """Reset the user definitions"""
        return self.session.definitions.reset_user_definitions()

    def print_and_log(self, message):
        """Print and log a message in the logfile"""
        if self.logfile:
            print_and_log(self.logfile, message.encode("utf-8"))
        elif not self.parameters.quiet:
            print(message)

    def validate_group_setup(
        self,
        include_set: set,
        entity_name: Optional[str],
    ):
        """
        Common things that need to be done before running a group of doctests.
        """
        test_parameters = self.parameters

        if self.documentation is None:
            self.print_and_log("Documentation is not initialized.")
            return INVALID_TEST_GROUP_SETUP

        if entity_name is not None:
            include_names = ", ".join(include_set)
            self.print_and_log(f"Testing {entity_name}(s): {include_names}")
        else:
            include_names = None

        if test_parameters.reload:
            doctest_latex_data_path = get_doctest_latex_data_path(
                should_be_readable=True
            )
            self.output_data = load_doctest_data(doctest_latex_data_path)
        else:
            self.output_data = {}

        # For consistency set the character encoding ASCII which is
        # the lowest common denominator available on all systems.
        settings.SYSTEM_CHARACTER_ENCODING = "ASCII"

        if self.session.definitions is None:
            self.print_and_log("Definitions are not initialized.")
            return INVALID_TEST_GROUP_SETUP

        # Start with a clean variables state from whatever came before.
        # In the test suite however, we may set new variables.
        self.reset_user_definitions()
        return self.output_data, include_names


class TestStatus:
    """
    Status parameters of the tests
    """

    def __init__(self, data_path: Optional[str] = None, quiet: Optional[bool] = False):
        self.texdatafolder = osp.dirname(data_path) if data_path is not None else None
        self.total = 0
        self.failed = 0
        self.skipped = 0
        self.failed_sections: Set[str] = set()
        self.prev_key: list = []
        self.quiet = quiet

    def mark_as_failed(self, key: str):
        """Mark a key as failed"""
        self.failed_sections.add(key)
        self.failed += 1

    def section_name_for_print(self, test: DocTest) -> str:
        """
        If the test has a different key,
        returns a printable version of the section name.
        Otherwise, return the empty string.
        """
        key = list(test.key)[1:-1]
        if key != self.prev_key:
            return " / ".join(key)
        return ""

    def show_section(self, test: DocTest):
        """Show information about the current test case"""
        section_name_for_print = self.section_name_for_print(test)
        if section_name_for_print:
            if self.quiet:
                print(f"Testing section: {section_name_for_print}")
            else:
                print(f"{STARS} {section_name_for_print} {STARS}")

    def show_test(self, test: DocTest, index: int, subindex: int):
        """Show the current test"""
        test_str = test.test
        if not self.quiet:
            print(f"{index:4d} ({subindex:2d}): TEST {test_str}")


def test_case(
    test: DocTest,
    test_pipeline: DocTestPipeline,
    fail: Callable,
) -> bool:
    """
    Run a single test cases ``test``. Return True if test succeeds and False if it
    fails. ``index``gives the global test number count, while ``subindex`` counts
    from the beginning of the section or subsection.

    The test results are assumed to be formatted to ASCII text.
    """
    test_parameters = test_pipeline.parameters
    try:
        time_start = datetime.now()
        result = test_pipeline.session.evaluate_as_in_cli(test.test, src_name="<test>")
        out = result.out
        result = result.result
    except Exception as exc:
        fail(f"Exception {exc}")
        info = sys.exc_info()
        sys.excepthook(*info)
        return False

    time_start = datetime.now()
    comparison_result = test.compare_result(result)

    if test_parameters.check_partial_elapsed_time:
        test_pipeline.print_and_log(
            f"   comparison took {datetime.now() - time_start} seconds"
        )
    if not comparison_result:
        print("result != wanted")
        fail_msg = f"Result: {result}\nWanted: {test.result}"
        if out:
            fail_msg += "\nAdditional output:\n"
            fail_msg += "\n".join(str(o) for o in out)
        return fail(fail_msg)

    time_start = datetime.now()
    output_ok = test.compare_out(out)
    if test_parameters.check_partial_elapsed_time:
        test_pipeline.print_and_log(
            f"   comparing messages took {datetime.now() - time_start} seconds"
        )
    if not output_ok:
        return fail(
            "Output:\n%s\nWanted:\n%s"
            % (
                "\n".join(str(o) for o in out),
                "\n".join(str(o) for o in test.outs),
            )
        )
    return True


def create_output(test_pipeline, tests):
    """
    Populate ``doctest_data`` with the results of the
    ``tests`` in the format ``output_format``
    """
    output_format = test_pipeline.parameters.output_format
    if test_pipeline.session.definitions is None:
        test_pipeline.print_and_log("Definitions are not initialized.")
        return

    doctest_data = test_pipeline.output_data
    test_pipeline.reset_user_definitions()
    session = test_pipeline.session

    for test in tests:
        if test.private:
            continue
        key = test.key
        try:
            result = session.evaluate_as_in_cli(test.test, form=output_format)
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


def load_pymathics_modules(module_names: set, definitions):
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
            eval_LoadModule(module_name, definitions)
        except PyMathicsLoadException:
            print(f"Python module {module_name} is not a Mathics3 module.")

        except Exception as exc:
            print(f"Python import errors with: {exc}.")
        else:
            print(f"Mathics3 Module {module_name} loaded")
            loaded_modules.append(module_name)

    return set(loaded_modules)


def show_test_summary(
    test_pipeline: DocTestPipeline,
    entity_name: str,
    entities_searched: str,
):
    """
    Print and log test summary results.

    If ``data_path`` is not ``None``, we will also generate output data
    to ``output_data``.
    """
    test_parameters: TestParameters = test_pipeline.parameters
    test_status: TestStatus = test_pipeline.status

    failed = test_status.failed
    print()
    if test_status.total == 0:
        test_pipeline.print_and_log(
            f"No {entity_name} found with a name in: {entities_searched}.",
        )
        if "MATHICS_DEBUG_TEST_CREATE" not in os.environ:
            test_pipeline.print_and_log(
                f"Set environment MATHICS_DEBUG_TEST_CREATE to see {entity_name}."
            )
    elif failed > 0:
        test_pipeline.print_and_log(SEP)
        if test_pipeline.parameters.data_path is None:
            test_pipeline.print_and_log(
                f"""{failed} test{'s' if failed != 1 else ''} failed.""",
            )
    else:
        test_pipeline.print_and_log("All tests passed.")

    if test_parameters.data_path and (failed == 0 or test_parameters.keep_going):
        save_doctest_data(test_pipeline)


def section_tests_iterator(
    section: DocSection,
    test_pipeline: DocTestPipeline,
    include_subsections: Optional[Set[str]] = None,
    exclude_sections: Optional[Set[str]] = None,
) -> Generator[DocTest, None, None]:
    """
    Iterator over tests in a section.
    A section contains tests in its documentation entry,
    in the head of the chapter and in its subsections.
    This function is a generator of all these tests.

    Before yielding a test from a documentation entry,
    the user definitions are reset.
    """
    chapter = section.chapter
    subsections: List[Union[DocumentationEntry, DocSection, DocSubsection]] = [section]
    if chapter.doc:
        subsections = [chapter.doc] + subsections
    if section.subsections:
        subsections.extend(section.subsections)

    for subsection in subsections:
        if (
            include_subsections is not None
            and subsection.title not in include_subsections
        ):
            continue
        if exclude_sections and subsection.title in exclude_sections:
            continue
        test_pipeline.reset_user_definitions()

        for test in subsection.get_tests():
            yield test


def test_section_in_chapter(
    test_pipeline: DocTestPipeline,
    section: Union[DocSection, DocGuideSection],
    include_sections: Optional[Set[str]] = None,
    exclude_sections: Optional[Set[str]] = None,
):
    """
    Runs a tests for section ``section`` under a chapter or guide section.
    Note that both of these contain a collection of section tests underneath.
    """
    test_parameters: TestParameters = test_pipeline.parameters
    test_status: TestStatus = test_pipeline.status

    # Start out assuming all subsections will be tested
    include_subsections = None
    if include_sections is not None and section.title not in include_sections:
        # use include_section to filter subsections
        include_subsections = include_sections

    chapter = section.chapter
    index = 0
    subsections: List[Union[DocumentationEntry, DocSection, DocSubsection]] = [section]
    if chapter.doc:
        subsections = [chapter.doc] + subsections
    if section.subsections:
        subsections.extend(section.subsections)

    section_name_for_print = ""
    for doctest in section_tests_iterator(
        section, test_pipeline, include_subsections, exclude_sections
    ):
        if doctest.ignore:
            continue
        section_name_for_print = test_status.section_name_for_print(doctest)
        test_status.show_section(doctest)
        key = list(doctest.key)[1:-1]
        if key != test_status.prev_key:
            index = 1
        else:
            index += 1
        test_status.prev_key = key
        test_status.total += 1
        if test_status.total > test_parameters.max_tests:
            return
        if test_status.total < test_parameters.start_at:
            test_status.skipped += 1
            continue

        def fail_message(why):
            test_pipeline.print_and_log(
                (f"""{SEP}Test failed: in {section_name_for_print}\n""" f"""{why}"""),
            )
            return False

        test_status.show_test(doctest, test_status.total, index)

        success = test_case(
            doctest,
            test_pipeline,
            fail=fail_message,
        )
        if not success:
            test_status.mark_as_failed(doctest.key[:-1])
            if not test_pipeline.parameters.keep_going:
                return

    return


def test_tests(
    test_pipeline: DocTestPipeline,
    excludes: Optional[Set[str]] = None,
):
    """
    Runs a group of related tests, ``Tests`` provided that the section is not
    listed in ``excludes`` and the global test count given in ``index`` is not
    before ``start_at``.

    Tests are from a section or subsection (when the section is a guide
    section). If ``quiet`` is True, the progress and results of the tests
    are shown.

    ``index`` has the current count. We will stop on the first failure
    if ``keep_going`` is false.

    """
    test_status: TestStatus = test_pipeline.status
    test_parameters: TestParameters = test_pipeline.parameters
    # For consistency set the character encoding ASCII which is
    # the lowest common denominator available on all systems.

    settings.SYSTEM_CHARACTER_ENCODING = "ASCII"
    test_pipeline.reset_user_definitions()

    output_data, names = test_pipeline.validate_group_setup(
        set(),
        None,
    )
    if (output_data, names) == INVALID_TEST_GROUP_SETUP:
        return

    # Loop over the whole documentation.
    for part in test_pipeline.documentation.parts:
        for chapter in part.chapters:
            for section in chapter.all_sections:
                section_name = section.title
                if excludes and section_name in excludes:
                    continue

                if test_status.total >= test_parameters.max_tests:
                    show_test_summary(
                        test_pipeline,
                        "chapters",
                        "",
                    )
                    return
                test_section_in_chapter(
                    test_pipeline,
                    section,
                    exclude_sections=excludes,
                )
                if test_status.failed_sections:
                    if not test_parameters.keep_going:
                        show_test_summary(
                            test_pipeline,
                            "chapters",
                            "",
                        )
                        return
                else:
                    if test_parameters.data_path:
                        create_output(
                            test_pipeline,
                            section_tests_iterator(
                                section,
                                test_pipeline,
                                exclude_sections=excludes,
                            ),
                        )
    show_test_summary(
        test_pipeline,
        "chapters",
        "",
    )

    return


def test_chapters(
    test_pipeline: DocTestPipeline,
    include_chapters: set,
    exclude_sections: set,
):
    """
    Runs a group of related tests for the set specified in ``chapters``.

    If ``quiet`` is True, the progress and results of the tests are shown.
    """
    test_status = test_pipeline.status
    test_parameters = test_pipeline.parameters

    output_data, chapter_names = test_pipeline.validate_group_setup(
        include_chapters, "chapters"
    )
    if (output_data, chapter_names) == INVALID_TEST_GROUP_SETUP:
        return

    for chapter_name in include_chapters:
        chapter_slug = slugify(chapter_name)
        for part in test_pipeline.documentation.parts:
            chapter = part.chapters_by_slug.get(chapter_slug, None)
            if chapter is None:
                continue
            for section in chapter.all_sections:
                test_section_in_chapter(
                    test_pipeline,
                    section,
                    exclude_sections=exclude_sections,
                )
                if test_parameters.data_path is not None and test_status.failed == 0:
                    create_output(
                        test_pipeline,
                        section.doc.get_tests(),
                    )

    show_test_summary(
        test_pipeline,
        "chapters",
        chapter_names,
    )

    return


def test_sections(
    test_pipeline: DocTestPipeline,
    include_sections: Set[str],
    exclude_subsections: Set[str],
):
    """Runs a group of related tests for the set specified in ``sections``.

    If ``quiet`` is True, the progress and results of the tests are shown.

    ``index`` has the current count. If ``keep_going`` is false
    then the remaining tests in a section are skipped when a test
    fails. If ``keep_going`` is True and there is a failure, the next
    section is continued after failure occurs.
    """
    test_status = test_pipeline.status
    test_parameters = test_pipeline.parameters

    output_data, section_names = test_pipeline.validate_group_setup(
        include_sections, "section"
    )
    if (output_data, section_names) == INVALID_TEST_GROUP_SETUP:
        return

    # seen_sections: Set[str] = set()
    # seen_last_section = False
    # last_section_name = None
    # section_name_for_finish = None

    for part in test_pipeline.documentation.parts:
        for chapter in part.chapters:
            for section in chapter.all_sections:
                test_section_in_chapter(
                    test_pipeline,
                    section=section,
                    include_sections=include_sections,
                    exclude_sections=exclude_subsections,
                )

                if test_parameters.data_path is not None and test_status.failed == 0:
                    create_output(
                        test_pipeline,
                        section.doc.get_tests(),
                    )

                # if last_section_name != section_name_for_finish:
                #     if seen_sections == include_sections:
                #         seen_last_section = True
                #         break
                #     if section_name_for_finish in include_sections:
                #         seen_sections.add(section_name_for_finish)
                #     last_section_name = section_name_for_finish

                # if seen_last_section:
                #     show_test_summary(test_pipeline, "sections", section_names)
                #     return

    show_test_summary(test_pipeline, "sections", section_names)
    return


def show_report(test_pipeline):
    """Print a report with the results of the tests"""
    test_status = test_pipeline.status
    test_parameters = test_pipeline.parameters
    total, failed = test_status.total, test_status.failed
    builtin_total = test_pipeline.builtin_total
    skipped = test_status.skipped
    if test_parameters.max_tests == MAX_TESTS:
        test_pipeline.print_and_log(
            f"{total} Tests for {builtin_total} built-in symbols, {total-failed} "
            f"passed, {failed} failed, {skipped} skipped.",
        )
    else:
        test_pipeline.print_and_log(
            f"{total} Tests, {total - failed} passed, {failed} failed, {skipped} "
            "skipped.",
        )
    if test_status.failed_sections:
        if not test_pipeline.parameters.keep_going:
            test_pipeline.print_and_log(
                "(not all tests are accounted for due to --)",
            )
        test_pipeline.print_and_log("Failed:")
        for part, chapter, section in sorted(test_status.failed_sections):
            test_pipeline.print_and_log(f"  - {section} in {part} / {chapter}")

    if test_parameters.data_path is not None and (
        test_status.failed == 0 or test_parameters.keep_going
    ):
        save_doctest_data(test_pipeline)
        return


def test_all(
    test_pipeline: DocTestPipeline,
    excludes: Optional[Set[str]] = None,
):
    """
    Run all the tests in the documentation.
    """
    test_parameters = test_pipeline.parameters
    test_status = test_pipeline.status
    if not test_parameters.quiet:
        test_pipeline.print_and_log(f"Testing {version_string}")

    try:
        test_tests(
            test_pipeline,
            excludes=excludes,
        )
    except KeyboardInterrupt:
        test_pipeline.print_and_log("\nAborted.\n")
        return

    if test_status.failed > 0:
        test_pipeline.print_and_log(SEP)

    show_report(test_pipeline)


def save_doctest_data(doctest_pipeline: DocTestPipeline):
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
    output_data: Dict[tuple, dict] = doctest_pipeline.output_data

    if len(output_data) == 0:
        doctest_pipeline.print_and_log("output data is empty")
        return
    doctest_pipeline.print_and_log(f"saving {len(output_data)} entries")
    doctest_pipeline.print_and_log(output_data.keys())
    doctest_latex_data_path = doctest_pipeline.parameters.data_path
    doctest_pipeline.print_and_log(
        f"Writing internal document data to {doctest_latex_data_path}"
    )
    i = 0
    for key in output_data:
        i = i + 1
        doctest_pipeline.print_and_log(f"{key}, {output_data[key]}")
        if i > 9:
            break
    with open(doctest_latex_data_path, "wb") as output_file:
        pickle.dump(output_data, output_file, 4)


def write_doctest_data(doctest_pipeline: DocTestPipeline):
    """
    Get doctest information, which involves running the tests to obtain
    test results and write out both the tests and the test results.
    """
    test_parameters = doctest_pipeline.parameters
    if not test_parameters.quiet:
        doctest_pipeline.print_and_log(
            f"Extracting internal doc data for {version_string}"
        )
        print("This may take a while...")

    try:
        doctest_pipeline.output_data = (
            load_doctest_data(test_parameters.data_path)
            if test_parameters.reload
            else {}
        )
        for tests in doctest_pipeline.documentation.get_tests():
            create_output(
                doctest_pipeline,
                tests,
            )
    except KeyboardInterrupt:
        doctest_pipeline.print_and_log("\nAborted.\n")
        return

    print("done.\n")

    save_doctest_data(doctest_pipeline)


def build_arg_parser():
    """Build the argument parser"""
    parser = ArgumentParser(description="Mathics test suite.", add_help=False)
    parser.add_argument(
        "--help", "-h", help="show this help message and exit", action="help"
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + mathics.__version__,
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
        help=(
            "generate pickled internal document data without running tests; "
            "Can't be used with --section or --reload."
        ),
    )
    parser.add_argument(
        "--reload",
        "-r",
        dest="reload",
        action="store_true",
        help="reload pickled internal document data, before possibly adding to it",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        dest="quiet",
        action="store_true",
        help="hide passed tests",
    )
    parser.add_argument(
        "--keep-going",
        "-k",
        dest="keep_going",
        action="store_true",
        help="create documentation even if there is a test failure",
    )
    parser.add_argument(
        "--stop-on-failure",
        "-x",
        dest="stop_on_failure",
        action="store_true",
        help="stop on failure",
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
    return parser.parse_args()


def main():
    """main"""
    args = build_arg_parser()
    data_path = (
        get_doctest_latex_data_path(should_be_readable=False, create_parent=True)
        if args.output
        else None
    )

    test_pipeline = DocTestPipeline(args, output_format="latex", data_path=data_path)
    test_status = test_pipeline.status

    start_time = None
    if args.sections:
        include_sections = set(args.sections.split(","))
        exclude_subsections = set(args.exclude.split(","))
        start_time = datetime.now()
        test_sections(test_pipeline, include_sections, exclude_subsections)
    elif args.chapters:
        start_time = datetime.now()
        include_chapters = set(args.chapters.split(","))
        exclude_sections = set(args.exclude.split(","))
        test_chapters(test_pipeline, include_chapters, exclude_sections)
    else:
        if args.doc_only:
            write_doctest_data(test_pipeline)
        else:
            excludes = set(args.exclude.split(","))
            start_time = datetime.now()
            test_all(test_pipeline, excludes=excludes)

    if test_status.total > 0 and start_time is not None:
        test_pipeline.print_and_log(
            f"Test evaluation took {datetime.now() - start_time} seconds"
        )
        test_pipeline.print_and_log(
            f"Test finished at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )

    if args.show_statistics:
        show_lru_cache_statistics()
    if test_pipeline.logfile:
        test_pipeline.logfile.close()

    if test_status.failed == 0:
        print("\nOK")
    else:
        print("\nFAILED")
        sys.exit(1)  # Travis-CI knows the tests have failed


if __name__ == "__main__":
    import_and_load_builtins()
    main()
