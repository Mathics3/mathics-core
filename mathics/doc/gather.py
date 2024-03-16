# -*- coding: utf-8 -*-
"""
Gather module information

Functions used to build the reference sections from module information. 

"""


import os.path as osp
import pkgutil
from os import listdir
from types import ModuleType
from typing import Tuple


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
    modules_seen = set([])
    for module in sorted_modules(modules):
        if skip_module_doc(module, modules_seen):
            continue
        chapter = documentation.doc_chapter(module, reference_part, builtins_by_module)
        if chapter is None:
            continue
        reference_part.chapters.append(chapter)
    return reference_part


def gather_chapter(part, module, builtins_by_module):
    """Build a chapter from a "top-level" module"""
    pass


def new_gather_sections(chapter, module, builtins_by_module) -> list:
    """Build a list of DocSections from a "top-level" module"""
    pass


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
    definition and docs for the "Named Colors" Mathics Bultin
    Functions.
    """
    modpkgs = []
    if hasattr(obj, "__path__"):
        for importer, modname, ispkg in pkgutil.iter_modules(obj.__path__):
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


def skip_doc(cls) -> bool:
    """Returns True if we should skip cls in docstring extraction."""
    return cls.__name__.endswith("Box") or (hasattr(cls, "no_doc") and cls.no_doc)


def skip_module_doc(module, must_be_skipped) -> bool:
    """True if the module should not be included in the documentation"""
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
        key=lambda module: module.sort_order
        if hasattr(module, "sort_order")
        else module.__name__,
    )
