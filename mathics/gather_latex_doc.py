#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Does 2 things which can are necessary for producing LaTeX documentation
that produces the Mathics3 PDF.

1. Extracts tests and runs them from static mdoc files and docstrings from
   Mathics3 built-in functions
2. Creates/updates internal documentation data
"""
import pickle
import sys

from mathics.core.load_builtin import import_and_load_builtins
from mathics.doc.utils import open_ensure_dir
from mathics.docpipeline import (
    DocTestPipeline,
    build_arg_parser,
    test_all,
    test_chapters,
    test_sections,
    write_doctest_data,
)
from mathics.settings import get_doctest_latex_data_path


def save_doctest_data(output_data):
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

    doctest_latex_data_path = get_doctest_latex_data_path(
        should_be_readable=False, create_parent=True
    )
    print(f"Writing internal document data to {doctest_latex_data_path}")
    with open_ensure_dir(doctest_latex_data_path, "wb") as output_file:
        pickle.dump(output_data, output_file, 4)


def main():
    args = build_arg_parser()
    data_path = (
        get_doctest_latex_data_path(should_be_readable=False, create_parent=True)
        if args.output
        else None
    )

    test_pipeline = DocTestPipeline(
        args, output_format="latex", data_path=data_path, doc_only=args.doc_only
    )
    test_status = test_pipeline.status

    if args.sections:
        include_sections = set(args.sections.split(","))
        exclude_subsections = set(args.exclude.split(","))
        test_sections(
            test_pipeline, include_sections, exclude_subsections, output_format="latex"
        )
    elif args.chapters:
        include_chapters = set(args.chapters.split(","))
        exclude_sections = set(args.exclude.split(","))
        test_chapters(
            test_pipeline, include_chapters, exclude_sections, output_format="latex"
        )
    else:
        if args.doc_only:
            write_doctest_data(test_pipeline, output_format="latex")
        else:
            excludes = set(args.exclude.split(","))
            test_all(test_pipeline, excludes=excludes, output_format="latex")

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
