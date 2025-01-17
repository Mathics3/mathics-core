"""
File Utilities
"""

from mathics.builtin.files_io.files import MathicsOpen
from mathics.core.builtin import Builtin, MessageException
from mathics.core.convert.expression import to_expression
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.systemsymbols import SymbolFailed

sort_order = "mathics.builtin.file-operations.file_utilities"


class FindList(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FindList.html</url>

    <dl>
      <dt>'FindList[$file$, $text$]'
      <dd>returns a list of all lines in $file$ that contain $text$.

      <dt>'FindList[$file$, {$text1$, $text2$, ...}]'
      <dd>returns a list of all lines in $file$ that contain any of the specified \
          string.

      <dt>'FindList[{$file1$, $file2$, ...}, ...]'
      <dd>returns a list of all lines in any of the $filei$ that contain the specified \
          strings.
    </dl>

    >> stream = FindList["ExampleData/EinsteinSzilLetter.txt", "uranium"];
    >> Length[stream]
     = 7

    >> FindList["ExampleData/EinsteinSzilLetter.txt", "uranium", 1]
     = {in manuscript, leads me to expect that the element uranium may be turned into}
    """

    messages = {
        "strs": "String or non-empty list of strings expected at position `1` in `2`.",
    }

    options = {
        "AnchoredSearch": "False",
        "IgnoreCase": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "WordSearch": "False",
        "WordSeparators": '{" ", "\t"}',
    }
    summary_text = "list lines in a file that contains a text"

    # TODO: Extra options AnchoredSearch, IgnoreCase RecordSeparators,
    # WordSearch, WordSeparators this is probably best done with a regex

    def eval_without_n(self, filename, text, evaluation: Evaluation, options: dict):
        "FindList[filename_, text_, OptionsPattern[FindList]]"
        return self.eval(filename, text, None, evaluation, options)

    def eval(self, filename, text, n, evaluation: Evaluation, options: dict):
        "FindList[filename_, text_, n_, OptionsPattern[FindList]]"
        py_text = text.to_python()
        py_name = filename.to_python()
        if n is None:
            py_n = None
            expr = to_expression("FindList", filename, text)
        else:
            py_n = n.to_python()
            expr = to_expression("FindList", filename, text, n)

        if not isinstance(py_text, list):
            py_text = [py_text]

        if not isinstance(py_name, list):
            py_name = [py_name]

        if not all(isinstance(t, str) and t[0] == t[-1] == '"' for t in py_name):
            evaluation.message("FindList", "strs", "1", expr)
            return SymbolFailed

        if not all(isinstance(t, str) and t[0] == t[-1] == '"' for t in py_text):
            evaluation.message("FindList", "strs", "2", expr)
            return SymbolFailed

        if not ((isinstance(py_n, int) and py_n >= 0) or py_n is None):
            evaluation.message("FindList", "intnm", "3", expr)
            return SymbolFailed

        if py_n == 0:
            return SymbolFailed

        py_text = [t[1:-1] for t in py_text]
        py_name = [t[1:-1] for t in py_name]

        results = []
        for path in py_name:
            try:
                with MathicsOpen(path, "r") as f:
                    lines = f.readlines()
            except IOError:
                evaluation.message("General", "noopen", path)
                return
            except MessageException as e:
                e.message(evaluation)
                return

            result = []
            for line in lines:
                for t in py_text:
                    if line.find(t) != -1:
                        result.append(line[:-1])
            results.append(result)

        results = [r for result in results for r in result]

        if isinstance(py_n, int):
            results = results[: min(py_n, len(results))]

        return from_python(results)


# TODO: FilePrint, ReadString
