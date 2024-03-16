# -*- coding: utf-8 -*-
"""
Structural elements of Mathics Documentation

This module contains the classes representing the Mathics documentation structure.

"""
import logging
import os.path as osp
import re
from os import environ, listdir
from types import ModuleType
from typing import Iterator, List, Optional

from mathics import settings
from mathics.core.builtin import check_requires_list
from mathics.core.load_builtin import (
    builtins_by_module as global_builtins_by_module,
    mathics3_builtins_modules,
)
from mathics.core.util import IS_PYPY
from mathics.doc.doc_entries import DocumentationEntry, Tests, filter_comments
from mathics.doc.gather import (
    get_doc_name_from_module,
    get_module_doc,
    skip_doc,
    skip_module_doc,
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
        installed: bool = True,
        in_guide: bool = False,
        summary_text: str = "",
    ):
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.items = []  # tests in section when this is under a guide section
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
        # DocumentationEntry uses self.chapter.
        # Notice that we need the documentation object, to have access
        # to the suitable subclass of DocumentationElement.
        documentation = self.chapter.part.doc
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

    @property
    def parent(self):
        return self.chapter

    @parent.setter
    def parent(self, value):
        raise TypeError("parent is a read-only property")

    def get_tests(self):
        """yield tests"""
        if self.installed:
            for test in self.doc.get_tests():
                yield test

    @property
    def parent(self):
        return self.chapter

    @parent.setter
    def parent(self, value):
        raise TypeError("parent is a read-only property")


# DocChapter has to appear before DocGuideSection which uses it.
class DocChapter:
    """An object for a Documented Chapter.
    A Chapter is part of a Part[dChapter. It can contain (Guide or plain) Sections.
    """

    def __init__(self, part, title, doc=None, chapter_order: Optional[int] = None):
        self.chapter_order = chapter_order
        self.doc = doc
        self.guide_sections = []
        self.part = part
        self.title = title
        self.slug = slugify(title)
        self.sections = []
        self.sections_by_slug = {}
        self.sort_order = None
        if doc:
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
        return sorted(self.sections + self.guide_sections)

    @property
    def parent(self):
        return self.part

    @parent.setter
    def parent(self, value):
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

    # FIXME: turn into a @property tests?
    def get_tests(self):
        """
        Tests included in a Guide.
        """
        # FIXME: The below is a little weird for Guide Sections.
        # Figure out how to make this clearer.
        # A guide section's subsection are Sections without the Guide.
        # it is *their* subsections where we generally find tests.
        #
        # Currently, this is not called in docpipeline or in making
        # the LaTeX documentation.
        for section in self.subsections:
            if not section.installed:
                continue
            for subsection in section.subsections:
                # FIXME we are omitting the section title here...
                if not subsection.installed:
                    continue
                for doctests in subsection.items:
                    yield doctests.get_tests()


class DocPart:
    """
    Represents one of the main parts of the document. Parts
    can be loaded from a mdoc file, generated automatically from
    the docstrings of Builtin objects under `mathics.builtin`.
    """

    chapter_class = DocChapter

    def __init__(self, doc, title, is_reference=False):
        self.doc = doc
        self.title = title
        self.chapters = []
        self.chapters_by_slug = {}
        self.is_reference = is_reference
        self.is_appendix = False
        self.slug = slugify(title)
        doc.parts_by_slug[self.slug] = self
        if MATHICS_DEBUG_DOC_BUILD:
            print("DEBUG Creating Part", title)

    def __str__(self) -> str:
        return f"    Part    {self.title}\n\n" + "\n\n".join(
            str(chapter) for chapter in sorted_chapters(self.chapters)
        )


class Documentation:
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
                                           +-----0>Sections
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
        self.appendix = []
        self.doc_dir = doc_dir
        self.parts = []
        self.parts_by_slug = {}
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
            return

        else:
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

    def doc_part(self, title, modules, builtins_by_module, start):
        """
        Build documentation structure for a "Part" - Reference
        section or collection of Mathics3 Modules.
        """

        builtin_part = self.part_class(self, title, is_reference=start)

        # This is used to ensure that we pass just once over each module.
        # The algorithm we use to walk all the modules without repetitions
        # relies on this, which in my opinion is hard to test and susceptible
        # to errors. I guess we include it as a temporal fixing to handle
        # packages inside ``mathics.builtin``.
        modules_seen = set([])

        def filter_toplevel_modules(module_list):
            """
            Keep just the modules at the top level.
            """
            if len(module_list) == 0:
                return module_list

            modules_and_levels = sorted(
                ((module.__name__.count("."), module) for module in module_list),
                key=lambda x: x[0],
            )
            top_level = modules_and_levels[0][0]
            return (entry[1] for entry in modules_and_levels if entry[0] == top_level)

        # The loop to load chapters must be run over the top-level modules. Otherwise,
        # modules like ``mathics.builtin.functional.apply_fns_to_lists`` are loaded
        # as chapters and sections of a GuideSection, producing duplicated tests.
        #
        # Also, this provides a more deterministic way to walk the module hierarchy,
        # which can be decomposed in the way proposed in #984.

        modules = filter_toplevel_modules(modules)
        for module in sorted_modules(modules):
            if skip_module_doc(module, modules_seen):
                continue
            chapter = self.doc_chapter(module, builtin_part, builtins_by_module)
            if chapter is None:
                continue
            builtin_part.chapters.append(chapter)

        self.parts.append(builtin_part)

    def doc_chapter(self, module, part, builtins_by_module) -> Optional[DocChapter]:
        """
        Build documentation structure for a "Chapter" - reference section which
        might be a Mathics Module.
        """
        modules_seen = set([])

        title, text = get_module_doc(module)
        chapter = self.chapter_class(part, title, self.doc_class(text, title, None))
        builtins = builtins_by_module.get(module.__name__)
        if module.__file__.endswith("__init__.py"):
            # We have a Guide Section.

            # This is used to check if a symbol is not duplicated inside
            # a guide.
            submodule_names_seen = set([])
            name = get_doc_name_from_module(module)
            guide_section = self.add_section(
                chapter, name, module, operator=None, is_guide=True
            )
            submodules = [
                value
                for value in module.__dict__.values()
                if isinstance(value, ModuleType)
            ]

            # Add sections in the guide section...
            for submodule in sorted_modules(submodules):
                if skip_module_doc(submodule, modules_seen):
                    continue
                elif IS_PYPY and submodule.__name__ == "builtins":
                    # PyPy seems to add this module on its own,
                    # but it is not something that can be importable
                    continue

                submodule_name = get_doc_name_from_module(submodule)
                if submodule_name in submodule_names_seen:
                    continue
                section = self.add_section(
                    chapter,
                    submodule_name,
                    submodule,
                    operator=None,
                    is_guide=False,
                    in_guide=True,
                )
                modules_seen.add(submodule)
                submodule_names_seen.add(submodule_name)
                guide_section.subsections.append(section)

                builtins = builtins_by_module.get(submodule.__name__, [])
                subsections = list(builtins)
                for instance in subsections:
                    if hasattr(instance, "no_doc") and instance.no_doc:
                        continue

                    name = instance.get_name(short=True)
                    if name in submodule_names_seen:
                        continue

                    submodule_names_seen.add(name)
                    modules_seen.add(instance)

                    self.add_subsection(
                        chapter,
                        section,
                        name,
                        instance,
                        instance.get_operator(),
                        in_guide=True,
                    )
        else:
            if not builtins:
                return None
            sections = [
                builtin for builtin in builtins if not skip_doc(builtin.__class__)
            ]
            self.doc_sections(sections, modules_seen, chapter)
        return chapter

    def doc_sections(self, sections, modules_seen, chapter):
        """
        Load sections from a list of mathics builtins.
        """

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

    def get_part(self, part_slug):
        """return a section from part key"""
        return self.parts_by_slug.get(part_slug)

    def get_chapter(self, part_slug, chapter_slug):
        """return a section from part and chapter keys"""
        part = self.parts_by_slug.get(part_slug)
        if part:
            return part.chapters_by_slug.get(chapter_slug)
        return None

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

                tests = chapter.doc.get_tests()
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
                                        doctest_list += list(doctests.get_tests())
                                        for test in doctest_list:
                                            test.index = index
                                            index += 1

                                    if doctest_list:
                                        yield Tests(
                                            section.chapter.part.title,
                                            section.chapter.title,
                                            docsubsection.title,
                                            doctest_list,
                                        )
                        else:
                            tests = section.doc.get_tests()
                            if tests:
                                yield Tests(
                                    part.title,
                                    chapter.title,
                                    section.title,
                                    tests,
                                )
        return

    def load_documentation_sources(self):
        """
        Extract doctest data from various static XML-like doc files, Mathics3 Built-in functions
        (inside mathics.builtin), and external Mathics3 Modules.

        The extracted structure is stored in ``self``.
        """
        assert (
            len(self.parts) == 0
        ), "The documentation must be empty to call this function."

        # First gather data from static XML-like files. This constitutes "Part 1" of the
        # documentation.
        files = listdir(self.doc_dir)
        files.sort()

        chapter_order = 0
        for file in files:
            part_title = file[2:]
            if part_title.endswith(".mdoc"):
                part_title = part_title[: -len(".mdoc")]
                # If the filename start with a number, then is a main part. Otherwise
                # is an appendix.
                is_appendix = not file[0].isdigit()
                chapter_order = self.load_part_from_file(
                    osp.join(self.doc_dir, file),
                    part_title,
                    chapter_order,
                    is_appendix,
                )

        # Next extract data that has been loaded into Mathics3 when it runs.
        # This is information from  `mathics.builtin`.
        # This is Part 2 of the documentation.

        # Notice that in order to generate the documentation
        # from the builtin classes, it is needed to call first to
        #    import_and_load_builtins()

        for title, modules, builtins_by_module, start in [
            (
                "Reference of Built-in Symbols",
                mathics3_builtins_modules,
                global_builtins_by_module,
                True,
            )
        ]:
            self.doc_part(title, modules, builtins_by_module, start)

        # Next extract external Mathics3 Modules that have been loaded via
        # LoadModule, or eval_LoadModule.  This is Part 3 of the documentation.

        self.doc_part(
            MATHICS3_MODULES_TITLE,
            pymathics_modules,
            pymathics_builtins_by_module,
            True,
        )

        # Finally, extract Appendix information. This include License text
        # This is the final Part of the documentation.

        for part in self.appendix:
            self.parts.append(part)

        return

    def load_part_from_file(
        self,
        filename: str,
        title: str,
        chapter_order: int,
        is_appendix: bool = False,
    ) -> int:
        """Load a markdown file as a part of the documentation"""
        part = self.part_class(self, title)
        text = open(filename, "rb").read().decode("utf8")
        text = filter_comments(text)
        chapters = CHAPTER_RE.findall(text)
        for title, text in chapters:
            chapter = self.chapter_class(part, title, chapter_order=chapter_order)
            chapter_order += 1
            text += '<section title=""></section>'
            section_texts = SECTION_RE.findall(text)
            for pre_text, title, text in section_texts:
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
            self.parts.append(part)
        return chapter_order


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
        the "section" name for the class Red (the subsection) inside it.
        """
        title_summary_text = re.split(" -- ", title)
        n = len(title_summary_text)
        # We need the documentation object, to have access
        # to the suitable subclass of DocumentationElement.
        documentation = chapter.part.doc

        self.title = title_summary_text[0] if n > 0 else ""
        self.summary_text = title_summary_text[1] if n > 1 else summary_text
        self.doc = documentation.doc_class(text, title, None)
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.operator = operator

        self.section = section
        self.slug = slugify(title)
        self.subsections = []
        self.title = title
        self.doc.set_parent_path(self)

        # This smells wrong: Here a DocSection (a level in the documentation system)
        # is mixed with a DocumentationEntry. `items` is an attribute of the
        # `DocumentationEntry`, not of a Part / Chapter/ Section.
        # The content of a subsection should be stored in self.doc,
        # and the tests should set the rute (key) through self.doc.set_parent_doc
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

    @property
    def parent(self):
        return self.section

    @parent.setter
    def parent(self, value):
        raise TypeError("parent is a read-only property")

    def get_tests(self):
        """yield tests"""
        if self.installed:
            for test in self.doc.get_tests():
                yield test


class MathicsMainDocumentation(Documentation):
    """
    MathicsMainDocumentation specializes ``Documentation`` by providing the attributes
    and methods needed to generate the documentation from the Mathics library.

    The parts of the documentation are loaded from the Markdown files contained
    in the path specified by ``self.doc_dir``. Files with names starting in numbers
    are considered parts of the main text, while those that starts with other characters
    are considered as appendix parts.

    In addition to the parts loaded from markdown files, a ``Reference of Builtin-Symbols`` part
    and a part for the loaded Pymathics modules are automatically generated.

    In the ``Reference of Built-in Symbols`` tom-level modules and files in ``mathics.builtin``
    are associated to Chapters. For single file submodules (like ``mathics.builtin.procedure``)
    The chapter contains a Section for each Symbol in the module. For sub-packages
    (like ``mathics.builtin.arithmetic``) sections are given by the sub-module files,
    and the symbols in these sub-packages defines the Subsections. ``__init__.py`` in
    subpackages are associated to GuideSections.

    In a similar way, in the ``Pymathics`` part, each ``pymathics`` module defines a Chapter,
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
        Populates the documentatation.
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
        key=lambda chapter: str(chapter.sort_order)
        if chapter.sort_order is not None
        else chapter.title,
    )


def sorted_modules(modules) -> list:
    """Return modules sorted by the ``sort_order`` attribute if that
    exists, or the module's name if not."""
    return sorted(
        modules,
        key=lambda module: module.sort_order
        if hasattr(module, "sort_order")
        else module.__name__,
    )
