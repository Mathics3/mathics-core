# -*- coding: utf-8 -*-
"""

common_doc

This module is kept for backward compatibility.

The module was split into
* mathics.doc.doc_entries: classes containing the documentation entries and doctests.
* mathics.doc.structure: the classes describing the elements in the documentation organization
* mathics.doc.gather: functions to gather information from modules to build the
  documentation reference.

"""


from mathics.doc.doc_entries import (
    ALLOWED_TAGS,
    ALLOWED_TAGS_RE,
    CONSOLE_RE,
    DL_ITEM_RE,
    DL_RE,
    HYPERTEXT_RE,
    IMG_RE,
    LATEX_RE,
    LIST_ITEM_RE,
    LIST_RE,
    MATHICS_RE,
    PYTHON_RE,
    QUOTATIONS_RE,
    REF_RE,
    SPECIAL_COMMANDS,
    DocTest,
    DocTests,
    DocText,
    DocumentationEntry,
    Tests,
    get_results_by_test,
    parse_docstring_to_DocumentationEntry_items,
    post_sub,
    pre_sub,
)

gather_tests = parse_docstring_to_DocumentationEntry_items
XMLDOC = DocumentationEntry

from mathics.doc.structure import (
    MATHICS3_MODULES_TITLE,
    SUBSECTION_END_RE,
    SUBSECTION_RE,
    DocChapter,
    DocGuideSection,
    DocPart,
    DocSection,
    DocSubsection,
    Documentation,
    MathicsMainDocumentation,
    sorted_chapters,
)

__all__ = [
    "ALLOWED_TAGS",
    "ALLOWED_TAGS_RE",
    "CONSOLE_RE",
    "DL_ITEM_RE",
    "DL_RE",
    "DocChapter",
    "DocGuideSection",
    "DocPart",
    "DocSection",
    "DocSubsection",
    "DocTest",
    "DocTests",
    "DocText",
    "Documentation",
    "DocumentationEntry",
    "HYPERTEXT_RE",
    "IMG_RE",
    "LATEX_RE",
    "LIST_ITEM_RE",
    "LIST_RE",
    "MATHICS3_MODULES_TITLE",
    "MATHICS_RE",
    "MathicsMainDocumentation",
    "PYTHON_RE",
    "QUOTATIONS_RE",
    "REF_RE",
    "SPECIAL_COMMANDS",
    "SUBSECTION_END_RE",
    "SUBSECTION_RE",
    "Tests",
    "get_results_by_test",
    "parse_docstring_to_DocumentationEntry_items",
    "post_sub",
    "pre_sub",
    "sorted_chapters",
]
