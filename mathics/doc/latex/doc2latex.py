#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writes a LaTeX file containing the entire User Manual.

The information for this comes from:

* the docstrings from loading in Mathics3 core (mathics)

* the docstrings from loading Mathics3 modules that have been specified
  on the command line

* doctest tests and test result that have been stored in a Python
  Pickle file, from a privious docpipeline.py run.  Ideally the
  Mathics3 Modules given to docpipeline.py are the same as
  given on the command line for this program
"""

import os
import os.path as osp
import pickle
import subprocess
import sys
from argparse import ArgumentParser
from typing import Dict, Optional

from mpmath import __version__ as mpmathVersion
from numpy import __version__ as NumPyVersion
from sympy import __version__ as SymPyVersion

import mathics
from mathics import __version__, settings, version_string
from mathics.core.definitions import Definitions
from mathics.doc.latex_doc import LaTeXMathicsDocumentation
from mathics.eval.pymathics import PyMathicsLoadException, eval_LoadModule

# Global variables
logfile = None

# Input doctest PCL FILE. This contains just the
# tests and test results.
#
# This information is stitched in with information comes from
# docstrings that are loaded from load Mathics builtins and external modules.

DOCTEST_LATEX_DATA_PCL = settings.DOCTEST_LATEX_DATA_PCL

# Output location information
DOC_LATEX_DIR = os.environ.get("DOC_LATEX_DIR", settings.DOC_LATEX_DIR)
DOC_LATEX_FILE = os.environ.get("DOC_LATEX_FILE", settings.DOC_LATEX_FILE)


def read_doctest_data(quiet=False) -> Optional[Dict[tuple, dict]]:
    """
    Read doctest information from PCL file and return this.
    This is a wrapper around laod_doctest_data().
    """
    if not quiet:
        print(f"Extracting internal doctest data for {version_string}")
    try:
        return load_doctest_data(
            settings.get_doctest_latex_data_path(should_be_readable=True)
        )
    except KeyboardInterrupt:
        print("\nAborted.\n")
        return


def load_doctest_data(data_path, quiet=False) -> Dict[tuple, dict]:
    """
    Read doctest information from PCL file and return this.

    The return value is a dictionary of test results. The key is a tuple
    of:
    * Part name,
    * Chapter name,
    * [Guide Section name],
    * Section name,
    * Subsection name,
    * test number
    and the value is a dictionary of a Result.getdata() dictionary.
    """
    if not quiet:
        print(f"Loading LaTeX internal data from {data_path}")
    with open_ensure_dir(data_path, "rb") as doc_data_fp:
        return pickle.load(doc_data_fp)


def open_ensure_dir(f, *args, **kwargs):
    try:
        return open(f, *args, **kwargs)
    except (IOError, OSError):
        d = osp.dirname(f)
        if d and not osp.exists(d):
            os.makedirs(d)
        return open(f, *args, **kwargs)


def print_and_log(*args):
    global logfile
    a = [a.decode("utf-8") if isinstance(a, bytes) else a for a in args]
    string = "".join(a)
    print(string)
    if logfile:
        logfile.write(string)


def get_versions():
    def try_cmd(cmd_list: tuple, stdout_or_stderr: str) -> str:
        status = subprocess.run(cmd_list, capture_output=True)
        if status.returncode == 0:
            out = getattr(status, stdout_or_stderr)
            return out.decode("utf-8").split("\n")[0]
        else:
            return "Unknown"

    versions = {
        "MathicsCoreVersion": __version__,
        "PythonVersion": sys.version,
        "NumPyVersion": NumPyVersion,
        "SymPyVersion": SymPyVersion,
        "mpmathVersion": mpmathVersion,
    }

    for name, cmd, field in (
        ["AsymptoteVersion", ("asy", "--version"), "stderr"],
        ["XeTeXVersion", ("xetex", "--version"), "stdout"],
        ["GhostscriptVersion", ("gs", "--version"), "stdout"],
    ):
        versions[name] = try_cmd(cmd, field)
    return versions


def write_latex(
    doc_data, quiet=False, filter_parts=None, filter_chapters=None, filter_sections=None
):
    documentation = LaTeXMathicsDocumentation()
    if not quiet:
        print(f"Writing LaTeX document to {DOC_LATEX_FILE}")
    with open_ensure_dir(DOC_LATEX_FILE, "wb") as doc:
        content = documentation.latex(
            doc_data,
            quiet=quiet,
            filter_parts=filter_parts,
            filter_chapters=filter_chapters,
            filter_sections=filter_sections,
        )
        content = content.encode("utf-8")
        doc.write(content)
    DOC_VERSION_FILE = osp.join(DOC_LATEX_DIR, "version-info.tex")
    if not quiet:
        print(f"Writing Mathics Core Version Information to {DOC_VERSION_FILE}")
    with open(DOC_VERSION_FILE, "w") as doc:
        doc.write("%% Mathics core version number created via doc2latex.py\n\n")
        for name, version_info in get_versions().items():
            doc.write("""\\newcommand{\\%s}{%s}\n""" % (name, version_info))


def main():

    global logfile

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
        "You can list multiple chapters by adding a comma (and no space) in between chapter names.",
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
        "--parts",
        "-p",
        dest="parts",
        metavar="PART",
        help="only test PART(s). "
        "You can list multiple parts by adding a comma (and no space) in between part names.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        dest="quiet",
        action="store_true",
        help="Don't show formatting progress tests",
    )
    args = parser.parse_args()

    # LoadModule Mathics3 modules to pull in modules, and
    # their docstrings
    if args.pymathics:
        definitions = Definitions(add_builtin=True)
        for module_name in args.pymathics.split(","):
            try:
                eval_LoadModule(module_name, definitions)
            except PyMathicsLoadException:
                print(f"Python module {module_name} is not a Mathics3 module.")

            except Exception as e:
                print(f"Python import errors with: {e}.")
            else:
                print(f"Mathics3 Module {module_name} loaded")

    doctest_data = read_doctest_data(quiet=args.quiet)
    write_latex(
        doctest_data,
        quiet=args.quiet,
        filter_parts=args.parts,
        filter_chapters=args.chapters,
        filter_sections=args.sections,
    )


if __name__ == "__main__":
    main()
