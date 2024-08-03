"""
Directory Names
"""

import os
import os.path as osp

from mathics.core.atoms import String
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_expression
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.streams import path_search
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.eval.directories import SYS_ROOT_DIR


class DirectoryName(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DirectoryName.html</url>

    <dl>
      <dt>'DirectoryName["$name$"]'
      <dd>extracts the directory name from a filename.
    </dl>

    >> DirectoryName["a/b/c"]
     = a/b

    >> DirectoryName["a/b/c", 2]
     = a
    """

    messages = {
        "string": "String expected at position 1 in `1`.",
        "intpm": ("Positive machine-sized integer expected at " "position 2 in `1`."),
    }

    options = {
        "OperatingSystem": "$OperatingSystem",
    }
    summary_text = "directory part of a filename"

    def eval_with_n(self, name, n, evaluation: Evaluation, options: dict):
        "DirectoryName[name_, n_, OptionsPattern[DirectoryName]]"

        if n is None:
            expr = to_expression("DirectoryName", name)
            py_n = 1
        else:
            expr = to_expression("DirectoryName", name, n)
            py_n = n.to_python()

        if not (isinstance(py_n, int) and py_n > 0):
            evaluation.message("DirectoryName", "intpm", expr)
            return

        py_name = name.to_python()
        if not (isinstance(py_name, str) and py_name[0] == py_name[-1] == '"'):
            evaluation.message("DirectoryName", "string", expr)
            return
        py_name = py_name[1:-1]

        result = py_name
        for i in range(py_n):
            (result, tmp) = osp.split(result)

        return String(result)

    def eval(self, name, evaluation: Evaluation, options: dict):
        "DirectoryName[name_, OptionsPattern[DirectoryName]]"
        return self.eval_with_n(name, None, evaluation, options)


class DirectoryQ(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DirectoryQ.html</url>

    <dl>
      <dt>'DirectoryQ["$name$"]'
      <dd>returns 'True' if the directory called $name$ exists and 'False' otherwise.
    </dl>

    >> DirectoryQ["ExampleData/"]
     = True
    >> DirectoryQ["ExampleData/MythicalSubdir/"]
     = False
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }
    summary_text = "test whether a path exists and is a directory"

    def eval(self, pathname, evaluation):
        "DirectoryQ[pathname_]"
        path = pathname.to_python()

        if not (isinstance(path, str) and path[0] == path[-1] == '"'):
            evaluation.message("DirectoryQ", "fstr", pathname)
            return
        path = path[1:-1]

        path, _ = path_search(path)

        if path is not None and osp.isdir(path):
            return SymbolTrue
        return SymbolFalse


class FileNameDepth(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FileNameDepth.html</url>

    <dl>
      <dt>'FileNameDepth["$name$"]'
      <dd>gives the number of path parts in the given filename.
    </dl>

    >> FileNameDepth["a/b/c"]
     = 3

    >> FileNameDepth["a/b/c/"]
     = 3
    """

    options = {
        "OperatingSystem": "$OperatingSystem",
    }

    rules = {
        "FileNameDepth[name_String]": "Length[FileNameSplit[name]]",
    }
    summary_text = "number of parts in a path"


class FileNameJoin(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FileNameJoin.html</url>

    <dl>
      <dt>'FileNameJoin[{"$dir_1$", "$dir_2$", ...}]'
      <dd>joins the $dir_i$ together into one path.

      <dt>'FileNameJoin[..., OperatingSystem->"os"]'
      <dd>yields a file name in the format for the specified operating system. \
          Possible choices are "Windows", "MacOSX", and "Unix".
    </dl>

    >> FileNameJoin[{"dir1", "dir2", "dir3"}]
     = ...

    >> FileNameJoin[{"dir1", "dir2", "dir3"}, OperatingSystem -> "Unix"]
     = dir1/dir2/dir3

    >> FileNameJoin[{"dir1", "dir2", "dir3"}, OperatingSystem -> "Windows"]
     = dir1\\dir2\\dir3
    """

    messages = {
        "ostype": (
            "The value of option OperatingSystem -> `1` "
            'must be one of "MacOSX", "Windows", or "Unix".'
        ),
    }
    options = {
        "OperatingSystem": "$OperatingSystem",
    }
    summary_text = "join parts into a path"

    def eval(self, pathlist, evaluation: Evaluation, options: dict):
        "FileNameJoin[pathlist_List, OptionsPattern[FileNameJoin]]"

        py_pathlist = pathlist.to_python()
        if not all(isinstance(p, str) and p[0] == p[-1] == '"' for p in py_pathlist):
            return
        py_pathlist = [p[1:-1] for p in py_pathlist]

        operating_system = (
            options["System`OperatingSystem"].evaluate(evaluation).get_string_value()
        )

        if operating_system not in ["MacOSX", "Windows", "Unix"]:
            evaluation.message(
                "FileNameSplit", "ostype", options["System`OperatingSystem"]
            )
            if os.name == "posix":
                operating_system = "Unix"
            elif os.name == "nt":
                operating_system = "Windows"
            elif os.name == "os2":
                operating_system = "MacOSX"
            else:
                return

        if operating_system in ("Unix", "MacOSX"):
            import posixpath

            result = posixpath.join(*py_pathlist)
        elif operating_system in ("Windows",):
            import ntpath

            result = ntpath.join(*py_pathlist)
        else:
            result = osp.join(*py_pathlist)

        return String(result)


class FileNameSplit(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FileNameSplit.html</url>

    <dl>
      <dt>'FileNameSplit["$filenames$"]'
      <dd>splits a $filename$ into a list of parts.
    </dl>

    >> FileNameSplit["example/path/file.txt"]
     = {example, path, file.txt}
    """

    messages = {
        "ostype": (
            "The value of option OperatingSystem -> `1` "
            'must be one of "MacOSX", "Windows", or "Unix".'
        ),
    }
    options = {
        "OperatingSystem": "$OperatingSystem",
    }

    summary_text = "split the file name in a list of parts"

    def eval(self, filename, evaluation: Evaluation, options: dict):
        "FileNameSplit[filename_String, OptionsPattern[FileNameSplit]]"

        path = filename.to_python()[1:-1]

        operating_system = (
            options["System`OperatingSystem"].evaluate(evaluation).to_python()
        )

        if operating_system not in ['"MacOSX"', '"Windows"', '"Unix"']:
            evaluation.message(
                "FileNameSplit", "ostype", options["System`OperatingSystem"]
            )
            if os.name == "posix":
                operating_system = "Unix"
            elif os.name == "nt":
                operating_system = "Windows"
            elif os.name == "os2":
                operating_system = "MacOSX"
            else:
                return

        # TODO Implement OperatingSystem Option

        result = []
        while path not in ["", SYS_ROOT_DIR]:
            path, ext = osp.split(path)
            if ext != "":
                result.insert(0, ext)

        return from_python(result)


class ParentDirectory(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ParentDirectory.html</url>

    <dl>
      <dt>'ParentDirectory[]'
      <dd>returns the parent of the current working directory.

      <dt>'ParentDirectory["$dir$"]'
      <dd>returns the parent $dir$.
    </dl>

    >> ParentDirectory[]
     = ...
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }
    rules = {
        "ParentDirectory[]": "ParentDirectory[Directory[]]",
    }
    summary_text = "parent directory of the current working directory"

    def eval(self, path, evaluation):
        "ParentDirectory[path_]"

        if not isinstance(path, String):
            evaluation.message("ParentDirectory", "fstr", path)
            return

        pypath = path.to_python()[1:-1]

        result = osp.abspath(osp.join(pypath, osp.pardir))
        return String(result)


# TODO: FileNameDepth, NotebookFileName
