#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writes a folder with RsT files containing the entire User Manual.

The information for this comes from:

* the docstrings from loading in Mathics3 core (mathics)

* the docstrings from loading Mathics3 modules that have been specified
  on the command line

* doctest tests and test result that have been stored in a Python
  Pickle file, from a previous docpipeline.py run.  Ideally the
  Mathics3 Modules given to docpipeline.py are the same as
  given on the command line for this program
"""

import os
import os.path as osp
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Optional

from mpmath import __version__ as mpmathVersion
from numpy import __version__ as NumPyVersion
from sympy import __version__ as SymPyVersion

import mathics
from mathics import __version__, settings, version_info, version_string
from mathics.core.definitions import Definitions
from mathics.core.load_builtin import import_and_load_builtins
from mathics.doc.structure import MathicsMainDocumentation
from mathics.doc.utils import load_doctest_data
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
DOC_RST_DIR = os.environ.get("DOC_RST_DIR", settings.DOC_RST_DIR)


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
        return None
    except Exception:
        return {}


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
    versions.update(version_info)
    return versions


def process_doc_element(
    doc_element, doc_data, quiet=False, filter_chapters=None, filter_sections=None
):
    path = osp.join(
        DOC_RST_DIR, *[docelem.slug for docelem in doc_element.get_ancestors()[1:]]
    )
    # Ensure that the path to store the files already exists:
    if not Path(path).is_dir():
        os.makedirs(path)

    # Process all the children
    children = []

    # TODO: Implement filters. By now, just do not skip...
    def do_skip(c):
        return False

    for child_obj in doc_element.get_children():
        if do_skip(child_obj):
            continue

        child_idx = process_doc_element(
            child_obj, doc_data, quiet, filter_chapters, filter_sections
        )
        children.append(child_idx)

    slug = doc_element.slug
    title = doc_element.title
    content = title + "\n" + "=" * len(title) + "\n\n"

    if hasattr(doc_element, "doc") and doc_element.doc is not None:
        content += doc_element.doc.rst(doc_data)

    if children:
        content += "\n\n"
        content += ".. toctree::\n    :maxdepth: 4\n\n    "
        len_curr_path = len(path) + 1
        content += "\n    ".join(child[1][len_curr_path:] for child in children)
        content += "\n\n"

    path = osp.join(path, slug + ".rst")
    with open(path, "w") as outfile:
        outfile.write(content)
    return (title, path)


def write_rst(
    doc_data, quiet=False, filter_parts=None, filter_chapters=None, filter_sections=None
):
    documentation = MathicsMainDocumentation()
    documentation.load_documentation_sources()
    if not quiet:
        print(f"Writing ReStructured Text document to {DOC_RST_DIR}")

    seen_parts = set()
    parts_set = None
    if filter_parts is not None:
        parts_set = set(filter_parts.split(","))
    parts = []
    appendices = []
    for part in documentation.parts:
        if filter_parts:
            if part.title not in filter_parts:
                continue
        seen_parts.add(part.title)
        part_entry = process_doc_element(
            part, doc_data, quiet, filter_chapters, filter_sections
        )
        print("part entry:", part_entry, part.is_appendix)
        if part.is_appendix:
            appendices.append(part_entry)
        else:
            parts.append(part_entry)
        if parts_set == seen_parts:
            break

    len_curr_path = len(DOC_RST_DIR) + 1
    content = 30 * " " + "Mathics User Guide" + 30 * " " + "\n"
    content += 30 * " " + len("Mathics User Guide") * "#" + 30 * " " + "\n"
    content += "\n\n"
    content += ".. toctree::\n    :maxdepth: 4\n\n    "
    content += "\n    ".join(child[1][len_curr_path:] for child in parts)
    content += "\n    ".join(child[1][len_curr_path:] for child in appendices)
    content += "\n\n"

    with open(osp.join(DOC_RST_DIR, "index.rst"), "w") as outfile:
        outfile.write(content)

        DOC_VERSION_FILE = osp.join(DOC_RST_DIR, "version-info.tex")
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
        "You can list multiple chapters by adding a comma (and no space) in between "
        "chapter names.",
    )
    parser.add_argument(
        "--sections",
        "-s",
        dest="sections",
        metavar="SECTION",
        help="only test SECTION(s). "
        "You can list multiple chapters by adding a comma (and no space) in between "
        "chapter names.",
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

    print("importing builtins")
    import_and_load_builtins()

    print("processing arguments")
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
    write_rst(
        doctest_data,
        quiet=args.quiet,
        filter_parts=args.parts,
        filter_chapters=args.chapters,
        filter_sections=args.sections,
    )


if __name__ == "__main__":
    main()
