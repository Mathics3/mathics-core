"""
Compression & Archive Formats
"""

from mathics.core.builtin import Builtin, String
from mathics.core.evaluation import Evaluation
from mathics.eval.fileformats.compression import eval_ImportZIP

# See commit in __init__.py regarding the whacky way this gets called


class ImportZIP(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/format/ZIP.html</url>

    <dl>
      <dt>'Compress`ImportZIP[path]'
      <dd>Run zip for archive file $path$
    </dl>

    """

    context = "Compress`"
    summary_text = "import a ZIP file"

    def eval(self, path: String, evaluation: Evaluation):
        "Compress`ImportZIP[path_String]"
        return eval_ImportZIP(path, evaluation)

    def eval_with_elements(self, path: String, elements, evaluation: Evaluation):
        "Compress`ImportZIP[path_String, elements_]"
        return eval_ImportZIP(path, evaluation, elements)
