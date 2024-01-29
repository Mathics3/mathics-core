# -*- coding: utf-8 -*-
"""
A module and library that assists in organizing document data
located in static files and docstrings from
Mathics3 Builtin Modules. Builtin Modules are written in Python and
reside either in the Mathics3 core (mathics.builtin) or are packaged outside,
e.g. pymathics.natlang.

This data is stored in a way that facilitates:
* organizing information to produce a LaTeX file
* running documentation tests
* producing HTML-based documentation

The command-line utility ``docpipeline.py``, loads the data from
Python modules and static files, accesses the functions here.

Mathics Django also uses this library for its HTML-based documentation.

The Mathics3 builtin function ``Information[]`` also uses to provide the
information it reports.

As with reading in data, final assembly to a LaTeX file or running
documentation tests is done elsewhere.

FIXME: This code should be replaced by Sphinx and autodoc.
Things are such a mess, that it is too difficult to contemplate this right now. Also there
higher-priority flaws that are more more pressing.

In the shorter, we might we move code for extracting printing to a separate package.
"""

import importlib
import logging
import os.path as osp
import pkgutil
import re
from os import environ, getenv, listdir
from types import ModuleType
from typing import Callable, Iterator, List, Optional, Tuple

from mathics import settings
from mathics.core.builtin import check_requires_list
from mathics.core.evaluation import Message, Print
from mathics.core.load_builtin import (
    builtins_by_module as global_builtins_by_module,
    mathics3_builtins_modules,
)
from mathics.core.util import IS_PYPY
from mathics.doc.utils import slugify
from mathics.eval.pymathics import pymathics_builtins_by_module, pymathics_modules

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

CHAPTER_RE = re.compile('(?s)<chapter title="(.*?)">(.*?)</chapter>')
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
SECTION_RE = re.compile('(?s)(.*?)<section title="(.*?)">(.*?)</section>')
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
SUBSECTION_END_RE = re.compile("</subsection>")
SUBSECTION_RE = re.compile('(?s)<subsection title="(.*?)">')

TESTCASE_RE = re.compile(
    r"""(?mx)^  # re.MULTILINE (multi-line match)
                # and re.VERBOSE (readable regular expressions
        ((?:.|\n)*?)
        ^\s+([>#SX])>[ ](.*)  # test-code indicator
        ((?:\n\s*(?:[:|=.][ ]|\.).*)*)  # test-code results"""
)
TESTCASE_OUT_RE = re.compile(r"^\s*([:|=])(.*)$")

# Used for getting test results by test expresson and chapter/section information.
test_result_map = {}

# Debug flags.

# Set to True if want to follow the process
# The first phase is building the documentation data structure
# based on docstrings:

MATHICS_DEBUG_DOC_BUILD: bool = "MATHICS_DEBUG_DOC_BUILD" in environ

# After building the doc structure, we extract test cases.
MATHICS_DEBUG_TEST_CREATE: bool = "MATHICS_DEBUG_TEST_CREATE" in environ


def get_module_doc(module: ModuleType) -> Tuple[str, str]:
    doc = module.__doc__
    if doc is not None:
        doc = doc.strip()
    if doc:
        title = doc.splitlines()[0]
        text = "\n".join(doc.splitlines()[1:])
    else:
        title = module.__name__
        for prefix in ("mathics.builtin.", "mathics.optional."):
            if title.startswith(prefix):
                title = title[len(prefix) :]
        title = title.capitalize()
        text = ""
    return title, text


def get_results_by_test(test_expr: str, full_test_key: list, doc_data: dict) -> dict:
    """
    Sometimes test numbering is off, either due to bugs or changes since the
    data was read.

    Here, we compensate for this by looking up the test by its chapter and section name
    portion stored in `full_test_key` along with the and the test expresion data
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
                    logging.warning(f"multiple results appear under {search_key}.")
                    return {}
                else:
                    result = result_candidate

    return result


def get_submodule_names(obj) -> list:
    """Many builtins are organized into modules which, from a documentation
    standpoint, are like Mathematica Online Guide Docs.

    "List Functions", "Colors", or "Distance and Similarity Measures"
    are some examples Guide Documents group group various Bultin Functions,
    under submodules relate to that general classification.

    Here, we want to return a list of the Python modules under a "Guide Doc"
    module.

    As an example of a "Guide Doc" and its submodules, consider the
    module named mathics.builtin.colors. It collects code and documentation pertaining
    to the builtin functions that would be found in the Guide documenation for "Colors".

    The `mathics.builtin.colors` module has a submodule
    `mathics.builtin.colors.named_colors`.

    The builtin functions defined in `named_colors` then are those found in the
    "Named Colors" group of the "Colors" Guide Doc.

    So in this example then, in the list the modules returned for
    Python module `mathics.builtin.colors` would be the
    `mathics.builtin.colors.named_colors` module which contains the
    definition and docs for the "Named Colors" Mathics Bultin
    Functions.
    """
    modpkgs = []
    if hasattr(obj, "__path__"):
        for importer, modname, ispkg in pkgutil.iter_modules(obj.__path__):
            modpkgs.append(modname)
        modpkgs.sort()
    return modpkgs


def filter_comments(doc: str) -> str:
    """Remove docstring documentation comments. These are lines
    that start with ##"""
    return "\n".join(
        line for line in doc.splitlines() if not line.lstrip().startswith("##")
    )


def get_doc_name_from_module(module) -> str:
    name = "???"
    if module.__doc__:
        lines = module.__doc__.strip()
        if not lines:
            name = module.__name__
        else:
            name = lines.split("\n")[0]
    return name


POST_SUBSTITUTION_TAG = "_POST_SUBSTITUTION%d_"


def pre_sub(regexp, text: str, repl_func):
    post_substitutions = []

    def repl_pre(match):
        repl = repl_func(match)
        index = len(post_substitutions)
        post_substitutions.append(repl)
        return POST_SUBSTITUTION_TAG % index

    text = regexp.sub(repl_pre, text)

    return text, post_substitutions


def post_sub(text: str, post_substitutions) -> str:
    for index, sub in enumerate(post_substitutions):
        text = text.replace(POST_SUBSTITUTION_TAG % index, sub)
    return text


def skip_doc(cls) -> bool:
    """Returns True if we should skip cls in docstring extraction."""
    return cls.__name__.endswith("Box") or (hasattr(cls, "no_doc") and cls.no_doc)


def skip_module_doc(module, modules_seen) -> bool:
    return (
        module.__doc__ is None
        or module in modules_seen
        or module.__name__.split(".")[0] not in ("mathics", "pymathics")
        or hasattr(module, "no_doc")
        and module.no_doc
    )


def gather_tests(
    doc: str,
    test_collection_constructor: Callable,
    test_case_constructor: Callable,
    text_constructor: Callable,
    key_part=None,
) -> list:
    """
    This parses string `doc` (using regular expresssions) into Python objects.
    test_collection_fn() is the class construtorto call to create an object for the
    test collection. Each test is created via test_case_fn().
    Text within the test is stored via text_constructor.
    """
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
    for index in range(len(testcases)):
        testcase = list(testcases[index])
        text = testcase.pop(0).strip()
        if text:
            if tests is not None:
                items.append(tests)
                tests = None
            text = post_sub(text, post_substitutions)
            items.append(text_constructor(text))
            tests = None
        if index < len(testcases) - 1:
            test = test_case_constructor(index, testcase, key_part)
            if tests is None:
                tests = test_collection_constructor()
            tests.tests.append(test)
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

    def __init__(self, index, testcase, key_prefix: tuple):
        def strip_sentinal(line):
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

        self.part = key_prefix[0]
        self.chapter = key_prefix[1]
        self.section = key_prefix[2]
        self.index = index
        self.outs = []
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

        self.key = None
        if key_prefix:
            self.key = tuple(key_prefix + (index,))

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
                    out = Message("", "", text)
                    self.outs.append(out)
                elif symbol == "|":
                    out = Print(text)
                    self.outs.append(out)

    def __str__(self):
        return self.test


# FIXME: Turn into a NamedTuple?

# Looking at https://github.com/mathics/Mathics/blob/eba5c22990fae01cd2579d13bbeabcfdb5221426/mathics/doc/doc.py
#
# The class Test was used to yield tests from the Documentation.get_tests() function,
# while DocTests was used as items in the Doc object (now DocText). It is possible that Tests should subclass DocTests.
#
#
#
class Tests:
    """
    A group of tests in the same section or subsection of the Documentation.
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


class DocChapter:
    """An object for a Documented Chapter.
    A Chapter is part of a Part[dChapter. It can contain (Guide or plain) Sections.
    """

    def __init__(self, part, title, doc):
        self.doc = doc
        self.guide_sections = []
        self.part = part
        self.title = title
        self.slug = slugify(title)
        self.sections = []
        self.sections_by_slug = {}
        part.chapters_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("  DEBUG Creating Chapter", title)

    def __str__(self) -> str:
        sections = "\n".join(section.title for section in self.sections)
        return f"= {self.part.title}: {self.title} =\n\n{sections}"

    @property
    def all_sections(self):
        return sorted(self.sections + self.guide_sections)

    def doc_chapter(
        self,
        module,
        builtin_part,
        builtins_by_module,
        modules_seen: set,
        submodule_names_seen: set,
    ):
        """
        Extracts documentation and test data for a Chapter.
        A Chapter is the level just under a "Part" and above
        a "Guide Section" or a "Section".
        """
        builtins = builtins_by_module.get(module.__name__)
        if module.__file__.endswith("__init__.py"):
            # We have a Guide Section.
            name = get_doc_name_from_module(module)
            guide_section = self.doc.add_section(
                self, name, module, operator=None, is_guide=True
            )
            self.guide_sections.append(guide_section)
            submodules = [
                value
                for value in module.__dict__.values()
                if isinstance(value, ModuleType)
            ]

            def sorted_submodule(submodules):
                return sorted(
                    submodules,
                    key=lambda submodule: submodule.sort_order
                    if hasattr(submodule, "sort_order")
                    else submodule.__name__,
                )

            # Add sections in the guide section...
            for submodule in sorted_submodule(submodules):
                if skip_module_doc(submodule, modules_seen):
                    continue
                elif IS_PYPY and submodule.__name__ == "builtins":
                    # PyPy seems to add this module on its own,
                    # but it is not something that can be importable
                    continue

                submodule_name = get_doc_name_from_module(submodule)
                if submodule_name in submodule_names_seen:
                    continue
                section = self.doc.add_section(
                    self,
                    submodule_name,
                    submodule,
                    operator=None,
                    is_guide=False,
                    in_guide=True,
                )
                modules_seen.add(submodule)
                submodule_names_seen.add(submodule_name)
                if guide_section is not None:
                    guide_section.subsections.append(section)

                builtins = builtins_by_module.get(submodule.__name__, [])
                subsections = [builtin for builtin in builtins]
                for instance in subsections:
                    if hasattr(instance, "no_doc") and instance.no_doc:
                        continue

                    name = instance.get_name(short=True)
                    if name in submodule_names_seen:
                        continue

                    submodule_names_seen.add(name)
                    modules_seen.add(instance)

                    self.doc.add_subsection(
                        self,
                        section,
                        name,
                        instance,
                        instance.get_operator(),
                        in_guide=True,
                    )
        else:
            if not builtins:
                return
            sections = [
                builtin for builtin in builtins if not skip_doc(builtin.__class__)
            ]
            self.doc.doc_sections(sections, modules_seen, self)
        builtin_part.chapters.append(self)

    def get_tests(self) -> Iterator[Tests]:
        """
        Generator which returns all of the Mathics3 Doctest-type tests for a given chapter.
        It is assumed that everything has been "gathered" or parsed and
        extracted from all modules previously.
        """

        for section in self.all_sections:
            if section.installed:
                if section.in_guide:
                    # Sections inside a Guide Section should have been
                    # processed when the Guide section was processed which
                    # should happen first.
                    continue

                if MATHICS_DEBUG_TEST_CREATE:
                    if isinstance(section, DocGuideSection):
                        print(
                            f"DEBUG Gathering tests for   Guide Section {section.title}"
                        )
                    else:
                        print(f"DEBUG Gathering tests for      Section {section.title}")

                if isinstance(section, DocGuideSection):
                    for docsection in section.subsections:
                        for docsubsection in docsection.subsections:
                            # FIXME: Something is weird here where tests for subsection items
                            # appear not as a collection but individually and need to be
                            # iterated below. Probably some other code is faulty and
                            # when fixed the below loop and collection into doctest_list[]
                            # will be removed.
                            if not docsubsection.installed:
                                continue
                            doctest_list = []
                            index = 1
                            for doctests in docsubsection.items:
                                doctest_list += list(doctests.tests)
                                for test in doctest_list:
                                    test.index = index
                                    index += 1

                            if doctest_list:
                                yield Tests(
                                    section.chapter.part.title,
                                    section.chapter.title,
                                    docsection.title,
                                    doctest_list,
                                    docsubsection.title,
                                )
                else:
                    # Section that is not under a Guide Section.
                    # The Tutorials Part works this way.
                    # DRY with above
                    yield section.get_tests()
                pass
            pass
        return


def sorted_chapters(chapters: List[DocChapter]) -> List[DocChapter]:
    """Return chapters sorted by title"""
    return sorted(chapters, key=lambda chapter: chapter.title)


class DocPart:
    """
    Class to gather Part data and its sub-parts (chapters) and format that.
    """

    def __init__(self, doc, title, is_reference=False):
        self.doc = doc
        self.title = title
        self.chapters = []
        self.chapters_by_slug = {}
        self.chapter_class = DocChapter
        self.is_reference = is_reference
        self.is_appendix = False
        self.slug = slugify(title)
        doc.parts_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("DEBUG Creating Part", title)

    def __str__(self) -> str:
        return f"{self.title}\n\n" + "\n".join(
            str(chapter) for chapter in sorted_chapters(self.chapters)
        )


class DocTests:
    """
    Object to hold a sequence of related DocTest objects for a section or
    subsection.
    Access ``tests`` to get these.
    """

    def __init__(self):
        self._tests = []
        self.text = ""

    @property
    def tests(self) -> list:
        """
        Retrieves test items of this DocTests object.
        """
        return self._tests

    # Deprecate
    def get_tests(self):
        """
        Older form of ``.tests`` attribute. Don't use.
        """
        logging.warn("get_tests is deprecated")
        return self._tests

    def is_private(self) -> bool:
        return all(test.private for test in self.tests)

    def __str__(self) -> str:
        return "\n".join(str(test) for test in self.tests)

    def test_indices(self) -> List[int]:
        return [test.index for test in self.tests]


class DocSection:
    """An object for a Documented Section.
    A Section is part of a Chapter. It can contain subsections.
    """

    def __init__(
        self,
        chapter,
        title: str,
        text: str,
        operator,
        installed=True,
        in_guide=False,
        summary_text="",
    ):
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.items = []  # tests in section
        self.operator = operator
        self.slug = slugify(title)
        self.subsections = []
        self.subsections_by_slug = {}
        self.summary_text = summary_text
        self.tests = None  # tests in section when not under a guide section
        self.title = title

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )

        # Needs to come after self.chapter is initialized since
        # XMLDoc uses self.chapter.
        self.xml_doc = XMLDoc(text, title, self)

        chapter.sections_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("      DEBUG Creating Section", title)

    # Add __eq__ and __lt__ so we can sort Sections.
    def __eq__(self, other) -> bool:
        return self.title == other.title

    def __lt__(self, other) -> bool:
        return self.title < other.title

    def __str__(self) -> str:
        return f"== {self.title} ==\n{self.chapter}"

    def get_tests(self) -> Iterator[Tests]:
        # FIXME: The below is a little weird for Guide Sections.
        # Figure out how to make this clearer.
        # A guide section's subsection are Sections without the Guide.
        # it is *their* subsections where we generally find tests.
        if self.in_guide:
            # FIXME section may have items, but not subsections.
            for section in self.subsections:
                if not section.installed:
                    continue
                if len(section.subsections) == 0 and len(section.items) > 0:
                    new_items = []
                    index = 1
                    for doctest in section.items:
                        if isinstance(doctest, DocTests):
                            # Why monkey patch DocTests?
                            # These attributes corresponds to a `Tests`
                            # object.
                            doctest_index = index
                            doctest_chapter = self.chapter.title
                            doctest_part = self.chapter.part.title
                            doctest_section = self.title
                            doctest_key = (
                                doctest_part,
                                doctest_chapter,
                                doctest_section,
                                index,
                            )
                            index += 1
                            new_items.append(doctest)
                            if len(new_items) > 0:
                                self.tests = Tests(
                                    doctest_part,
                                    doctest_chapter,
                                    doctest_section,
                                    new_items,
                                )
                                yield self.tests
                                1 / 0
                    return

                for subsection in section.subsections:
                    # FIXME we are omitting the section title here...
                    if not subsection.installed:
                        continue
                    for doctests in subsection.items:
                        yield doctests.get_tests()
                        pass
                    pass

            if len(self.items) > 0:
                self.tests = Tests(
                    doctest.part, doctest.chapter, doctest.section, self.items
                )
                yield self.tests
            pass

        elif self.tests is None:
            # Section that is not under a Guide Section.
            # The Tutorials Part works this way.
            # DRY with above
            assert len(self.items) == 0
            index = 1
            for doctest in self.xml_doc.get_tests():
                if isinstance(doctest, DocTest):
                    doctest.index = index
                    doctest.chapter = self.chapter.title
                    doctest.part = self.chapter.part.title
                    doctest.section = self.title
                    doctest.key = (
                        doctest.part,
                        doctest.chapter,
                        doctest.section,
                        index,
                    )
                    index += 1
                    self.items.append(doctest)
                    pass
                pass

            if len(self.items) > 0:
                self.tests = Tests(
                    doctest.part, doctest.chapter, doctest.section, self.items
                )
                yield self.tests
            pass
        else:
            assert False
            yield self.tests


# This stores a pointer to the Mathics3 Module portion of docs In interactive
# sessions, Mathics3 Modules get loaded on user demand. We need to update that
# portion of the documenation separately. Storing a pointer here allows us to
# retrive this portion
mathics3_module_part: Optional[DocPart] = None


# FIXME
# We hang "add_section",  off of Documenation when it would be better
# to hang it off of DocSection or DocChapter and then have to dogpaddle from a
# section or chapter up to the "doc" parent in order to find the routine.
# The irregularity of atutorial section currently prevents us from doing this
# When that is split out into a routine this is more possible.


class Documentation:
    def __init__(self):
        self.doc_class = XMLDoc
        self.doc_dir = settings.DOC_DIR
        self.chapter_class = DocChapter
        self.chapters: List[DocChapter] = []
        self.guide_section_class = DocGuideSection
        self.section_class = DocSection
        self.subsection_class = DocSubsection
        self.guide_sections: List[DocGuideSection] = []
        self.part_class = DocPart
        self.parts: list[DocPart] = []
        self.parts_by_slug = {}
        self.sections = []
        self.sections_by_slug = {}
        self.title = "Overview"

    def add_section(
        self,
        chapter,
        section_name: str,
        section_object,
        operator,
        is_guide: bool = False,
        in_guide: bool = False,
        summary_text="",
    ) -> Optional[DocSection]:
        """
        Adds a DocSection or DocGuideSection
        object to the chapter, a DocChapter object.
        "section_object" is either a Python module or a Class object instance.
        """
        installed = check_requires_list(getattr(section_object, "requires", []))

        # FIXME add an additional mechanism in the module
        # to allow a docstring and indicate it is not to go in the
        # user manual
        if not section_object.__doc__:
            return
        if is_guide:
            section = self.guide_section_class(
                chapter,
                section_name,
                section_object.__doc__,
                section_object,
                installed=installed,
            )
            chapter.guide_sections.append(section)
        else:
            section = self.section_class(
                chapter,
                section_name,
                section_object.__doc__,
                operator=operator,
                installed=installed,
                in_guide=in_guide,
                summary_text=summary_text,
            )
            chapter.sections.append(section)

        return section

    def add_subsection(
        self,
        chapter,
        section,
        subsection_name: str,
        instance,
        operator=None,
        in_guide=False,
    ):
        installed = check_requires_list(getattr(instance, "requires", []))

        # FIXME add an additional mechanism in the module
        # to allow a docstring and indicate it is not to go in the
        # user manual

        """
        Append a subsection for ``instance`` into ``section.subsections``
        """
        installed = True
        for package in getattr(instance, "requires", []):
            try:
                importlib.import_module(package)
            except ImportError:
                installed = False
                break

        # FIXME add an additional mechanism in the module
        # to allow a docstring and indicate it is not to go in the
        # user manual
        if not instance.__doc__:
            return
        summary_text = (
            instance.summary_text if hasattr(instance, "summary_text") else ""
        )
        subsection = self.subsection_class(
            chapter,
            section,
            subsection_name,
            instance.__doc__,
            operator=operator,
            installed=installed,
            in_guide=in_guide,
            summary_text=summary_text,
        )
        section.subsections.append(subsection)

    def doc_part(self, title, modules, builtins_by_module, start) -> DocPart:
        """
        Produce documentation and tests for a "Part". "Parts" are the highest-level division.
        Currently a Part is either:
          * Tutorial, or a
          * Reference, or a
          * Mathics3 Module, or
          * License Information
        """

        builtin_part = self.part_class(self, title, is_reference=start)
        modules_seen = set([])
        submodule_names_seen = set([])

        def module_collection_fn(modules):
            """Sort function for modules"""
            return sorted(
                modules,
                key=lambda module: module.sort_order
                if hasattr(module, "sort_order")
                else module.__name__,
            )

        for module in module_collection_fn(modules):
            if skip_module_doc(module, modules_seen):
                continue

            title, _ = get_module_doc(module)
            chapter = self.chapter_class(builtin_part, title, self)
            self.chapters.append(chapter)
            chapter.doc_chapter(
                module,
                builtin_part,
                builtins_by_module,
                modules_seen,
                submodule_names_seen,
            )
        self.parts.append(builtin_part)
        return builtin_part

    def doc_sections(self, sections, modules_seen, chapter):
        for instance in sections:
            if instance not in modules_seen and (
                not hasattr(instance, "no_doc") or not instance.no_doc
            ):
                name = instance.get_name(short=True)
                summary_text = (
                    instance.summary_text if hasattr(instance, "summary_text") else ""
                )
                self.add_section(
                    chapter,
                    name,
                    instance,
                    instance.get_operator(),
                    is_guide=False,
                    in_guide=False,
                    summary_text=summary_text,
                )
                modules_seen.add(instance)

    def gather_doctest_data(self):
        """
        Extract doctest data from various static XML-like doc files, Mathics3 Built-in functions
        (inside mathics.builtin), and external Mathics3 Modules.

        The extracted structure is stored in ``self``.
        """

        # First gather data from static XML-like files. This constitutes "Part 1" of the
        # documentation.
        files = listdir(self.doc_dir)
        files.sort()
        appendix = []

        for file in files:
            part_title = file[2:]
            if part_title.endswith(".mdoc"):
                part_title = part_title[: -len(".mdoc")]
                part = self.part_class(self, part_title)
                text = open(osp.join(self.doc_dir, file), "rb").read().decode("utf8")
                text = filter_comments(text)
                chapters = CHAPTER_RE.findall(text)
                for title, text in chapters:
                    chapter = self.chapter_class(part, title, self)
                    self.chapters.append(chapter)
                    text += '<section title=""></section>'
                    sections = SECTION_RE.findall(text)
                    for _, title, text in sections:
                        if title:
                            section = self.section_class(
                                chapter, title, text, operator=None, installed=True
                            )
                            chapter.sections.append(section)
                            subsections = SUBSECTION_RE.findall(text)
                            for subsection_title in subsections:
                                subsection = self.subsection_class(
                                    chapter,
                                    section,
                                    subsection_title,
                                    text,
                                )
                                section.subsections.append(subsection)
                                pass
                            pass
                        else:
                            section = None
                        pass

                    part.chapters.append(chapter)
                if file[0].isdigit():
                    self.parts.append(part)
                else:
                    part.is_appendix = True
                    appendix.append(part)
                pass
            pass

        # Next extract data that has been loaded into Mathics3 when it runs.
        # This is information from  `mathics.builtin`.
        # This is Part 2 of the documentation.

        self.doc_part(
            "Reference of Built-in Symbols",
            mathics3_builtins_modules,
            global_builtins_by_module,
            True,
        )

        # Now extract external Mathics3 Modules that have been loaded via
        # LoadModule, or eval_LoadModule.  This is Part 3 of the documentation.

        global mathics3_module_part
        mathics3_module_part = self.doc_part(
            "Mathics3 Modules", pymathics_modules, pymathics_builtins_by_module, True
        )

        # Now extract Appendix information. This include License text.  This is
        # the final Part of the documentation.

        for part in appendix:
            self.parts.append(part)

        return

    def get_part(self, part_slug):
        return self.parts_by_slug.get(part_slug)

    def get_chapter(self, part_slug, chapter_slug):
        part = self.parts_by_slug.get(part_slug)
        if part:
            return part.chapters_by_slug.get(chapter_slug)
        return None

    def get_section(self, part_slug, chapter_slug, section_slug):
        part = self.parts_by_slug.get(part_slug)
        if part:
            chapter = part.chapters_by_slug.get(chapter_slug)
            if chapter:
                return chapter.sections_by_slug.get(section_slug)
        return None

    def get_subsection(self, part_slug, chapter_slug, section_slug, subsection_slug):
        part = self.parts_by_slug.get(part_slug)
        if part:
            chapter = part.chapters_by_slug.get(chapter_slug)
            if chapter:
                section = chapter.sections_by_slug.get(section_slug)
                if section:
                    return section.subsections_by_slug.get(subsection_slug)

        return None


class DocGuideSection(DocSection):
    """An object for a Documented Guide Section.
    A Guide Section is part of a Chapter. "Colors" or "Special Functions"
    are examples of Guide Sections, and each contains a number of Sections.
    like NamedColors or Orthogonal Polynomials.
    """

    def __init__(
        self,
        chapter: DocChapter,
        title: str,
        text: str,
        submodule,
        installed: bool = True,
    ):
        self.chapter = chapter
        self.xml_doc = XMLDoc(text, title, self)
        self.in_guide = False
        self.installed = installed
        self.section = submodule
        self.slug = slugify(title)
        self.subsections = []
        self.subsections_by_slug = {}
        self.title = title

        # FIXME: Sections never are operators. Subsections can have
        # operators though.  Fix up the view and searching code not to
        # look for the operator field of a section.
        self.operator = False

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )
        if MATHICS_DEBUG_DOC_BUILD:
            print("    DEBUG Creating Guide Section", title)
        chapter.sections_by_slug[self.slug] = self


class DocSubsection:
    """An object for a Documented Subsection.
    A Subsection is part of a Section.
    """

    def __init__(
        self,
        chapter,
        section,
        title,
        text,
        operator=None,
        installed=True,
        in_guide=False,
        summary_text="",
    ):
        """
        Information that goes into a subsection object. This can be a written text, or
        text extracted from the docstring of a builtin module or class.

        About some of the parameters...

        Some subsections are contained in a grouping module and need special work to
        get the grouping module name correct.

        For example the Chapter "Colors" is a module so the docstring text for it is in
        mathics/builtin/colors/__init__.py . In mathics/builtin/colors/named-colors.py we have
        the "section" name for the class Read (the subsection) inside it.
        """

        title_summary_text = re.split(" -- ", title)
        n = len(title_summary_text)
        self.title = title_summary_text[0] if n > 0 else ""
        self.summary_text = title_summary_text[1] if n > 1 else summary_text

        self.doc = XMLDoc(text, title, section)
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.operator = operator

        self.section = section
        self.slug = slugify(title)
        self.subsections = []
        self.title = title

        if section:
            chapter = section.chapter
            part = chapter.part
            if section.title != chapter.title:
                key_prefix = (part.title, chapter.title, section.title, title)
            else:
                key_prefix = (part.title, chapter.title, title)

        else:
            key_prefix = None

        if in_guide:
            # Tests haven't been picked out yet from the doc string yet.
            # Gather them here.
            self.items = gather_tests(text, DocTests, DocTest, DocText, key_prefix)
        else:
            self.items = []

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )
        self.section.subsections_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("          DEBUG Creating Subsection", title)

    def __str__(self):
        return f"=== {self.title} ===\n{self.doc}"


# FIXME: think about - do we need this? Or can we use DjangoMathicsDocumentation and
# LatTeXMathicsDocumentation only?
class MathicsMainDocumentation(Documentation):
    """
    This module is used for creating test data and saving it to a Python Pickle file
    and running tests that appear in the documentation (doctests).

    There are other classes DjangoMathicsDocumentation and LaTeXMathicsDocumentation
    that format the data accumulated here. In fact I think those can sort of serve
    instead of this.
    """

    def __init__(self):
        super().__init__()
        self.doctest_latex_pcl_path = settings.DOCTEST_LATEX_DATA_PCL
        self.pymathics_doc_loaded = False
        self.doc_data_file = settings.get_doctest_latex_data_path(
            should_be_readable=True
        )


class DocText:
    """
    Class to hold some (non-test) text.

    Some of the kinds of tags you may find here are showin in global ALLOWED_TAGS.
    Some text may be marked with surrounding "$" or "'".

    The code here however does not make use of any of the tagging.
    """

    def __init__(self, text):
        self.text = text
        self._tests = []

    def __str__(self) -> str:
        return self.text

    @property
    def tests(self) -> list:
        """
        Retrieves test items of this DocText object.
        For this kind of object, there are never any tsets.
        """
        return self._tests

    def is_private(self) -> bool:
        return False

    def test_indices(self) -> list:
        return []


class XMLDoc:
    """A class to hold our internal XML-like format data for test sections or subsections.
    Specialized classes like LaTeXDoc or and DjangoDoc provide methods for
    getting formatted output. For LaTeXDoc ``latex()`` is added while for
    DjangoDoc ``html()`` is added

    Mathics core also uses this in getting usage strings (`??`).
    """

    def __init__(
        self,
        doc_str: str,
        title: str,
        section: [DocSection],
        doctests_class=DocTests,
        doctest_class=DocTest,
        doctext_class=DocText,
    ):
        self.title = title
        chapter = section.chapter
        part = chapter.part
        # Note: we elide section.title
        key_prefix = (part.title, chapter.title, title)

        self.rawdoc = doc_str
        self.items = gather_tests(
            self.rawdoc, doctests_class, doctest_class, doctext_class, key_prefix
        )

    def __str__(self) -> str:
        return "\n".join(str(item) for item in self.items)

    def text(self) -> str:
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

    def get_tests(self) -> list:
        tests = []
        for item in self.items:
            tests.extend(item.tests)
        return tests
