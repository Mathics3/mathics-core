# -*- coding: utf-8 -*-
"""
Gather module information

Functions used to build the reference sections from module information.

"""

import os.path as osp
import pkgutil
from os import listdir
from types import ModuleType
from typing import Tuple, Union

from mathics.core.builtin import Builtin, check_requires_list
from mathics.core.load_builtin import submodules
from mathics.core.util import IS_PYPY
from mathics.doc.doc_entries import DocumentationEntry
from mathics.doc.structure import DocChapter, DocGuideSection, DocSection, DocSubsection


def check_installed(src: Union[ModuleType, Builtin]) -> bool:
    """Check if the required libraries"""
    required_libs = getattr(src, "requires", [])
    return check_requires_list(required_libs) if required_libs else True


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


def gather_docs_from_files(documentation, path):
    """
    Load documentation from files in path
    """
    # First gather data from static XML-like files. This constitutes "Part 1" of the
    # documentation.
    files = listdir(path)
    files.sort()

    chapter_order = 0
    for file in files:
        part_title = file[2:]
        if part_title.endswith(".mdoc"):
            part_title = part_title[: -len(".mdoc")]
            # If the filename start with a number, then is a main part. Otherwise
            # is an appendix.
            is_appendix = not file[0].isdigit()
            chapter_order = documentation.load_part_from_file(
                osp.join(path, file),
                part_title,
                chapter_order,
                is_appendix,
            )


def gather_reference_part(documentation, title, modules, builtins_by_module):
    """
    Build a part from a title, a list of modules and information
    of builtins by modules.
    """
    part_class = documentation.part_class
    reference_part = part_class(documentation, title, True)
    modules = filter_toplevel_modules(modules)
    for module in sorted_modules(modules):
        if skip_module_doc(module):
            continue
        chapter = doc_chapter(module, reference_part, builtins_by_module)
        if chapter is None:
            continue
        # reference_part.chapters.append(chapter)
    return reference_part


def doc_chapter(module, part, builtins_by_module):
    """
    Build documentation structure for a "Chapter" - reference section which
    might be a Mathics Module.
    """
    # TODO: reformulate me in a way that symbols are always translated to
    # sections, and guide sections do not contain subsections.
    documentation = part.documentation if part else None
    chapter_class = documentation.chapter_class if documentation else DocChapter
    doc_class = documentation.doc_class if documentation else DocumentationEntry
    title, text = get_module_doc(module)
    chapter = chapter_class(part, title, doc_class(text, title, None))
    part.chapters.append(chapter)

    assert len(chapter.sections) == 0

    #    visited = set(sec.title for sec in symbol_sections)
    # If the module is a package, add the guides and symbols from the submodules
    if module.__file__.endswith("__init__.py"):
        guide_sections, symbol_sections = gather_guides_and_sections(
            chapter, module, builtins_by_module
        )
        chapter.guide_sections.extend(guide_sections)

        for sec in symbol_sections:
            if sec.title in visited:
                print(sec.title, "already visited. Skipped.")
            else:
                visited.add(sec.title)
                chapter.sections.append(sec)
    else:
        symbol_sections = gather_sections(chapter, module, builtins_by_module)
        chapter.sections.extend(symbol_sections)

    return chapter


def gather_sections(chapter, module, builtins_by_module, section_class=None) -> list:
    """Build a list of DocSections from a "top-level" module"""
    symbol_sections = []
    if skip_module_doc(module):
        return []

    part = chapter.part if chapter else None
    documentation = part.documentation if part else None
    if section_class is None:
        section_class = documentation.section_class if documentation else DocSection

    # TODO: Check the reason why for the module
    # `mathics.builtin.numbers.constants`
    # `builtins_by_module` has two copies of `Khinchin`.
    # By now,  we avoid the repetition by
    # converting the entries into `set`s.
    #
    visited = set()
    for symbol_instance in builtins_by_module.get(module.__name__, []):
        if skip_doc(symbol_instance, module):
            continue
        default_contexts = ("System`", "Pymathics`")
        title = symbol_instance.get_name(
            short=(symbol_instance.context in default_contexts)
        )
        if title in visited:
            continue
        visited.add(title)
        text = symbol_instance.__doc__
        operator = symbol_instance.get_operator()
        installed = check_installed(symbol_instance)
        summary_text = symbol_instance.summary_text
        section = section_class(
            chapter,
            title,
            text,
            operator,
            installed,
            summary_text=summary_text,
        )
        assert (
            section not in symbol_sections
        ), f"{section.title} already in {module.__name__}"
        symbol_sections.append(section)

    return symbol_sections


def gather_subsections(chapter, section, module, builtins_by_module) -> list:
    """Build a list of DocSubsections from a "top-level" module"""

    part = chapter.part if chapter else None
    documentation = part.documentation if part else None
    section_class = documentation.subsection_class if documentation else DocSubsection

    def section_function(
        chapter,
        title,
        text,
        operator=None,
        installed=True,
        in_guide=False,
        summary_text="",
    ):
        return section_class(
            chapter, section, title, text, operator, installed, in_guide, summary_text
        )

    return gather_sections(chapter, module, builtins_by_module, section_function)


def gather_guides_and_sections(chapter, module, builtins_by_module):
    """
    Look at the submodules in module, and produce the guide sections
    and sections.
    """
    guide_sections = []
    symbol_sections = []
    if skip_module_doc(module):
        return guide_sections, symbol_sections

    if not module.__file__.endswith("__init__.py"):
        return guide_sections, symbol_sections

    # Determine the class for sections and guide sections
    part = chapter.part if chapter else None
    documentation = part.documentation if part else None
    guide_class = (
        documentation.guide_section_class if documentation else DocGuideSection
    )

    # Loop over submodules
    docpath = f"/doc/{chapter.part.slug}/{chapter.slug}/"

    for sub_module in sorted_modules(submodules(module)):
        if skip_module_doc(sub_module):
            continue

        title, text = get_module_doc(sub_module)
        installed = check_installed(sub_module)

        guide_section = guide_class(
            chapter=chapter,
            title=title,
            text=text,
            submodule=sub_module,
            installed=installed,
        )

        submodule_symbol_sections = gather_subsections(
            chapter, guide_section, sub_module, builtins_by_module
        )

        guide_section.subsections.extend(submodule_symbol_sections)
        guide_sections.append(guide_section)

        # TODO, handle recursively the submodules.
        # Here there I see two options:
        #  if sub_module.__file__.endswith("__init__.py"):
        #      (deeper_guide_sections,
        #       deeper_symbol_sections) = gather_guides_and_sections(chapter,
        #                                       sub_module, builtins_by_module)
        #      symbol_sections.extend(deeper_symbol_sections)
        #      guide_sections.extend(deeper_guide_sections)
    return guide_sections, []


def get_module_doc(module: ModuleType) -> Tuple[str, str]:
    """
    Determine the title and text associated to the documentation
    of a module.
    If the module has a module docstring, extract the information
    from it. If not, pick the title from the name of the module.
    """
    doc = module.__doc__
    if doc is not None:
        doc = doc.strip()
    if doc:
        title = doc.splitlines()[0]
        text = "\n".join(doc.splitlines()[1:])
    else:
        title = module.__name__
        for prefix in ("mathics.builtin.", "mathics.optional.", "pymathics."):
            if title.startswith(prefix):
                title = title[len(prefix) :]
        title = title.capitalize()
        text = ""
    return title, text


def get_submodule_names(obj) -> list:
    """Many builtins are organized into modules which, from a documentation
    standpoint, are like Mathematica Online Guide Docs.

    "List Functions", "Colors", or "Distance and Similarity Measures"
    are some examples Guide Documents group group various Builtin Functions,
    under submodules relate to that general classification.

    Here, we want to return a list of the Python modules under a "Guide Doc"
    module.

    As an example of a "Guide Doc" and its submodules, consider the
    module named mathics.builtin.colors. It collects code and documentation pertaining
    to the builtin functions that would be found in the Guide documentation for "Colors".

    The `mathics.builtin.colors` module has a submodule
    `mathics.builtin.colors.named_colors`.

    The builtin functions defined in `named_colors` then are those found in the
    "Named Colors" group of the "Colors" Guide Doc.

    So in this example then, in the list the modules returned for
    Python module `mathics.builtin.colors` would be the
    `mathics.builtin.colors.named_colors` module which contains the
    definition and docs for the "Named Colors" Mathics Builtin
    Functions.
    """
    modpkgs = []
    if hasattr(obj, "__path__"):
        for _, modname, __ in pkgutil.iter_modules(obj.__path__):
            modpkgs.append(modname)
        modpkgs.sort()
    return modpkgs


def get_doc_name_from_module(module) -> str:
    """
    Get the title associated to the module.
    If the module has a docstring, pick the name from
    its first line (the title). Otherwise, use the
    name of the module.
    """
    name = "???"
    if module.__doc__:
        lines = module.__doc__.strip()
        if not lines:
            name = module.__name__
        else:
            name = lines.split("\n")[0]
    return name


def skip_doc(instance, module="") -> bool:
    """Returns True if we should skip the docstring extraction."""
    if not isinstance(module, str):
        module = module.__name__ if module else ""

    if type(instance).__name__.endswith("Box"):
        return True
    if hasattr(instance, "no_doc") and instance.no_doc:
        return True

    # Just include the builtins defined in the module.
    if module:
        if module != instance.__class__.__module__:
            return True
    return False


def skip_module_doc(module, must_be_skipped=frozenset()) -> bool:
    """True if the module should not be included in the documentation"""
    if IS_PYPY and module.__name__ == "builtins":
        return True
    return (
        module.__doc__ is None
        or module in must_be_skipped
        or module.__name__.split(".")[0] not in ("mathics", "pymathics")
        or hasattr(module, "no_doc")
        and module.no_doc
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
