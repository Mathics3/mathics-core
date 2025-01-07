"""
Functions used in the inline (Information[]) help. 

"""

import re

from mathics.core.evaluation import Evaluation
from mathics.core.symbols import Symbol
from mathics.doc.doc_entries import DocumentationEntry


def online_doc_string(
    symbol: Symbol, evaluation: Evaluation, is_long_form: bool
) -> str:
    """
    Returns a python string with the documentation associated to a given symbol.
    """
    definition = evaluation.definitions.get_definition(symbol.name)
    ruleusage = definition.get_values_list("messages")
    usagetext = ""

    # First look at user definitions:
    for rulemsg in ruleusage:
        if rulemsg.pattern.expr.elements[1].__str__() == '"usage"':
            usagetext = rulemsg.replace.value

    if not is_long_form and usagetext:
        return usagetext

    builtins = evaluation.definitions.builtin
    pymathics = evaluation.definitions.pymathics
    bio = pymathics.get(definition.name) or builtins.get(definition.name)

    if bio is not None:
        docstr = bio.builtin.__class__.__doc__
        title = bio.builtin.__class__.__name__
        if docstr is None:
            return usagetext
        docstr = docstr[docstr.find("<dl>") : (docstr.find("</dl>") + 6)]
        usagetext = DocumentationEntry(docstr, title).text()
    return usagetext
