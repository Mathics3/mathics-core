# -*- coding: utf-8 -*-
"""
Structural elements of Mathics Documentation

This module contains the classes representing the Mathics documentation structure,
and extended regular expressions used to parse it.

"""
import logging
import re
from os import environ
from typing import Dict, Iterator, List, Optional, Sequence

from mathics import settings
from mathics.core.builtin import check_requires_list
from mathics.core.load_builtin import (
    builtins_by_module as global_builtins_by_module,
    mathics3_builtins_modules,
)
from mathics.doc.doc_entries import (
    BaseDocElement,
    DocTest,
    DocumentationEntry,
    Tests,
    filter_comments,
)
from mathics.doc.utils import slugify
from mathics.eval.pymathics import pymathics_builtins_by_module, pymathics_modules

CHAPTER_RE = re.compile('(?s)<chapter title="(.*?)">(.*?)</chapter>')
SECTION_RE = re.compile('(?s)(.*?)<section title="(.*?)">(.*?)</section>')
SUBSECTION_RE = re.compile('(?s)<subsection title="(.*?)">')
SUBSECTION_END_RE = re.compile("</subsection>")

# Debug flags.

# Set to True if want to follow the process
# The first phase is building the documentation data structure
# based on docstrings:

MATHICS_DEBUG_DOC_BUILD: bool = "MATHICS_DEBUG_DOC_BUILD" in environ

# After building the doc structure, we extract test cases.
MATHICS_DEBUG_TEST_CREATE: bool = "MATHICS_DEBUG_TEST_CREATE" in environ

# Name of the Mathics3 Module part of the document.
MATHICS3_MODULES_TITLE = "Mathics3 Modules"


# DocSection has to appear before DocGuideSection which uses it.
class DocSection(BaseDocElement):
    """An object for a Documented Section.
    A Section is part of a Chapter. It can contain subsections.
    """

    def __init__(
        self,
        chapter: "DocChapter",
        title: str,
        text: str,
        operator,
        installed: bool = True,
        in_guide: bool = False,
        summary_text: str = "",
    ):
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        # tests in section when this is under a guide section
        self.items: List[DocTest] = []
        self.operator = operator
        self.slug = slugify(title)
        self.subsections: Sequence[DocSubsection] = []
        self.subsections_by_slug: Dict[str, DocSubsection] = {}
        self.summary_text = summary_text
        self.tests = None  # tests in section when not under a guide section
        self.title = title

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )

        # Needs to come after self.chapter is initialized since
        # DocumentationEntry uses self.chapter.
        # Notice that we need the documentation object, to have access
        # to the suitable subclass of DocumentationElement.
        documentation = self.chapter.part.documentation
        self.doc = documentation.doc_class(text, title, None).set_parent_path(self)

        chapter.sections_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("      DEBUG Creating Section", title)

    # Add __eq__ and __lt__ so we can sort Sections.
    def __eq__(self, other) -> bool:
        return self.title == other.title

    def __lt__(self, other) -> bool:
        return self.title < other.title

    def __str__(self) -> str:
        return f"    == {self.title} ==\n{self.doc}"

    def get_children(self) -> list:
        """Get children"""
        return list(self.subsections)

    def get_tests(self):
        """yield tests"""
        if self.installed:
            for test in self.doc.get_tests():
                yield test

    @property
    def parent(self):
        "the container where the section is"
        return self.chapter

    @parent.setter
    def parent(self, value):
        "the container where the section is"
        raise TypeError("parent is a read-only property")


# DocChapter has to appear before DocGuideSection which uses it.
class DocChapter(BaseDocElement):
    """An object for a Documented Chapter.
    A Chapter is part of a Part[dChapter. It can contain (Guide or plain) Sections.
    """

    def __init__(
        self,
        part: "DocPart",
        title: str,
        doc: Optional["DocumentationEntry"] = None,
        chapter_order: Optional[int] = None,
    ):
        self.chapter_order = chapter_order
        self.doc = doc
        self.guide_sections: Sequence[DocGuideSection] = []
        self.part = part
        self.title = title
        self.slug = slugify(title)
        self.sections: List[DocSection] = []
        self.sections_by_slug: Dict[str, DocSection] = {}
        self.sort_order = None
        if self.doc:
            self.doc.set_parent_path(self)

        part.chapters_by_slug[self.slug] = self

        if MATHICS_DEBUG_DOC_BUILD:
            print("  DEBUG Creating Chapter", title)

    def __str__(self) -> str:
        """
        A DocChapter is represented as the index of its sections
        and subsections.
        """
        sections_descr = ""
        for section in self.all_sections:
            sec_class = "@>" if isinstance(section, DocGuideSection) else "@ "
            sections_descr += f"     {sec_class} " + section.title + "\n"
            for subsection in section.subsections:
                sections_descr += "         * " + subsection.title + "\n"

        return f"   = {self.part.title}: {self.title} =\n\n{sections_descr}"

    @property
    def all_sections(self):
        "guides and normal sections"
        return sorted(self.guide_sections) + sorted(self.sections)

    def get_children(self) -> list:
        """Get children"""
        return self.all_sections

    @property
    def parent(self):
        "the container where the chapter is"
        return self.part

    @parent.setter
    def parent(self, value):
        "the container where the chapter is"
        raise TypeError("parent is a read-only property")


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
        super().__init__(chapter, title, text, None, installed, False)
        self.section = submodule

        if MATHICS_DEBUG_DOC_BUILD:
            print("    DEBUG Creating Guide Section", title)


class DocPart(BaseDocElement):
    """
    Represents one of the main parts of the document. Parts
    can be loaded from a mdoc file, generated automatically from
    the docstrings of Builtin objects under `mathics.builtin`.
    """

    chapter_class = DocChapter

    def __init__(self, documentation: "Documentation", title: str, is_reference=False):
        self.documentation = documentation
        self.title = title
        self.chapters: List[DocChapter] = []
        self.chapters_by_slug: Dict[str, DocChapter] = {}
        self.is_reference = is_reference
        self.is_appendix = False
        self.slug = slugify(title)
        documentation.parts_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("DEBUG Creating Part", title)

    def __str__(self) -> str:
        return f"    Part    {self.title}\n\n" + "\n\n".join(
            str(chapter) for chapter in sorted_chapters(self.chapters)
        )

    def get_children(self) -> list:
        """Get children"""
        return self.chapters

    @property
    def parent(self):
        "the container where the element is"
        return self.documentation

    @parent.setter
    def parent(self, value):
        "the container where the section is"
        raise TypeError("parent is a read-only property")


class Documentation(BaseDocElement):
    """
    `Documentation` describes an object containing the whole documentation system.
    Documentation
        |
        +--------0> Parts
                      |
                      +-----0> Chapters
                                 |
                                 +-----0>Sections
                                 |         |
                                 |         +------0> SubSections
                                 |
                                 +---->0>GuideSections
                                           |
                                           +------0> SubSections

    (with 0>) meaning "aggregation".

    Each element contains a title, a collection of elements of the following class
    in the hierarchy. Parts, Chapters, Guide Sections, Sections and SubSections contains a doc
    attribute describing the content to be shown after the title, and before
    the elements of the subsequent terms in the hierarchy.
    """

    def __init__(self, title: str = "Title", doc_dir: str = ""):
        """
        Parameters
        ----------
        title : str, optional
            The title of the Documentation. The default is "Title".
        doc_dir : str, optional
            The path where the sources can be loaded. The default is "",
            meaning that no sources must be loaded.
        """
        # This is a way to load the default classes
        # without defining these attributes as class
        # attributes.
        self._set_classes()
        self.appendix: List[DocPart] = []
        self.doc_dir = doc_dir
        self.parts: Sequence[DocPart] = []
        self.parts_by_slug: Dict[str, DocPart] = {}
        self.title = title

    def _set_classes(self):
        """
        Set the classes of the subelements. Must be overloaded
        by the subclasses.
        """
        if not hasattr(self, "part_class"):
            self.chapter_class = DocChapter
            self.doc_class = DocumentationEntry
            self.guide_section_class = DocGuideSection
            self.part_class = DocPart
            self.section_class = DocSection
            self.subsection_class = DocSubsection

    def __str__(self):
        result = self.title + "\n" + len(self.title) * "~" + "\n"
        return (
            result + "\n\n".join([str(part) for part in self.parts]) + "\n" + 60 * "-"
        )

    def add_section(
        self,
        chapter,
        section_name: str,
        section_object,
        operator,
        is_guide: bool = False,
        in_guide: bool = False,
        summary_text="",
    ):
        """
        Adds a DocSection or DocGuideSection
        object to the chapter, a DocChapter object.
        "section_object" is either a Python module or a Class object instance.
        """
        if section_object is not None:
            required_libs = getattr(section_object, "requires", [])
            installed = check_requires_list(required_libs) if required_libs else True
            # FIXME add an additional mechanism in the module
            # to allow a docstring and indicate it is not to go in the
            # user manual
        if not section_object.__doc__:
            return None

        installed = True

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
        """
        Append a subsection for ``instance`` into ``section.subsections``
        """

        required_libs = getattr(instance, "requires", [])
        installed = check_requires_list(required_libs) if required_libs else True

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

    def doc_part(self, title, start):
        """
        Build documentation structure for a "Part" - Reference
        section or collection of Mathics3 Modules.
        """

        builtin_part = self.part_class(self, title, is_reference=start)
        self.parts.append(builtin_part)

    def get_children(self):
        return self.parts

    def get_chapter(self, part_slug, chapter_slug):
        """return a section from part and chapter keys"""
        part = self.parts_by_slug.get(part_slug)
        if part:
            return part.chapters_by_slug.get(chapter_slug)
        return None

    def get_part(self, part_slug):
        """return a section from part key"""
        return self.parts_by_slug.get(part_slug)

    def get_section(self, part_slug, chapter_slug, section_slug):
        """return a section from part, chapter and section keys"""
        part = self.parts_by_slug.get(part_slug)
        if part:
            chapter = part.chapters_by_slug.get(chapter_slug)
            if chapter:
                return chapter.sections_by_slug.get(section_slug)
        return None

    def get_subsection(self, part_slug, chapter_slug, section_slug, subsection_slug):
        """
        return a section from part, chapter, section and subsection
        keys
        """
        part = self.parts_by_slug.get(part_slug)
        if part:
            chapter = part.chapters_by_slug.get(chapter_slug)
            if chapter:
                section = chapter.sections_by_slug.get(section_slug)
                if section:
                    return section.subsections_by_slug.get(subsection_slug)

        return None

    # FIXME: turn into a @property tests?
    def get_tests(self) -> Iterator:
        """
        Returns a generator to extracts lists test objects.
        """
        for part in self.parts:
            for chapter in sorted_chapters(part.chapters):
                if MATHICS_DEBUG_TEST_CREATE:
                    print(f"DEBUG Gathering tests for Chapter {chapter.title}")

                tests = chapter.doc.get_tests() if chapter.doc else []
                if tests:
                    yield Tests(part.title, chapter.title, "", tests)

                for section in chapter.all_sections:
                    if section.installed:
                        if MATHICS_DEBUG_TEST_CREATE:
                            if isinstance(section, DocGuideSection):
                                print(
                                    f"DEBUG Gathering tests for   Guide Section {section.title}"
                                )
                            else:
                                print(
                                    f"DEBUG Gathering tests for      Section {section.title}"
                                )

                        tests = section.doc.get_tests()
                        if tests:
                            yield Tests(
                                part.title,
                                chapter.title,
                                section.title,
                                tests,
                            )

    def load_documentation_sources(self):
        """
        Extract doctest data from various static XML-like doc files, Mathics3 Built-in functions
        (inside mathics.builtin), and external Mathics3 Modules.

        The extracted structure is stored in ``self``.
        """
        from mathics.doc.gather import gather_docs_from_files, gather_reference_part

        assert (
            len(self.parts) == 0
        ), "The documentation must be empty to call this function."

        gather_docs_from_files(self, self.doc_dir)
        # Next extract data that has been loaded into Mathics3 when it runs.
        # This is information from  `mathics.builtin`.
        # This is Part 2 of the documentation.

        # Notice that in order to generate the documentation
        # from the builtin classes, it is needed to call first to
        #    import_and_load_builtins()

        for title, modules, builtins_by_module in [
            (
                "Reference of Built-in Symbols",
                mathics3_builtins_modules,
                global_builtins_by_module,
            ),
            (
                MATHICS3_MODULES_TITLE,
                pymathics_modules,
                pymathics_builtins_by_module,
            ),
        ]:
            self.parts.append(
                gather_reference_part(self, title, modules, builtins_by_module)
            )

        # Finally, extract Appendix information. This include License text
        # This is the final Part of the documentation.

        for part in self.appendix:
            self.parts.append(part)

    def load_part_from_file(
        self,
        filename: str,
        part_title: str,
        chapter_order: int,
        is_appendix: bool = False,
    ) -> int:
        """Load a document file (tagged XML-like in custom format) as
        a part of the documentation"""
        part = self.part_class(self, part_title)
        with open(filename, "rb") as src_file:
            text = src_file.read().decode("utf8")

        text = filter_comments(text)
        chapters = CHAPTER_RE.findall(text)
        for chapter_title, text in chapters:
            chapter = self.chapter_class(
                part, chapter_title, chapter_order=chapter_order
            )
            chapter_order += 1
            text += '<section title=""></section>'
            section_texts = SECTION_RE.findall(text)
            for pre_text, title, text in section_texts:
                if title:
                    section = self.section_class(
                        chapter, title, text, operator=None, installed=True
                    )
                    chapter.sections.append(section)
                    # Subsections are processed inside the Documentation entry.
                else:
                    section = None
                if not chapter.doc:
                    chapter.doc = self.doc_class(pre_text, title, section)
                pass

            part.chapters.append(chapter)
        if is_appendix:
            part.is_appendix = True
            self.appendix.append(part)
        else:
            assert isinstance(self.parts, list)
            self.parts.append(part)
        return chapter_order

    @property
    def parent(self):
        "the container where the element is"
        return None

    @parent.setter
    def parent(self, value):
        "the container where the section is"
        raise TypeError("parent is a read-only property")


class DocSubsection(BaseDocElement):
    """An object for a Documented Subsection.
    A Subsection is part of a Section.
    """

    def __init__(
        self,
        chapter: DocChapter,
        section: DocSection,
        title: str,
        text: str,
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
        the "section" name for the class Red (the subsection) inside it.
        """
        title_summary_text = re.split(" -- ", title)
        len_title = len(title_summary_text)
        # We need the documentation object, to have access
        # to the suitable subclass of DocumentationElement.
        documentation = chapter.part.documentation

        self.title = title_summary_text[0] if len_title > 0 else ""
        self.summary_text = title_summary_text[1] if len_title > 1 else summary_text
        self.doc = documentation.doc_class(text, title, None)
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.operator = operator

        self.section = section
        self.slug = slugify(title)
        self.subsections: Sequence[DocSubsection] = []
        self.title = title
        self.doc.set_parent_path(self)

        # This smells wrong: Here a DocSection (a level in the documentation system)
        # is mixed with a DocumentationEntry. `items` is an attribute of the
        # `DocumentationEntry`, not of a Part / Chapter/ Section.
        # The content of a subsection should be stored in self.doc,
        # and the tests should set the route (key) through self.doc.set_parent_doc
        if in_guide:
            # Tests haven't been picked out yet from the doc string yet.
            # Gather them here.
            self.items = self.doc.items

            for item in self.items:
                for test in item.get_tests():
                    assert test.key is not None
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

    def __str__(self) -> str:
        return f"=== {self.title} ===\n{self.doc}"

    def get_children(self) -> list:
        """Get children"""
        return list(self.subsections)

    def get_tests(self):
        """yield tests"""
        if self.installed:
            for test in self.doc.get_tests():
                yield test

    @property
    def parent(self):
        """the chapter where the section is"""
        return self.section

    @parent.setter
    def parent(self, value):
        "the container where the section is"
        raise TypeError("parent is a read-only property")


class MathicsMainDocumentation(Documentation):
    """MathicsMainDocumentation specializes ``Documentation`` by providing the attributes
    and methods needed to generate the documentation from the Mathics library.

    The parts of the documentation are loaded from the Markdown files contained
    in the path specified by ``self.doc_dir``. Files with names starting in numbers
    are considered parts of the main text, while those that starts with other characters
    are considered as appendix parts.

    In addition to the parts loaded from our custom-marked XML
    document file, a ``Reference of Builtin-Symbols`` part and a part
    for the loaded Pymathics modules are automatically generated.

    In the ``Reference of Built-in Symbols`` tom-level modules and files in ``mathics.builtin``
    are associated to Chapters. For single file submodules (like ``mathics.builtin.procedure``)
    The chapter contains a Section for each Symbol in the module. For sub-packages
    (like ``mathics.builtin.arithmetic``) sections are given by the sub-module files,
    and the symbols in these sub-packages defines the Subsections. ``__init__.py`` in
    subpackages are associated to GuideSections.

    In a similar way, in the ``Mathics3 Modules`` part, each ``Mathics3`` module defines a Chapter,
    files in the module defines Sections, and Symbols defines Subsections.


    ``MathicsMainDocumentation`` is also used for creating test data and saving it to a
    Python Pickle file and running tests that appear in the documentation (doctests).

    There are other classes DjangoMathicsDocumentation and LaTeXMathicsDocumentation
    that format the data accumulated here. In fact I think those can sort of serve
    instead of this.

    """

    def __init__(self):
        super().__init__(title="Mathics Main Documentation", doc_dir=settings.DOC_DIR)
        self.doctest_latex_pcl_path = settings.DOCTEST_LATEX_DATA_PCL
        self.pymathics_doc_loaded = False
        self.doc_data_file = settings.get_doctest_latex_data_path(
            should_be_readable=True
        )

    def gather_doctest_data(self):
        """
        Populates the documentation.
        (deprecated)
        """
        logging.warning(
            "gather_doctest_data is deprecated. Use load_documentation_sources"
        )
        return self.load_documentation_sources()


def sorted_chapters(chapters: List[DocChapter]) -> List[DocChapter]:
    """Return chapters sorted by title"""
    return sorted(
        chapters,
        key=lambda chapter: (
            str(chapter.sort_order) if chapter.sort_order is not None else chapter.title
        ),
    )


def sorted_modules(modules) -> list:
    """Return modules sorted by the ``sort_order`` attribute if that
    exists, or the module's name if not."""
    return sorted(
        modules,
        key=lambda module: (
            module.sort_order if hasattr(module, "sort_order") else module.__name__
        ),
    )
