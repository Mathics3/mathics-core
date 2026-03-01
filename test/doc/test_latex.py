"""
Pytests for the documentation system. Basic functions and classes.
"""

from mathics.core.load_builtin import import_and_load_builtins
from mathics.doc.latex_doc import (
    LaTeXDocChapter,
    LaTeXDocPart,
    LaTeXDocSection,
    LaTeXDocTest,
    LaTeXDocTests,
    LaTeXDocText,
    LaTeXDocumentationEntry,
    LaTeXMathicsDocumentation,
)

# Load the documentation once.
import_and_load_builtins()
LATEX_DOCUMENTATION = LaTeXMathicsDocumentation()

TEST_DOC_DATA_DICT = {
    (
        "Manual",
        "Further Tutorial Examples",
        "Curve Sketching",
        0,
    ): {
        "query": "f[x_] := 4 x / (x ^ 2 + 3 x + 5)",
        "results": [
            {
                "out": [],
                "result": "o",
            }
        ],
    },
}


def test_load_latex_documentation():
    """
    Test the structure of the LaTeX Documentation
    """

    documentation = LATEX_DOCUMENTATION
    doc_data = TEST_DOC_DATA_DICT

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
    assert (
        doc_in_section.latex(doc_data)[:39]
    ).strip() == "Let's sketch the function\n\\begin{tests}"
    assert (
        first_section.latex(doc_data)[:30]
    ).strip() == "\\section{Curve Sketching}{}"
    assert (
        third_chapter.latex(doc_data)[:38]
    ).strip() == "\\chapter{Further Tutorial Examples}"


def test_chapter():
    documentation = LATEX_DOCUMENTATION
    part = documentation.parts[1]
    chapter = part.chapters_by_slug["testing-expressions"]
    print(chapter.sections_by_slug.keys())
    section = chapter.sections_by_slug["numerical-properties"]
    expected_latex_section_head = (
        "\\section{Numerical Properties}\n"
        "\\label{reference-of-built-in-symbols/testing-expressions/numerical-properties}\n"
        "\\sectionstart\n\n\n\n"
        "\\subsection{CoprimeQ}\\index{CoprimeQ}"
    )
    latex_section_head = section.latex({}).strip()[: len(expected_latex_section_head)]

    assert latex_section_head == expected_latex_section_head
    print(60 * "@")
    latex_chapter = chapter.latex({}, quiet=False)

    count = 0
    next_pos = 0
    while True:
        print(next_pos)
        next_pos = latex_chapter.find(latex_section_head, next_pos + 64)
        if next_pos == -1:
            break
        count += 1

    assert count == 1, "The section is rendered twice"
