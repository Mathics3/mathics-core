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
from datetime import datetime
from typing import Callable, Dict, Optional, Set, Union

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
    """Output class for tests"""

    def max_stored_size(self, _):
        return None


# Global variables

# FIXME: After 3.8 is the minimum Python we can turn "str" into a Literal
SEP: str = "-" * 70 + "\n"
STARS: str = "*" * 10


MAX_TESTS = 100000  # A number greater than the total number of tests.


# When 3.8 is base, the below can be a Literal type.
INVALID_TEST_GROUP_SETUP = (None, None)


class TestParameters:
    """
    Parameters of the test.
    """

    def __init__(self, args):
        self.check_partial_elapsed_time = args.elapsed_times
        self.generate_output = args.output
        self.keep_going = args.keep_going and not args.stop_on_failure
        self.logfile = open(args.logfilename, "wt") if args.logfilename else None
        self.max_tests = args.count + args.skip
        self.quiet = args.quiet
        self.reload = args.reload
        self.start_at = args.skip + 1

        self.definitions = Definitions(add_builtin=True)

        # LoadModule Mathics3 modules
        if args.pymathics:
            required_modules = set(args.pymathics.split(","))
            load_pymathics_modules(required_modules, self.definitions)

        self.builtin_total = len(_builtins)
        self.documentation = MathicsMainDocumentation()
        self.documentation.load_documentation_sources()

    def reset_user_definitions(self):
        """Reset the user definitions"""
        return self.definitions.reset_user_definitions()

    def print_and_log(self, message):
        """Print and log a message in the logfile"""
        if not self.quiet:
            print(message)
        if self.logfile:
            print_and_log(self.logfile, message.encode("utf-8"))


class TestStatus:
    """
    Status parameters of the tests
    """

    def __init__(self, generate_output=False):
        self.texdatafolder = self.find_texdata_folder() if generate_output else None
        self.total = 0
        self.failed = 0
        self.skipped = 0
        self.output_data = {}
        self.failed_sections = set()
        self.prev_key = []

    def find_texdata_folder(self):
        """Generate a folder for texdata"""
        return osp.dirname(
            settings.get_doctest_latex_data_path(
                should_be_readable=False, create_parent=True
            )
        )

    def validate_group_setup(
        self,
        include_set: set,
        entity_name: Optional[str],
        test_parameters: TestParameters,
    ):
        """
        Common things that need to be done before running a group of doctests.
        """

        if test_parameters.documentation is None:
            test_parameters.print_and_log("Documentation is not initialized.")
            return INVALID_TEST_GROUP_SETUP

        if entity_name is not None:
            include_names = ", ".join(include_set)
            print(f"Testing {entity_name}(s): {include_names}")
        else:
            include_names = None

        if test_parameters.reload:
            doctest_latex_data_path = settings.get_doctest_latex_data_path(
                should_be_readable=True
            )
            self.output_data = load_doctest_data(doctest_latex_data_path)
        else:
            self.output_data = {}

        # For consistency set the character encoding ASCII which is
        # the lowest common denominator available on all systems.
        settings.SYSTEM_CHARACTER_ENCODING = "ASCII"

        if test_parameters.definitions is None:
            test_parameters.print_and_log("Definitions are not initialized.")
            return INVALID_TEST_GROUP_SETUP

        # Start with a clean variables state from whatever came before.
        # In the test suite however, we may set new variables.
        test_parameters.reset_user_definitions()
        return self.output_data, include_names


def test_case(
    test: DocTest,
    test_parameters: TestParameters,
    fail: Optional[Callable] = lambda x: False,
) -> bool:
    """
    Run a single test cases ``test``. Return True if test succeeds and False if it
    fails. ``index``gives the global test number count, while ``subindex`` counts
    from the beginning of the section or subsection.

    The test results are assumed to be foramtted to ASCII text.
    """
    test_str = test.test

    feeder = MathicsSingleLineFeeder(test_str, filename="<test>")
    evaluation = Evaluation(
        test_parameters.definitions,
        catch_interrupt=False,
        output=TestOutput(),
        format="text",
    )
    try:
        time_parsing = datetime.now()
        query = evaluation.parse_feeder(feeder)
        if test_parameters.check_partial_elapsed_time:
            print("   parsing took", datetime.now() - time_parsing)
        if query is None:
            # parsed expression is None
            result = None
            out = evaluation.out
        else:
            result = evaluation.evaluate(query)
            if test_parameters.check_partial_elapsed_time:
                print("   evaluation took", datetime.now() - time_parsing)
            out = result.out
            result = result.result
    except Exception as exc:
        fail(f"Exception {exc}")
        info = sys.exc_info()
        sys.excepthook(*info)
        return False

    time_comparing = datetime.now()
    comparison_result = test.compare_result(result)

    if test_parameters.check_partial_elapsed_time:
        print("   comparison took ", datetime.now() - time_comparing)
    if not comparison_result:
        print("result != wanted")
        fail_msg = f"Result: {result}\nWanted: {test.result}"
        if out:
            fail_msg += "\nAdditional output:\n"
            fail_msg += "\n".join(str(o) for o in out)
        return fail(fail_msg)

    time_comparing = datetime.now()
    output_ok = test.compare_out(out)
    if test_parameters.check_partial_elapsed_time:
        print("   comparing messages took ", datetime.now() - time_comparing)
    if not output_ok:
        return fail(
            "Output:\n%s\nWanted:\n%s"
            % (
                "\n".join(str(o) for o in out),
                "\n".join(str(o) for o in test.outs),
            )
        )
    return True


def create_output(tests, doctest_data, test_parameters, output_format="latex"):
    """
    Populate ``doctest_data`` with the results of the
    ``tests`` in the format ``output_format``
    """
    if test_parameters.definitions is None:
        test_parameters.print_and_log("Definitions are not initialized.")
        return

    test_parameters.definitions.reset_user_definitions()

    for test in tests:
        if test.private:
            continue
        key = test.key
        evaluation = Evaluation(
            test_parameters.definitions,
            format=output_format,
            catch_interrupt=True,
            output=TestOutput(),
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
    test_status: TestStatus,
    test_parameters: TestParameters,
    entity_name: str,
    entities_searched: str,
):
    """
    Print and log test summary results.

    If ``generate_output`` is True, we will also generate output data
    to ``output_data``.
    """
    failed = test_status.failed
    print()
    if test_status.total == 0:
        test_parameters.print_and_log(
            f"No {entity_name} found with a name in: {entities_searched}.",
        )
        if "MATHICS_DEBUG_TEST_CREATE" not in os.environ:
            print(f"Set environment MATHICS_DEBUG_TEST_CREATE to see {entity_name}.")
    elif failed > 0:
        print(SEP)
        if not test_parameters.generate_output:
            test_parameters.print_and_log(
                f"""{failed} test{'s' if failed != 1 else ''} failed.""",
            )
    else:
        test_parameters.print_and_log("All tests passed.")

    if test_parameters.generate_output and (failed == 0 or test_parameters.keep_going):
        save_doctest_data(test_status.output_data)


def section_tests_iterator(
    section, test_parameters, include_subsections=None, exclude_sections=None
):
    """
    Iterator over tests in a section.
    A section contains tests in its documentation entry,
    in the head of the chapter and in its subsections.
    This function is a generator of all these tests.

    Before yielding a test from a documentation entry,
    the user definitions are reset.
    """
    chapter = section.chapter
    subsections = [section]
    if chapter.doc:
        subsections = [chapter.doc] + subsections
    if section.subsections:
        subsections = subsections + section.subsections

    for subsection in subsections:
        if (
            include_subsections is not None
            and subsection.title not in include_subsections
        ):
            continue
        if exclude_sections and subsection.title in exclude_sections:
            continue
        test_parameters.reset_user_definitions()
        for test in subsection.get_tests():
            yield test


#
#  TODO: Split and simplify this section
#
#
def test_section_in_chapter(
    test_status: TestStatus,
    test_parameters: TestParameters,
    section: Union[DocSection, DocGuideSection],
    include_sections: Optional[Set[str]] = None,
    exclude_sections: Optional[Set[str]] = None,
):
    """
    Runs a tests for section ``section`` under a chapter or guide section.
    Note that both of these contain a collection of section tests underneath.
    """
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
    subsections = [section]
    if chapter.doc:
        subsections = [chapter.doc] + subsections
    if section.subsections:
        subsections = subsections + section.subsections

    section_name_for_print = ""
    for test in section_tests_iterator(
        section, test_parameters, include_subsections, exclude_sections
    ):
        # Get key dropping off test index number
        key = list(test.key)[1:-1]
        section_name_for_print = " / ".join(key)
        if test_status.prev_key != key:
            test_status.prev_key = key
            if test_parameters.quiet:
                # We don't print with stars inside in test_case(), so print here.
                print(f"Testing section: {section_name_for_print}")
                show_verbose = None
            else:

                def show_verbose(test_str, index=0, subindex=0):
                    print(f"{STARS} {section_name_for_print} {STARS}")
                    print(f"{index:4d} ({subindex:2d}): TEST {test_str}")

            index = 0
        else:
            # Null out section name, so that on the next iteration we do not
            # print a section header
            # in test_case().
            section_name_for_print = ""

            def show_verbose(test_str, index=0, subindex=0):
                if not test_parameters.quiet:
                    print(f"{index:4d} ({subindex:2d}): TEST {test_str}")

        tests = test.tests if isinstance(test, DocTests) else [test]

        for doctest in tests:
            if doctest.ignore:
                continue

            index += 1
            test_status.total += 1
            if test_status.total > test_parameters.max_tests:
                return
            if test_status.total < test_parameters.start_at:
                test_status.skipped += 1
                continue

            def fail_message(why):
                test_parameters.print_and_log(
                    (
                        f"""{SEP}Test failed: in {part_name} / {chapter_name} / {section_name}\n"""
                        f"""{part_name}\n{why}"""
                    ),
                )
                return False

            if show_verbose:
                show_verbose(doctest.test, test_status.total, index)

            success = test_case(
                doctest,
                test_parameters,
                fail=fail_message,
            )
            if not success:
                test_status.failed += 1
                test_status.failed_sections.add(
                    (
                        part_name,
                        chapter_name,
                        key[-1],
                    )
                )
                if not test_parameters.keep_going:
                    return

    return


def test_tests(
    test_status: TestStatus,
    test_parameters: TestParameters,
    excludes: Set[str] = set(),
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

    # For consistency set the character encoding ASCII which is
    # the lowest common denominator available on all systems.
    settings.SYSTEM_CHARACTER_ENCODING = "ASCII"
    test_parameters.reset_user_definitions()

    output_data, names = test_status.validate_group_setup(
        set(),
        None,
        test_parameters,
    )
    if (output_data, names) == INVALID_TEST_GROUP_SETUP:
        return

    def show_and_return():
        """Show the resume and build the tuple to return"""
        show_test_summary(
            test_status,
            test_parameters,
            "chapters",
            "",
        )

        if test_parameters.generate_output and (
            test_status.failed == 0 or test_parameters.keep_going
        ):
            save_doctest_data(test_status.output_data)

    # Loop over the whole documentation.
    for part in test_parameters.documentation.parts:
        for chapter in part.chapters:
            for section in chapter.all_sections:
                section_name = section.title
                if section_name in excludes:
                    continue

                if test_status.total >= test_parameters.max_tests:
                    show_and_return()
                    return
                test_section_in_chapter(
                    test_status, test_parameters, section, exclude_sections=excludes
                )
                if test_status.failed_sections:
                    if not test_parameters.keep_going:
                        show_and_return()
                        return
                else:
                    if test_parameters.generate_output:
                        create_output(
                            section_tests_iterator(
                                section, test_parameters, exclude_sections=excludes
                            ),
                            test_status.output_data,
                            test_parameters,
                        )
    show_and_return()
    return


def test_chapters(
    test_status: TestStatus,
    test_parameters: TestParameters,
    include_chapters: set,
    exclude_sections: set,
) -> int:
    """
    Runs a group of related tests for the set specified in ``chapters``.

    If ``quiet`` is True, the progress and results of the tests are shown.
    """
    output_data, chapter_names = test_status.validate_group_setup(
        include_chapters, "chapters", test_parameters
    )
    if (output_data, chapter_names) == INVALID_TEST_GROUP_SETUP:
        return test_status.total

    def show_and_return():
        """Show the resume and return"""
        show_test_summary(
            test_status,
            test_parameters,
            "chapters",
            chapter_names,
        )
        return test_status.total

    for chapter_name in include_chapters:
        chapter_slug = slugify(chapter_name)
        for part in test_parameters.documentation.parts:
            chapter = part.chapters_by_slug.get(chapter_slug, None)
            if chapter is None:
                continue
            for section in chapter.all_sections:
                test_section_in_chapter(
                    test_status,
                    test_parameters,
                    section,
                    exclude_sections=exclude_sections,
                )
                if test_parameters.generate_output and test_status.failed == 0:
                    create_output(
                        section.doc.get_tests(),
                        test_status.output_data,
                        test_parameters,
                    )

    return show_and_return()


def test_sections(
    test_status: TestStatus,
    test_parameters: TestParameters,
    include_sections: set,
    exclude_subsections: set,
) -> int:
    """Runs a group of related tests for the set specified in ``sections``.

    If ``quiet`` is True, the progress and results of the tests are shown.

    ``index`` has the current count. If ``keep_going`` is false
    then the remaining tests in a section are skipped when a test
    fails. If ``keep_going`` is True and there is a failure, the next
    section is continued after failure occurs.
    """
    output_data, section_names = test_status.validate_group_setup(
        include_sections, "section", test_parameters
    )
    if (output_data, section_names) == INVALID_TEST_GROUP_SETUP:
        return test_status.total

    seen_sections = set()
    seen_last_section = False
    last_section_name = None
    section_name_for_finish = None

    def show_and_return():
        show_test_summary(
            test_status,
            test_parameters,
            "sections",
            section_names,
        )
        return test_status.total

    for part in test_parameters.documentation.parts:
        for chapter in part.chapters:
            for section in chapter.all_sections:
                test_section_in_chapter(
                    test_status,
                    test_parameters,
                    section=section,
                    include_sections=include_sections,
                    exclude_sections=exclude_subsections,
                )

                if test_parameters.generate_output and test_status.failed == 0:
                    create_output(
                        section.doc.get_tests(),
                        test_status.output_data,
                        test_parameters,
                    )

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


def show_report(test_status, test_parameters):
    """Print a report with the results of the tests"""
    total, failed = test_status.total, test_status.failed
    builtin_total = test_parameters.builtin_total
    skipped = test_status.skipped
    if test_parameters.max_tests == MAX_TESTS:
        test_parameters.print_and_log(
            f"{total} Tests for {builtin_total} built-in symbols, {total-failed} "
            f"passed, {failed} failed, {skipped} skipped.",
        )
    else:
        test_parameters.print_and_log(
            f"{total} Tests, {total - failed} passed, {failed} failed, {skipped} "
            "skipped.",
        )
    if test_status.failed_sections:
        if not test_parameters.keep_going:
            test_parameters.print_and_log(
                "(not all tests are accounted for due to --)",
            )
        test_parameters.print_and_log("Failed:")
        for part, chapter, section in sorted(test_status.failed_sections):
            test_parameters.print_and_log(f"  - {section} in {part} / {chapter}")

    if test_parameters.generate_output and (
        test_status.failed == 0 or test_parameters.doc_even_if_error
    ):
        save_doctest_data(test_status.output_data)
        return total


def test_all(
    test_status: TestStatus,
    test_parameters: TestParameters,
    excludes: set = set(),
) -> int:
    """
    Run all the tests in the documentation.
    """
    if not test_parameters.quiet:
        print(f"Testing {version_string}")

    test_parameters.reload = False
    try:
        test_tests(
            test_status,
            test_parameters,
            excludes=excludes,
        )
    except KeyboardInterrupt:
        print("\nAborted.\n")
        return test_status.total

    if test_status.failed > 0:
        print(SEP)

    show_report(test_status, test_parameters)


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
    if len(output_data) == 0:
        print("output data is empty")
        return
    print("saving", len(output_data), "entries")
    print(output_data.keys())
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


def write_doctest_data(test_status: TestStatus, test_parameters: TestParameters):
    """
    Get doctest information, which involves running the tests to obtain
    test results and write out both the tests and the test results.
    """
    if not test_parameters.quiet:
        print(f"Extracting internal doc data for {version_string}")
        print("This may take a while...")

    doctest_latex_data_path = settings.get_doctest_latex_data_path(
        should_be_readable=False, create_parent=True
    )

    try:
        test_status.output_data = (
            load_doctest_data(doctest_latex_data_path) if test_parameters.reload else {}
        )
        for tests in test_parameters.documentation.get_tests():
            create_output(tests, test_status.output_data, test_parameters)
    except KeyboardInterrupt:
        print("\nAborted.\n")
        return

    print("done.\n")
    save_doctest_data(test_status.output_data)


def main():
    """main"""

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

    args = parser.parse_args()
    test_parameters = TestParameters(args)
    test_status = TestStatus(generate_output=args.output)

    start_time = None

    if args.sections:
        include_sections = set(args.sections.split(","))
        exclude_sections = set(args.exclude.split(","))
        start_time = datetime.now()
        test_sections(
            test_status,
            test_parameters,
            include_sections,
            exclude_subsections,
        )
    elif args.chapters:
        start_time = datetime.now()
        include_chapters = set(args.chapters.split(","))
        exclude_sections = set(args.exclude.split(","))
        test_chapters(
            test_status,
            test_parameters,
            include_chapters,
            exclude_sections,
        )
    else:
        if args.doc_only:
            write_doctest_data(test_status, test_parameters)
        else:
            excludes = set(args.exclude.split(","))
            start_time = datetime.now()
            test_all(
                test_status,
                excludes=excludes,
                test_parameters=test_parameters,
            )

    if test_status.total > 0 and start_time is not None:
        end_time = datetime.now()
        print("Test evalation took ", end_time - start_time)

    if test_parameters.logfile:
        test_parameters.logfile.close()
    if args.show_statistics:
        show_lru_cache_statistics()

    if test_status.failed == 0:
        print("\nOK")
    else:
        print("\nFAILED")
        sys.exit(1)  # Travis-CI knows the tests have failed


if __name__ == "__main__":
    import_and_load_builtins()
    main()
