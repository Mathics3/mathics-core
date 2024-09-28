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

import_and_load_builtins()
DOCUMENTATION = MathicsMainDocumentation()
DOCUMENTATION.load_documentation_sources()


def test_load_doctests():
    # there are in master 3959 tests...
    all_the_tests = tuple((tests for tests in DOCUMENTATION.get_tests()))
    visited_positions = set()
    # Check that there are not dupliceted entries
    for tests in all_the_tests:
        position = (tests.part, tests.chapter, tests.section)
        print(position)
        assert position not in visited_positions
        visited_positions.add(position)


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
