# -*- coding: utf-8 -*-
"""
Gather module information

Functions used to build the reference sections from module information. 

"""


import pkgutil
from types import ModuleType
from typing import Tuple


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
