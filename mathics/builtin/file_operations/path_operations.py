"""
File Path Manipulation
"""

import os.path as osp
from pathlib import Path
from typing import Optional

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
     = ...

    >> FileNameDrop[path, -1]
      = ...

    A shorthand for the above:

    >> FileNameDrop[path]
     = ...
    """

    messages = {
        "notfinished": "m-n handling is not complete.",
    }
    rules = {
        "FileNameDrop[name_]": "FileNameDrop[name, -1]",
        "FileNameDrop[list_List, parms___]": "FileNameDrop[#1,parms]&/@list",
    }
    summary_text = "drop a part of a file path"

    def eval_with_n(self, path: String, n: Integer, evaluation: Evaluation) -> String:
        "FileNameDrop[path_String, n_Integer]"
        pos = n.value
        if pos == 0:
            return path
        path_elts = Path(path.value).parts
        path_len = len(path_elts)
        if pos >= path_len or pos <= -path_len:
            return String("")

        new_elts = path_elts[pos:] if pos > 0 else path_elts[:pos]
        return String(osp.join(*new_elts) if new_elts else "")

    def eval_with_n_to_m(
        self, path: String, n: Integer, m: Integer, evaluation: Evaluation
    ) -> Optional[String]:
        "FileNameDrop[path_String, {n_Integer, m_Integer}]"
        n_pos = n.value
        m_pos = m.value
        path_elts = Path(path.value).parts
        path_len = len(path_elts)
        if n_pos > path_len:
            return path

        if n_pos == path_len:
            if n_pos == m_pos or n_pos + m_pos == -1:
                # Not sure why this is so.
                return String(osp.join(*path_elts[:-1]))
            return path

        if n_pos > m_pos:
            return path

        new_elts = None
        if 0 < n_pos < m_pos:
            new_elts = path_elts[: n_pos - 1] + path_elts[m_pos:]
        elif n_pos <= m_pos <= 0:
            new_elts = path_elts[:n_pos] + path_elts[m_pos + 1 :]
        else:
            evaluation.message("FindNameDrop", "notfinished")
            return None

        if new_elts:
            return String(osp.join(*new_elts))
        else:
            return String("")
