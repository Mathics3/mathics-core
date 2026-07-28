"""
WL File Format

WL and Mathics3 importer
"""

from mathics.core.builtin import Builtin, String
from mathics.core.evaluation import Evaluation
from mathics.eval.fileformats.wlformat import eval_WLImport


class ImportWL(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/format/WL.html</url>

    <dl>
      <dt>'WLDump`ImportWL[$path$]'
      <dd>Read $path$ as a Wolfram package and 'Get' it.
    </dl>

    """

    context = "WLDump`"
    summary_text = "import WL file"

    def eval(self, path: String, evaluation: Evaluation):
        "WLDump`ImportWL[path_String]"
        return eval_WLImport(path, evaluation)
