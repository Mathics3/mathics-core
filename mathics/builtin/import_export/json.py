<<<<<<< HEAD
"""
JSON-Related Formats
"""

=======
>>>>>>> 5554cc9f0 (Split out Import/Export functions...)
from mathics.core.builtin import Builtin, String
from mathics.core.evaluation import Evaluation
from mathics.eval.import_export.json import eval_JSONImport

# The builtin functions defined here are called normally in a somewhat
# convoluted (and non obvious) way: via Import[] which consults
# RegisterImport[] which is invoked by autoloading
# Format/xxx/Import.wl

# Furthermore, all we really do is just pass the call over to
# eval_Import...


class ImportJSON(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/format/JSON.html</url>

    <dl>
      <dt>'ImportJSON[path]'
      <dd>Read $path$ as JSON and convert that to its corresponding Mathics3 equivalent.
    </dl>

    """

    summary_text = "import JSON file"

    def eval(self, path: String, evaluation: Evaluation):
        "ImportJSON[path_String]"
        return eval_JSONImport(path.value)
