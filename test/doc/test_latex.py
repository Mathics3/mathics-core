"""
Pytests for the documentation system. Basic functions and classes.
"""
import os.path as osp

from mathics.core.evaluation import Message, Print
from mathics.doc.latex_doc import (
    LaTeXDocChapter,
    LaTeXDocPart,
    LaTeXDocSection,
    LaTeXDocTest,
    LaTeXDocTests,
    LaTeXDocText,
    LaTeXDocumentationEntry,
    LaTeXMathicsDocumentation,
    parse_docstring_to_DocumentationEntry_items,
)
from mathics.settings import DOC_DIR


def test_load_latex_documentation():

    ssss = LaTeXDocTest(
        index=0,
        testcase="f[x_] := 4 x / (x ^ 2 + 3 x + 5)",
        key_prefix=(
            "Manual",
            "Further Tutorial Examples",
            "Curve Sketching",
        ),
    )

    documentation = LaTeXMathicsDocumentation()
    documentation.load_documentation_sources()
    doc_data = {
        ("Manual", "Further Tutorial Examples", "Curve Sketching", 0,): {
            "query": "f[x_] := 4 x / (x ^ 2 + 3 x + 5)",
            "results": [
                {
                    "out": [],
                    "result": "o",
                }
            ],
        },
    }
    part = documentation.get_part("manual")
    assert isinstance(part, LaTeXDocPart)

    third_chapter = part.chapters[2]
    assert isinstance(third_chapter, LaTeXDocChapter)

    first_section = third_chapter.sections[0]
    assert isinstance(first_section, LaTeXDocSection)

    doc_in_section = first_section.doc
    assert isinstance(doc_in_section, LaTeXDocumentationEntry)
    assert all(
        isinstance(
            item,
            (
                LaTeXDocText,
                LaTeXDocTests,
            ),
        )
        for item in doc_in_section.items
    )

    tests = doc_in_section.get_tests()
    assert isinstance(tests, list)
    assert isinstance(tests[0], LaTeXDocTest)

    assert tests[0].latex(doc_data) == (
        r"%% Test Manual/Further Tutorial Examples/Curve Sketching/0"
        "\n"
        r"\begin{testcase}"
        "\n"
        r"\test{\lstinline'f[x\_] := 4 x / (x ^ 2 + 3 x + 5)'}"
        "\n"
        r"%% mathics-1.asy"
        "\n"
        r"\begin{testresult}o\end{testresult}\end{testcase}"
    )
    assert doc_in_section.latex(doc_data)[:30] == "Let's sketch the function\n\\beg"
    assert first_section.latex(doc_data)[:30] == "\n\n\\section*{Curve Sketching}{}"
    assert third_chapter.latex(doc_data)[:30] == "\n\n\\chapter{Further Tutorial Ex"
