"""
JSON File Format

JSON importer (via Python's "json" module).
"""

from mathics.core.builtin import Builtin, String
from mathics.core.evaluation import Evaluation
from mathics.eval.fileformats.jsonformat import eval_JSONImport


class ImportJSON(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/format/JSON.html</url>

    <dl>
      <dt>'JSON`ImportJSON[path]'
      <dd>Read $path$ as JSON and convert that to its corresponding Mathics3 equivalent.
    </dl>

    """

    context = "JSON`"
    messages = {"dec": "Decoding Error at `1`"}
    summary_text = "import JSON file"

    def eval(self, path: String, evaluation: Evaluation):
        "JSON`ImportJSON[path_String]"
        return eval_JSONImport(path, evaluation)
