"""
File Path Manipulation
"""

import os.path as osp
from pathlib import Path

from mathics.core.atoms import Integer, String
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation

# This tells documentation how to sort this module
sort_order = "mathics.builtin.file-operations.file_path_operations"


class FileNameDrop(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FileNameDrop.html</url>

    <dl>
      <dt>'FileNameDrop["$path$", $n$]'
      <dd>drops the first $n$ path elements in the file name $path$.

      <dt>'FileNameDrop["$path$", -$n$]'
      <dd>drops the last $n$ path elements in the file name $path$.

      <dt>'FileNameDrop["$path$", {$m$, $n$}]'
      <dd>drops elements $m$ through $n$ path elements in the file name $path$.

      <dt>'FileNameDrop["$path$"]'
      <dd>drops the last path elements in the file name $path$.
    </dl>

    >> path = FileNameJoin{"a","b","c"}

    >> FileNameDrop[path, -1]

    A shorthand for the above:

    >> FileNameDrop[path]
    """

    rules = {"FileNameDrop[name_]": "FileNameDrop[name, -1]"}
    summary_text = "drop a part of a file path"

    def eval_with_n(self, path: String, n: Integer, evaluation: Evaluation):
        "FileNameDrop[path_String, n_Integer]"
        pos = n.value
        path_elts = Path(path.value).parts
        path_len = len(path_elts)
        if pos < 0:
            pos = path_len + pos

        if pos >= len(path_elts):
            return String("")
        new_elts = path_elts[pos:]
        return String(osp.join(*new_elts))

    def eval_with_n_to_m(
        self, path: String, n: Integer, m: Integer, evaluation: Evaluation
    ):
        "FileNameDrop[path_String, {n_Integer, m_Integer}]"
        n_pos = n.value
        m_pos = m.value
        path_elts = Path(path.value).parts
        path_len = len(path_elts)
        if n_pos < 0 or n_pos >= path_len:
            return path
        elif n_pos == 0:
            # We need to keep pos from going negative which is interpreted as
            # the last value. 1-1 = 0, so 1 is the right value here.
            n_pos = 1

        if m_pos < 0:
            m_pos = path_len + m_pos - 1

        new_elts = path_elts[: n_pos - 1] + path_elts[m_pos:]
        if new_elts:
            return String(osp.join(*new_elts))
        else:
            return String("")
