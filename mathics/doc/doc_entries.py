"""
Documentation entries and doctests

This module contains the objects representing the entries in the documentation
system, and the functions used to parse docstrings into these objects.


"""

import logging
import re
from os import getenv
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Sequence

from mathics.core.evaluation import Message, Print, _Out

if TYPE_CHECKING:
    from mathics.doc.structure import DocSection

# Used for getting test results by test expression and chapter/section information.
test_result_map: Dict[tuple, list] = {}


# These are all the XML/HTML-like tags that documentation supports.
ALLOWED_TAGS = (
    "dl",
    "dd",
    "dt",
    "em",
    "url",
    "ul",
    "i",
    "ol",
    "li",
    "con",
    "console",
    "img",
    "imgpng",
    "ref",
    "subsection",
)
ALLOWED_TAGS_RE = dict(
    (allowed, re.compile("&lt;(%s.*?)&gt;" % allowed)) for allowed in ALLOWED_TAGS
)

# This string is used, so we can indicate a trailing blank at the end of a line by
# adding this string to the end of the line which gets stripped off.
# Some editors and formatters like to strip off trailing blanks at the ends of lines.
END_LINE_SENTINAL = "#<--#"

# The regular expressions below (strings ending with _RE
# pull out information from docstring or text in a file. Ghetto parsing.

CONSOLE_RE = re.compile(r"(?s)<(?P<tag>con|console)>(?P<content>.*?)</(?P=tag)>")
DL_ITEM_RE = re.compile(
    r"(?s)<(?P<tag>d[td])>(?P<content>.*?)(?:</(?P=tag)>|)\s*(?:(?=<d[td]>)|$)"
)
DL_RE = re.compile(r"(?s)<dl>(.*?)</dl>")
HYPERTEXT_RE = re.compile(
    r"(?s)<(?P<tag>em|url)>(\s*:(?P<text>.*?):\s*)?(?P<content>.*?)</(?P=tag)>"
)
IMG_PNG_RE = re.compile(
    r'<imgpng src="(?P<src>.*?)" title="(?P<title>.*?)" label="(?P<label>.*?)">'
)
IMG_RE = re.compile(
    r'<img src="(?P<src>.*?)" title="(?P<title>.*?)" label="(?P<label>.*?)">'
)
# Preserve space before and after in-line code variables.
LATEX_RE = re.compile(r"(\s?)\$(\w+?)\$(\s?)")

LIST_ITEM_RE = re.compile(r"(?s)<li>(.*?)(?:</li>|(?=<li>)|$)")
LIST_RE = re.compile(r"(?s)<(?P<tag>ul|ol)>(?P<content>.*?)</(?P=tag)>")
MATHICS_RE = re.compile(r"(?<!\\)\'(.*?)(?<!\\)\'")

PYTHON_RE = re.compile(r"(?s)<python>(.*?)</python>")
QUOTATIONS_RE = re.compile(r"\"([\w\s,]*?)\"")
REF_RE = re.compile(r'<ref label="(?P<label>.*?)">')
SPECIAL_COMMANDS = {
    "LaTeX": (r"<em>LaTeX</em>", r"\LaTeX{}"),
    "Mathematica": (
        r"<em>Mathematica</em>&reg;",
        r"\emph{Mathematica}\textregistered{}",
    ),
    "Mathics": (r"<em>Mathics3</em>", r"\emph{Mathics3}"),
    "Mathics3": (r"<em>Mathics3</em>", r"\emph{Mathics3}"),
    "Sage": (r"<em>Sage</em>", r"\emph{Sage}"),
    "Wolfram": (r"<em>Wolfram</em>", r"\emph{Wolfram}"),
    "skip": (r"<br /><br />", r"\bigskip"),
}


TESTCASE_RE = re.compile(
    r"""(?mx)^  # re.MULTILINE (multi-line match)
                # and re.VERBOSE (readable regular expressions
        ((?:.|\n)*?)
        ^\s+([>#SX])>[ ](.*)  # test-code indicator
        ((?:\n\s*(?:[:|=.][ ]|\.).*)*)  # test-code results"""
)
TESTCASE_OUT_RE = re.compile(r"^\s*([:|=])(.*)$")


def get_results_by_test(test_expr: str, full_test_key: list, doc_data: dict) -> dict:
    """
    Sometimes test numbering is off, either due to bugs or changes since the
    data was read.

    Here, we compensate for this by looking up the test by its chapter and section name
    portion stored in `full_test_key` along with the and the test expression data
    stored in `test_expr`.

    This new key is looked up in `test_result_map` its value is returned.

    `doc_data` is only first time this is called to populate `test_result_map`.
    """

    # Strip off the test index form new key with this and the test string.
    # Add to any existing value for that "result". This is now what we want to
    # use as a tee in test_result_map to look for.
    test_section = list(full_test_key)[:-1]
    search_key = tuple(test_section)

    if not test_result_map:
        # Populate test_result_map from doc_data
        for key, result in doc_data.items():
            test_section = list(key)[:-1]
            new_test_key = tuple(test_section)
            next_result = test_result_map.get(new_test_key, None)
            if next_result is None:
                next_result = [result]
            else:
                next_result.append(result)

            test_result_map[new_test_key] = next_result

    results = test_result_map.get(search_key, None)
    result = {}
    if results:
        for result_candidate in results:
            if result_candidate["query"] == test_expr:
                if result:
                    # Already found something
                    logging.warning(
                        f"Warning, multiple results appear under {search_key}."
                    )
                    return {}

                result = result_candidate

    return result


def filter_comments(doc: str) -> str:
    """Remove docstring documentation comments. These are lines
    that start with ##"""
    return "\n".join(
        line for line in doc.splitlines() if not line.lstrip().startswith("##")
    )


POST_SUBSTITUTION_TAG = "_POST_SUBSTITUTION%d_"


def pre_sub(regexp, text: str, repl_func: Callable):
    """apply substitutions previous to parse the text"""
    post_substitutions: List[str] = []

    def repl_pre(match):
        repl = repl_func(match)
        index = len(post_substitutions)
        post_substitutions.append(repl)
        return POST_SUBSTITUTION_TAG % index

    text = regexp.sub(repl_pre, text)

    return text, post_substitutions


def post_sub(text: str, post_substitutions) -> str:
    """apply substitutions after parsing the doctests."""
    for index, sub in enumerate(post_substitutions):
        text = text.replace(POST_SUBSTITUTION_TAG % index, sub)
    return text


def parse_docstring_to_DocumentationEntry_items(
    doc: str,
    test_collection_constructor: Callable,
    test_case_constructor: Callable,
    text_constructor: Callable,
    key_part=None,
) -> List["DocumentationEntry"]:
    """
    This parses string `doc` (using regular expressions) into Python objects.
    The function returns a list of ``DocText`` and ``DocTests`` objects which
    are contained in a ``DocumentationElement``.

    test_collection_constructor() is the class constructor call to create an
    object for the test collection.
    Each test is created via test_case_constructor().
    Text within the test is stored via text_constructor.
    """
    # This function is used to populate a ``DocumentEntry`` element, that
    # in principle is not associated to any container
    # (``DocChapter``/``DocSection``/``DocSubsection``)
    # of the documentation system.
    #
    # The ``key_part`` parameter was used to set the ``key`` of the
    # ``DocTest`` elements. This attribute
    # should be set just after the  ``DocumentationEntry`` (
    # to which the tests belongs) is associated
    # to a container, by calling  ``container.set_parent_path``.
    # However, the parameter is still used in MathicsDjango, so let's
    # keep it and discard its value.
    #
    if key_part:
        logging.warning("``key_part`` is deprecated. Its value is discarded.")

    # Remove commented lines.
    doc = filter_comments(doc).strip(r"\s")

    # Remove leading <dl>...</dl>
    # doc = DL_RE.sub("", doc)

    # pre-substitute Python code because it might contain tests
    doc, post_substitutions = pre_sub(
        PYTHON_RE, doc, lambda m: "<python>%s</python>" % m.group(1)
    )

    # HACK: Artificially construct a last testcase to get the "intertext"
    # after the last (real) testcase. Ignore the test, of course.
    doc += "\n >> test\n = test"
    testcases = TESTCASE_RE.findall(doc)

    tests = None
    items = []
    for index, test_case in enumerate(testcases):
        testcase = list(test_case)
        text = testcase.pop(0).strip()
        if text:
            if tests is not None:
                items.append(tests)
                tests = None
            text = post_sub(text, post_substitutions)
            # Remove line breaks
            text = re.sub(r" \\\n[ ]*", r" ", text)
            text = re.sub(r"\\\n[ ]*", r" ", text)
            items.append(text_constructor(text))
            tests = None
        if index < len(testcases) - 1:
            test = test_case_constructor(index, testcase, None)
            if tests is None:
                tests = test_collection_constructor()
            tests.tests.append(test)

    # If the last block in the loop was not a Text block, append the
    # last set of tests.
    if tests is not None:
        items.append(tests)
        tests = None
    return items


class DocTest:
    """
    Class to hold a single doctest.

    DocTest formatting rules:

    * `>>` Marks test case; it will also appear as part of
           the documentation.
    * `#>` Marks test private or one that does not appear as part of
           the documentation.
    * `X>` Shows the example in the docs, but disables testing the example.
    * `S>` Shows the example in the docs, but disables testing if environment
           variable SANDBOX is set.
    * `=`  Compares the result text.
    * `:`  Compares an (error) message.
      `|`  Prints output.
    """

    def __init__(
        self,
        index: int,
        testcase: List[str],
        key_prefix: Optional[tuple] = None,
    ):
        def strip_sentinal(line: str):
            """Remove END_LINE_SENTINAL from the end of a line if it appears.

            Some editors like to strip blanks at the end of a line.
            Since the line ends in END_LINE_SENTINAL which isn't blank,
            any blanks that appear before will be preserved.

            Some tests require some lines to be blank or entry because
            Mathics3 output can be that way
            """
            if line.endswith(END_LINE_SENTINAL):
                line = line[: -len(END_LINE_SENTINAL)]

            # Also remove any remaining trailing blanks since that
            # seems *also* what we want to do.
            return line.strip()

        self.index = index
        self.outs: List[_Out] = []
        self.result = None

        # Private test cases are executed, but NOT shown as part of the docs
        self.private = testcase[0] == "#"

        # Ignored test cases are NOT executed, but shown as part of the docs
        # Sandboxed test cases are NOT executed if environment SANDBOX is set
        if testcase[0] == "X" or (testcase[0] == "S" and getenv("SANDBOX", False)):
            self.ignore = True
            # substitute '>' again so we get the correct formatting
            testcase[0] = ">"
        else:
            self.ignore = False

        self.test = strip_sentinal(testcase[1])
        self._key: Optional[tuple] = key_prefix + (index,) if key_prefix else None

        outs = testcase[2].splitlines()
        for line in outs:
            line = strip_sentinal(line)
            if line:
                if line.startswith("."):
                    text = line[1:]
                    if text.startswith(" "):
                        text = text[1:]
                    text = "\n" + text
                    if self.result is not None:
                        self.result += text
                    elif self.outs:
                        self.outs[-1].text += text
                    continue

                match = TESTCASE_OUT_RE.match(line)
                if not match:
                    continue
                symbol, text = match.group(1), match.group(2)
                text = text.strip()
                if symbol == "=":
                    self.result = text
                elif symbol == ":":
                    self.outs.append(Message("", "", text))
                elif symbol == "|":
                    self.outs.append(Print(text))

    def __str__(self) -> str:
        return self.test

    def compare(self, result: Optional[str], out: tuple = tuple()) -> bool:
        """
        Performs a doctest comparison between ``result`` and ``wanted`` and returns
        True if the test should be considered a success.
        """
        return self.compare_result(result) and self.compare_out(out)

    def compare_result(self, result: Optional[str]):
        """Compare a result with the expected result"""
        wanted = self.result
        # Check result
        if wanted in ("...", result):
            return True

        if result is None or wanted is None:
            return False
        result_list = result.splitlines()
        wanted_list = wanted.splitlines()
        if result_list == [] and wanted_list == ["#<--#"]:
            return True

        if len(result_list) != len(wanted_list):
            return False

        for res, want in zip(result_list, wanted_list):
            wanted_re = re.escape(want.strip())
            wanted_re = wanted_re.replace("\\.\\.\\.", ".*?")
            wanted_re = f"^{wanted_re}$"
            if not re.match(wanted_re, res.strip()):
                return False
        return True

    def compare_out(self, outs: tuple = tuple()) -> bool:
        """Compare messages and warnings produced during the evaluation of
        the test with the expected messages and warnings."""
        # Check out
        wanted_outs = self.outs
        if len(wanted_outs) == 1 and wanted_outs[0].text == "...":
            # If we have ... don't check
            return True
        if len(outs) != len(wanted_outs):
            # Mismatched number of output lines, and we don't have "..."
            return False

        # Need to check all output line by line
        for got, wanted in zip(outs, wanted_outs):
            if wanted.text == "...":
                return True
            if not got == wanted:
                return False

        return True

    @property
    def key(self):
        """key identifier of the test"""
        return self._key if hasattr(self, "_key") else None

    @key.setter
    def key(self, value):
        """setter for the key identifier of the test"""
        assert self.key is None
        self._key = value
        return self._key


class DocTests:
    """
    A bunch of consecutive ``DocTest`` objects extracted from a Builtin docstring.
    """

    def __init__(self):
        self.tests = []
        self.text = ""

    def get_tests(self) -> list:
        """
        Returns lists test objects.
        """
        return self.tests

    # def is_private(self) -> bool:
    #     """Returns True if this test is "private" not supposed to be visible as example documentation."""
    #     return all(test.private for test in self.tests)

    def __str__(self) -> str:
        return "\n".join(str(test) for test in self.tests)

    def test_indices(self) -> List[int]:
        """indices of the tests"""
        return [test.index for test in self.tests]


class DocText:
    """
    Class to hold some (non-test) text.

    Some of the kinds of tags you may find here are showing in global ALLOWED_TAGS.
    Some text may be marked with surrounding "$" or "'".

    The code here however does not make use of any of the tagging.

    """

    def __init__(self, text):
        self.text = text

    def __str__(self) -> str:
        return self.text

    def get_tests(self) -> list:
        """
        Return tests in a DocText item - there never are any.
        """
        return []

    # def is_private(self) -> bool:
    #     """the test is private, meaning that it will not be included in the
    #     documentation, but tested in the doctest cycle."""
    #     return False

    def test_indices(self) -> List[int]:
        """indices of the tests"""
        return []


# Former XMLDoc
class DocumentationEntry:
    """
    A class to hold the content of a documentation entry,
    in our custom XML-like format.

    Describes the contain of an entry in the documentation system, as a
    sequence (list) of items of the clase  `DocText` and `DocTests`.
    ``DocText`` items contains an internal XML-like formatted text. ``DocTests`` entries
    contain one or more `DocTest` element.
    Each level of the Documentation hierarchy contains an XMLDoc, describing the
    content after the title and before the elements of the next level. For example,
    in ``DocChapter``, ``DocChapter.doc`` contains the text coming after the title
    of the chapter, and before the sections in `DocChapter.sections`.
    Specialized classes like LaTeXDoc or and DjangoDoc provide methods for
    getting formatted output. For LaTeXDoc ``latex()`` is added while for
    DjangoDoc ``html()`` is added
    Mathics core also uses this in getting usage strings (`??`).

    """

    items: Sequence["DocumentationEntry"]

    def __init__(
        self, doc_str: str, title: str, section: Optional["DocSection"] = None
    ):
        self._set_classes()
        self.title = title
        self.path = None
        if section:
            chapter = section.chapter
            part = chapter.part
            # Note: we elide section.title
            key_prefix = (part.title, chapter.title, title)
        else:
            key_prefix = None

        self.key_prefix = key_prefix
        self.rawdoc = doc_str
        self.items = parse_docstring_to_DocumentationEntry_items(
            self.rawdoc,
            self.docTest_collection_class,
            self.docTest_class,
            self.docText_class,
            None,
        )

    def _set_classes(self):
        """
        Tells to the initializator the classes to be used to build the items.
        This must be overloaded by the daughter classes.
        """
        if not hasattr(self, "docTest_collection_class"):
            self.docTest_collection_class = DocTests
            self.docTest_class = DocTest
            self.docText_class = DocText

    def __str__(self) -> str:
        return "\n\n".join(str(item) for item in self.items)

    def text(self) -> str:
        """text version of the documentation entry"""
        # used for introspection
        # TODO parse XML and pretty print
        # HACK
        item = str(self.items[0])
        item = "\n".join(line.strip() for line in item.split("\n"))
        item = item.replace("<dl>", "")
        item = item.replace("</dl>", "")
        item = item.replace("<dt>", "  ")
        item = item.replace("</dt>", "")
        item = item.replace("<dd>", "    ")
        item = item.replace("</dd>", "")
        item = "\n".join(line for line in item.split("\n") if not line.isspace())
        return item

    def get_tests(self) -> List["DocTest"]:
        """retrieve a list of tests in the documentation entry"""
        tests = []
        for item in self.items:
            tests.extend(item.get_tests())
        return tests

    def set_parent_path(self, parent):
        """Set the parent path"""
        self.path = None
        path = []
        while hasattr(parent, "parent"):
            path = [parent.title] + path
            parent = parent.parent

        if hasattr(parent, "title"):
            path = [parent.title] + path

        if path:
            self.path = path
            # Set the key on each test
            for test in self.get_tests():
                assert test.key is None
                # For backward compatibility, we need
                # to reduce this to three fields.
                # TODO: remove me and ensure that this
                # works here and in Mathics Django
                if len(path) > 3:
                    path = path[:2] + [path[-1]]
                test.key = tuple(path) + (test.index,)

        return self


class Tests:
    """
    A group of tests in the same section or subsection.
    """

    def __init__(
        self,
        part_name: str,
        chapter_name: str,
        section_name: str,
        doctests: List[DocTest],
        subsection_name: Optional[str] = None,
    ):
        self.part = part_name
        self.chapter = chapter_name
        self.section = section_name
        self.subsection = subsection_name
        self.tests = doctests
        self._key = None

    @property
    def key(self):
        """key of the tests"""
        return self._key

    @key.setter
    def key(self, value):
        assert self._key is None
        self._key = value
        return self._key
