"""
Directory Operations
"""

import os
import os.path as osp
import shutil
import tempfile

from mathics.core.atoms import String
from mathics.core.attributes import A_LISTABLE, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_expression
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed
from mathics.eval.directories import TMP_DIR


class CreateDirectory(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/CreateDirectory.html</url>

    <dl>
      <dt>'CreateDirectory'["$dir$"]
      <dd>creates a directory called $dir$.

      <dt>'CreateDirectory[]'
      <dd>creates a temporary directory.
    </dl>

    >> dir = CreateDirectory[]
     = ...
    #> DirectoryQ[dir]
     = True
    #> DeleteDirectory[dir]
    """

    attributes = A_LISTABLE | A_PROTECTED

    options = {
        "CreateIntermediateDirectories": "True",
    }

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
        "nffil": "File not found during `1`.",
        "filex": "`1` already exists.",
    }
    summary_text = "create a directory"

    def eval(self, dirname, evaluation: Evaluation, options: dict):
        "CreateDirectory[dirname_, OptionsPattern[CreateDirectory]]"

        expr = to_expression("CreateDirectory", dirname)
        py_dirname = dirname.to_python()

        if not (isinstance(py_dirname, str) and py_dirname[0] == py_dirname[-1] == '"'):
            evaluation.message("CreateDirectory", "fstr", dirname)
            return

        py_dirname = py_dirname[1:-1]

        if osp.isdir(py_dirname):
            evaluation.message("CreateDirectory", "filex", osp.abspath(py_dirname))
            return

        os.mkdir(py_dirname)

        if not osp.isdir(py_dirname):
            evaluation.message("CreateDirectory", "nffil", expr)
            return

        return String(osp.abspath(py_dirname))

    def eval_empty(self, evaluation: Evaluation, options: dict):
        "CreateDirectory[OptionsPattern[CreateDirectory]]"
        dirname = tempfile.mkdtemp(prefix="m", dir=TMP_DIR)
        return String(dirname)


class DeleteDirectory(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DeleteDirectory.html</url>

    <dl>
      <dt>'DeleteDirectory'["$dir$"]
      <dd>deletes a directory called $dir$.
    </dl>

    >> dir = CreateDirectory[]
     = ...
    >> DeleteDirectory[dir]
    >> DirectoryQ[dir]
     = False
    #> Quiet[DeleteDirectory[dir]]
     = $Failed
    """

    messages = {
        "strs": (
            "String or non-empty list of strings expected at " "position 1 in `1`."
        ),
        "nodir": "Directory `1` not found.",
        "dirne": "Directory `1` not empty.",
        "optx": "Unknown option `1` in `2`",
        "idcts": "DeleteContents expects either True or False.",  # MMA Bug
    }
    options = {
        "DeleteContents": "False",
    }
    summary_text = "delete a directory"

    def eval(self, dirname, evaluation: Evaluation, options: dict):
        "DeleteDirectory[dirname_, OptionsPattern[DeleteDirectory]]"

        expr = to_expression("DeleteDirectory", dirname)
        py_dirname = dirname.to_python()

        delete_contents = options["System`DeleteContents"].to_python()
        if delete_contents not in [True, False]:
            evaluation.message("DeleteDirectory", "idcts")
            return

        if not (isinstance(py_dirname, str) and py_dirname[0] == py_dirname[-1] == '"'):
            evaluation.message("DeleteDirectory", "strs", expr)
            return

        py_dirname = py_dirname[1:-1]

        if not osp.isdir(py_dirname):
            evaluation.message("DeleteDirectory", "nodir", dirname)
            return SymbolFailed

        if delete_contents:
            shutil.rmtree(py_dirname)
        else:
            if os.listdir(py_dirname) != []:
                evaluation.message("DeleteDirectory", "dirne", dirname)
                return SymbolFailed
            os.rmdir(py_dirname)

        return SymbolNull


class RenameDirectory(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RenameDirectory.html</url>

    <dl>
      <dt>'RenameDirectory'["$dir_1$", "$dir_2$"]
      <dd>renames directory $dir_1$ to $dir_2$.
    </dl>
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
        "filex": "Cannot overwrite existing file `1`.",
        "nodir": "Directory `1` not found.",
    }
    summary_text = "change the name of a directory"

    def eval(self, dirs, evaluation):
        "RenameDirectory[dirs__]"

        seq = dirs.get_sequence()
        if len(seq) != 2:
            evaluation.message("RenameDirectory", "argr", "RenameDirectory", 2)
            return
        dir1, dir2 = (s.to_python() for s in seq)

        if not (isinstance(dir1, str) and dir1[0] == dir1[-1] == '"'):
            evaluation.message("RenameDirectory", "fstr", seq[0])
            return
        dir1 = dir1[1:-1]

        if not (isinstance(dir2, str) and dir2[0] == dir2[-1] == '"'):
            evaluation.message("RenameDirectory", "fstr", seq[1])
            return
        dir2 = dir2[1:-1]

        if not osp.isdir(dir1):
            evaluation.message("RenameDirectory", "nodir", seq[0])
            return SymbolFailed
        if osp.isdir(dir2):
            evaluation.message("RenameDirectory", "filex", seq[1])
            return SymbolFailed

        shutil.move(dir1, dir2)

        return String(osp.abspath(dir2))


# TODO: CopyDirectory
