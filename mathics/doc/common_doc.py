# -*- coding: utf-8 -*-
"""

common_doc

This module is kept for backward compatibility.

The module was splitted into
* mathics.doc.doc_entries: classes contaning the documentation entries and doctests.
* mathics.doc.structure: the classes describing the elements in the documentation organization
* mathics.doc.gather: functions to gather information from modules to build the
  documentation reference.

"""


from mathics.doc.doc_entries import (
    DocTest,
    DocTests,
    DocText,
    DocumentationEntry,
    Tests,
    parse_docstring_to_DocumentationEntry_items,
)

gather_tests = parse_docstring_to_DocumentationEntry_items
XMLDOC = DocumentationEntry

from mathics.doc.structure import (
    DocChapter,
    DocGuideSection,
    DocPart,
    DocSection,
    DocSubsection,
    Documentation,
    MathicsMainDocumentation,
)
