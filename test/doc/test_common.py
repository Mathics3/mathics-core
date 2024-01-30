from mathics.doc.common_doc import DocTest, DocTests, DocText, Tests, gather_tests

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
     : 
     = ComplexInfinity

"""


def test_gather_tests():
    """Check the behavioir of gather_tests"""

    base_expected_types = [
        DocText,
        DocTests,
        DocText,
        DocTests,
        DocText,
        DocTests,
        DocText,
        DocTests,
        DocText,
        DocTests,
    ]
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

    for case, list_expected_types in cases:
        result = gather_tests(
            case,
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
        assert len(list_expected_types) == len(result)
        assert all([isinstance(t, cls) for t, cls in zip(result, list_expected_types)])

    tests = [t for t in result if isinstance(t, DocTests)]
    num_tests = [len(t.tests) for t in tests]
    assert len(tests) == 5
    assert all([t == l for t, l in zip(num_tests, [1, 2, 1, 2, 1])])


def test_create_doctest():
    """DocTest"""

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
            },
        }
    ]
    for index, test_case in enumerate(test_cases):
        doctest = DocTest(1, test_case["test"], key)
        for property_key, value in test_case["properties"].items():
            assert getattr(doctest, property_key) == value