"""
Pytests for the documentation system. Basic functions and classes.
"""

from mathics.doc.doc_entries import (
    DocTest,
    DocTests,
    DocText,
    parse_docstring_to_DocumentationEntry_items,
)

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
    assert all([t == m for t, m in zip(num_tests, [1, 2, 1, 2, 1])])
