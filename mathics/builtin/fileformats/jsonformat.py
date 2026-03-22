# -*- coding: utf-8 -*-

"""
JSON

Basic implementation for an JSON importer.
"""

from mathics.core.builtin import Builtin
from mathics.core.expression import Evaluation
from mathics.eval.fileformats.jsonformat import eval_JSONImport


class JSONImport(Builtin):
    """
    ## <url>:native internal:</url>

    <dl>
      <dt>'JSON`Import`JSONImport["file"]'
      <dd>parses "string" as a JSON file, and returns the data as a nested \
          list of rules.
    </dl>

    """

    summary_text = "import elements from json"
    context = "JSON`Import`"
    messages = {"dec": "Decoding Error at `1`"}

    def eval(self, filename, evaluation: Evaluation):
        """%(name)s[filename_String]"""
        return eval_JSONImport(filename.value, evaluation)
