"""
Compression & Archive Formats
"""

from mathics.core.builtin import Builtin, String
from mathics.core.evaluation import Evaluation
from mathics.eval.import_export.compression import eval_ImportZIP

# The builtin functions defined here are called normally in a somewhat convoluted
# (and non obvious) way:
# via Import[] which consults RegisterImport[] which is invoked by autoloading
# Format/xxx/Import.wl

# Furthermore, all we really do is just pass the call over to eval_Import...


class ImportZIP(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/format/ZIP.html</url>

    <dl>
      <dt>'ImportZIP[path]'
      <dd>Run zip for archive file $path$
    </dl>

    """

    summary_text = "import ZIP file"

    def eval(self, path: String, evaluation: Evaluation):
        "ImportZIP[path_String]"
        return eval_ImportZIP(path.value, evaluation)

    def eval_with_elements(self, path: String, elements, evaluation: Evaluation):
        "ImportZIP[path_String, elements_]"
        return eval_ImportZIP(path.value, evaluation, elements)
