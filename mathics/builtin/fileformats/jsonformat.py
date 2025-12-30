# -*- coding: utf-8 -*-

"""
JSON

Basic implementation for an JSON importer.
"""

import json

from mathics.core.atoms import String
from mathics.core.builtin import Builtin
from mathics.core.convert.python import from_python
from mathics.core.expression import Evaluation


class JSONImport(Builtin):
    """
    ## <url>:native internal:</url>

    <dl>
      <dt>'JSON`Import`JSONImport["file"]'
      <dd>parses "string" as a JSON file, and returns the data as a nested
          list of rules.
    </dl>

    """

    summary_text = "import elements from json"
    context = "JSON`Import`"
    messages = {"dec": "Decoding Error at `1`"}

    def eval(self, filename, evaluation: Evaluation):
        """%(name)s[filename_String]"""
        source = filename.value
        with open(source, "r") as f:
            try:
                json_dict = json.load(f)
            except json.decoder.JSONDecodeError as exc:
                evaluation.message("JSON`Import`JSONImport", "dec", String(exc.msg))
                return None
        return from_python(json_dict)
