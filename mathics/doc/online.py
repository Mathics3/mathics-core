"""
Functions used in the inline (Information[]) help.

"""

import re
from typing import Optional

from mathics.core.atoms.associations import Association
from mathics.core.builtin import Builtin
from mathics.core.convert.python import association_from_dict
from mathics.core.definitions import Definitions
from mathics.core.symbols import Symbol
from mathics.doc.doc_entries import DocumentationEntry

URL_RE = re.compile(r"(?:[^<]*)<url>\s*:(.+?):\s*(.+?)\s*</url>", flags=re.DOTALL)
COMMON_DOCUMENT_KEYS: set[str] = {"SymPy", "NumPy"}


def get_builtin_class(name_str: str, definitions: Definitions) -> Optional[Builtin]:
    """
    If Symbol is a implemented as a builtin function,
    return the builtin class object for it.

    Parameters
    ----------
    name_str : str
        The fully-qualified string name we for the Builtin.
    definitions : Definitions
        definitions The evaluation object.

    Returns
    -------
    Buitin
        The Python Builtin function class implementing name_str, if it exists.

    """
    for builtin_group in (definitions.builtin, definitions.pymathics):
        if (bio := builtin_group.get(name_str)) is not None:
            return bio.builtin.__class__
    return None


# FIXME: This will get less regular-expression based and less hacky
# when the documentation is revised.
def get_builtin_documentation(builtin_class: Builtin) -> Optional[Association]:
    """
    Returns an Association of documentation links or None if we can't find any.
    Key: "Web" has a WMA reference.
    """
    docstr = builtin_class.__doc__
    links_association = {}
    if link_section := docstr[0 : docstr.find("<dl>")]:
        start_position = 0
        while matched := re.match(URL_RE, link_section[start_position:]):
            links_key = matched.group(1)
            url = matched.group(2)
            if links_key in ("WMA link", "WMA"):
                # Follow WMA naming convention for the key name.
                links_key = "Web"
            elif links_key not in COMMON_DOCUMENT_KEYS and url.startswith(
                "https://en.wikipedia.org"
            ):
                links_key = "Wiki"
            links_association[links_key] = url
            start_position = matched.end()
        pass
    if links_association:
        return association_from_dict(links_association)
    return None


def online_doc_string(
    symbol: Symbol, definitions: Definitions, is_long_form: bool
) -> str:
    """
    Returns a Python string with the documentation associated to a given symbol.
    """
    usagetext = ""
    try:
        definition = definitions.get_definition(symbol.name)
        ruleusage = definition.get_values_list("messages")
    except KeyError:
        ruleusage = []

    # First look at user definitions:
    for rulemsg in ruleusage:
        if rulemsg.pattern.expr.get_elements()[1].__str__() == '"usage"':
            usagetext = rulemsg.rhs.to_python(string_quotes=False)

    if not is_long_form and usagetext:
        return usagetext

    if builtin_class := get_builtin_class(symbol.name, definitions):
        docstr = builtin_class.__doc__
        title = builtin_class.__name__
        if docstr is None:
            return usagetext
        docstr = docstr[docstr.find("<dl>") : (docstr.find("</dl>") + 6)]
        usagetext = DocumentationEntry(docstr, title).text()
    return usagetext
