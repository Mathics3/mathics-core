"""
Pytests for the documentation system. Basic functions and classes.
"""

import os.path as osp

from mathics.core.evaluation import Message, Print
from mathics.core.load_builtin import import_and_load_builtins
from mathics.doc.common_doc import (
    DocChapter,
    DocPart,
    DocSection,
    Documentation,
    MathicsMainDocumentation,
)
from mathics.doc.doc_entries import (
    DocTest,
    DocTests,
    DocText,
    DocumentationEntry,
    parse_docstring_to_DocumentationEntry_items,
)
from mathics.settings import DOC_DIR

DOCTEST_ENTRY = """
    <dl>
      <dt>'TestSymbol'
      <dd>it is just a test example of docstring entry
    </dl>

    A doctest with a result value
    >> 2 + 2
     = 4

    Two consuecutive tests:
    >> a={1,2,3}
     = {1, 2, 3}
    >> Tr[a]
     = 6

    A doctest without a result value
    >> Print["Hola"]
     | Hola

    A private doctest without a result, followed
    by a private doctest with a result
    #> Null
    #> 2+2
     = 4
    A private doctest with a message
    #> 1/0
     : Infinite expression 1 / 0 encountered.
     = ComplexInfinity\
"""


def test_gather_parse_docstring_to_DocumentationEntry_items():
    """Check the behavior of parse_docstring_to_DocumentationEntry_items"""

    base_expected_types = [DocText, DocTests] * 5
    cases = [
        (
            DOCTEST_ENTRY[133:],
            base_expected_types[1:],
        ),
        (
            DOCTEST_ENTRY + "\n\n And a last paragraph\n with two lines.\n",
            base_expected_types + [DocText],
        ),
        (
            DOCTEST_ENTRY,
            base_expected_types,
        ),
    ]

    for test_case, list_expected_types in cases:
        result = parse_docstring_to_DocumentationEntry_items(
            test_case,
            DocTests,
            DocTest,
            DocText,
            (
                "part example",
                "chapter example",
                "section example",
            ),
        )
        assert isinstance(result, list)
        # These check that the gathered elements are the expected:
        assert len(list_expected_types) == len(result)
        assert all([isinstance(t, cls) for t, cls in zip(result, list_expected_types)])

    tests = [t for t in result if isinstance(t, DocTests)]
    num_tests = [len(t.tests) for t in tests]
    assert len(tests) == 5
    assert all([t == l for t, l in zip(num_tests, [1, 2, 1, 2, 1])])


def test_create_doctest():
    """initializing DocTest"""

    key = (
        "Part title",
        "Chapter Title",
        "Section Title",
    )
    test_cases = [
        {
            "test": [">", "2+2", "\n    = 4"],
            "properties": {
                "private": False,
                "ignore": False,
                "result": "4",
                "outs": [],
                "key": key + (1,),
            },
        },
        {
            "test": ["#", "2+2", "\n    = 4"],
            "properties": {
                "private": True,
                "ignore": False,
                "result": "4",
                "outs": [],
                "key": key + (1,),
            },
        },
        {
            "test": ["S", "2+2", "\n    = 4"],
            "properties": {
                "private": False,
                "ignore": False,
                "result": "4",
                "outs": [],
                "key": key + (1,),
            },
        },
        {
            "test": ["X", 'Print["Hola"]', "| Hola"],
            "properties": {
                "private": False,
                "ignore": True,
                "result": None,
                "outs": [Print("Hola")],
                "key": key + (1,),
            },
        },
        {
            "test": [
                ">",
                "1 / 0",
                "\n : Infinite expression 1 / 0 encountered.\n ComplexInfinity",
            ],
            "properties": {
                "private": False,
                "ignore": False,
                "result": None,
                "outs": [
                    Message(
                        symbol="", text="Infinite expression 1 / 0 encountered.", tag=""
                    )
                ],
                "key": key + (1,),
            },
        },
    ]
    for index, test_case in enumerate(test_cases):
        doctest = DocTest(1, test_case["test"], key)
        for property_key, value in test_case["properties"].items():
            assert getattr(doctest, property_key) == value


def test_load_documentation():
    documentation = Documentation()
    fn = osp.join(DOC_DIR, "1-Manual.mdoc")
    documentation.load_part_from_file(fn, "Main part", False)
    part = documentation.get_part("main-part")
    assert isinstance(part, DocPart)
    third_chapter = part.chapters[2]
    assert isinstance(third_chapter, DocChapter)
    first_section = third_chapter.sections[0]
    assert isinstance(first_section, DocSection)
    doc_in_section = first_section.doc
    assert isinstance(doc_in_section, DocumentationEntry)
    assert all(
        isinstance(
            item,
            (
                DocText,
                DocTests,
            ),
        )
        for item in doc_in_section.items
    )
    tests = doc_in_section.get_tests()
    assert isinstance(tests, list)
    assert isinstance(tests[0], DocTest)


def test_load_mathics_documentation():
    import_and_load_builtins()
    documentation = MathicsMainDocumentation()
    documentation.load_documentation_sources()

    # Check that there are not repeated elements.
    visited_parts = set([])
    for part in documentation.parts:
        assert part.title not in visited_parts
        visited_chapters = set([])
        for chapter in part.chapters:
            assert chapter.title not in visited_chapters
            visited_chapters.add(chapter.title)
            visited_sections = set([])
            for section in chapter.all_sections:
                assert section.title not in visited_sections
                visited_sections.add(section.title)
                visited_subsections = set([])
                for subsection in section.subsections:
                    assert subsection.title not in visited_subsections
                    visited_subsections.add(subsection.title)
