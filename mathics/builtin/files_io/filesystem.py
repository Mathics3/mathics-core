# -*- coding: utf-8 -*-

"""
Filesystem Operations
"""

import os
import os.path as osp
import pathlib
import re
import shutil
from typing import List

from mathics.builtin.files_io.files import MathicsOpen
from mathics.core.atoms import Integer, String
from mathics.core.attributes import A_LISTABLE, A_LOCKED, A_PROTECTED
from mathics.core.builtin import Builtin, MessageException, Predefined
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.convert.regex import to_regex
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.streams import create_temporary_file, path_search, urlsave_tmp
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolNull,
    SymbolTrue,
    valid_context_name,
)
from mathics.core.systemsymbols import (
    SymbolFailed,
    SymbolMemberQ,
    SymbolNeeds,
    SymbolPackages,
)
from mathics.eval.directories import DIRECTORY_STACK
from mathics.eval.files_io.files import eval_Get
from mathics.eval.stackframe import get_eval_Expression


class AbsoluteFileName(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/AbsoluteFileName.html</url>

    <dl>
      <dt>'AbsoluteFileName'["$name$"]
      <dd>returns the absolute version of the given filename.
    </dl>

    >> AbsoluteFileName["ExampleData/sunflowers.jpg"]
     = ...

    """

    messages = {
        "fstr": ("File specification x is not a string of one or more characters."),
    }
    summary_text = "get absolute file path"

    def eval(self, name, evaluation):
        "AbsoluteFileName[name_]"

        py_name = name.to_python()

        if not isinstance(py_name, str):
            evaluation.message("AbsoluteFileName", "fstr", name)
            return

        if py_name[0] == py_name[-1] == '"':
            py_name = py_name[1:-1]

        result, _ = path_search(py_name)

        if result is None:
            evaluation.message(
                "AbsoluteFileName", "nffil", to_expression("AbsoluteFileName", name)
            )
            return SymbolFailed

        return String(osp.abspath(result))


class CopyDirectory(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/CopyDirectory.html</url>

    <dl>
      <dt>'CopyDirectory'["$dir_1$", "$dir_2$"]
      <dd>copies directory $dir_1$ to $dir_2$.
    </dl>
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
        "filex": "Cannot overwrite existing file `1`.",
        "nodir": "Directory `1` not found.",
    }
    summary_text = "copy a directory into a new path"

    def eval(self, dirs, evaluation):
        "CopyDirectory[dirs__]"

        seq = dirs.get_sequence()
        if len(seq) != 2:
            evaluation.message("CopyDirectory", "argr", "CopyDirectory", 2)
            return
        dir1, dir2 = (s.to_python() for s in seq)

        if not (isinstance(dir1, str) and dir1[0] == dir1[-1] == '"'):
            evaluation.message("CopyDirectory", "fstr", seq[0])
            return
        dir1 = dir1[1:-1]

        if not (isinstance(dir2, str) and dir2[0] == dir2[-1] == '"'):
            evaluation.message("CopyDirectory", "fstr", seq[1])
            return
        dir2 = dir2[1:-1]

        if not osp.isdir(dir1):
            evaluation.message("CopyDirectory", "nodir", seq[0])
            return SymbolFailed
        if osp.isdir(dir2):
            evaluation.message("CopyDirectory", "filex", seq[1])
            return SymbolFailed

        shutil.copytree(dir1, dir2)

        return String(osp.abspath(dir2))


class CopyFile(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/CopyFile.html</url>

    <dl>
      <dt>'CopyFile'["$file_1$", "$file_2$"]
      <dd>copies $file_1$ to $file_2$.
    </dl>

    X> CopyFile["ExampleData/sunflowers.jpg", "MathicsSunflowers.jpg"]
     = MathicsSunflowers.jpg
    X> DeleteFile["MathicsSunflowers.jpg"]
    """

    messages = {
        "filex": "Cannot overwrite existing file `1`.",
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }
    summary_text = "copy a file into a new path"

    def eval(self, source, dest, evaluation):
        "CopyFile[source_, dest_]"

        py_source = source.to_python()
        py_dest = dest.to_python()

        # Check filenames
        if not (isinstance(py_source, str)):
            evaluation.message("CopyFile", "fstr", source)
            return
        if not (isinstance(py_dest, str)):
            evaluation.message("CopyFile", "fstr", dest)
            return

        if py_source[0] == py_source[-1] == '"':
            py_source = py_source[1:-1]

        if py_dest[0] == py_dest[-1] == '"':
            py_dest = py_dest[1:-1]

        py_source, _ = path_search(py_source)

        if py_source is None:
            evaluation.message("CopyFile", "filex", source)
            return SymbolFailed

        if osp.exists(py_dest):
            evaluation.message("CopyFile", "filex", dest)
            return SymbolFailed

        try:
            shutil.copy(py_source, py_dest)
        except IOError:
            evaluation.message("CopyFile", "nffil", get_eval_Expression())
            return SymbolFailed

        return dest


class CreateFile(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/CreateFile.html</url>

    <dl>
      <dt>'CreateFile["filename"]'
      <dd>Creates a file named "filename" temporary file, but do not open it.

      <dt>'CreateFile[]'
      <dd>Creates a temporary file, but do not open it.
    </dl>
    """

    attributes = A_LISTABLE | A_PROTECTED
    options = {
        "CreateIntermediateDirectories": "True",
        "OverwriteTarget": "True",
    }
    rules = {
        "CreateFile[]": "CreateTemporary[]",
    }
    summary_text = "create a file"

    def eval(self, filename, evaluation: Evaluation, **options):
        "CreateFile[filename_String, OptionsPattern[CreateFile]]"
        try:
            # TODO: Implement options
            if not osp.isfile(filename.value):
                f = open(filename.value, "w")
                res = f.name
                f.close()
                return String(res)
            else:
                return filename
        except Exception:
            return SymbolFailed


class CreateTemporary(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/CreateTemporary.html</url>

    <dl>
      <dt>'CreateTemporary[]'
      <dd>Creates a temporary file, but do not open it.
    </dl>
    """

    summary_text = "create a temporary file"

    def eval(self, evaluation: Evaluation):
        "CreateTemporary[]"
        try:
            res = create_temporary_file()
        except Exception:
            return SymbolFailed
        return String(res)


class DeleteFile(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DeleteFile.html</url>

    <dl>
      <dt>'Delete'["$file$"]
      <dd>deletes $file$.

      <dt>'Delete'[{"$file_1$", "$file_2$", ...}]
      <dd>deletes a list of files.
    </dl>

    >> CopyFile["ExampleData/sunflowers.jpg", "MathicsSunflowers.jpg"];
    >> DeleteFile["MathicsSunflowers.jpg"]

    >> CopyFile["ExampleData/sunflowers.jpg", "MathicsSunflowers1.jpg"];
    >> CopyFile["ExampleData/sunflowers.jpg", "MathicsSunflowers2.jpg"];
    >> DeleteFile[{"MathicsSunflowers1.jpg", "MathicsSunflowers2.jpg"}]
    """

    messages = {
        "filex": "Cannot overwrite existing file `1`.",
        "strs": (
            "String or non-empty list of strings expected at " "position `1` in `2`."
        ),
    }
    summary_text = "delete a file"

    def eval(self, filename, evaluation):
        "DeleteFile[filename_]"

        py_path = filename.to_python()
        if not isinstance(py_path, (list, tuple)):
            py_path = [py_path]

        py_paths = []
        for path in py_path:
            # Check filenames
            if not isinstance(path, str):
                evaluation.message(
                    "DeleteFile", "strs", filename, get_eval_Expression()
                )
                return

            if path[0] == path[-1] == '"':
                path = path[1:-1]
            path, _ = path_search(path)

            if path is None:
                evaluation.message("DeleteFile", "nffil", get_eval_Expression())
                return SymbolFailed
            py_paths.append(path)

        for path in py_paths:
            try:
                os.remove(path)
            except OSError:
                return SymbolFailed

        return SymbolNull


class Directory(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Directory.html</url>

    <dl>
      <dt>'Directory[]'
      <dd>returns the current working directory.
    </dl>

    >> Directory[]
    = ...
    """

    summary_text = "current working directory"

    def eval(self, evaluation: Evaluation):
        "Directory[]"
        result = os.getcwd()
        return String(result)


class DirectoryStack(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DirectoryStack.html</url>

    <dl>
      <dt>'DirectoryStack[]'
      <dd>returns the directory stack.
    </dl>

    >> DirectoryStack[]
    = ...
    """

    summary_text = "list the sequence of current directories in use"

    def eval(self, evaluation):
        "DirectoryStack[]"
        global DIRECTORY_STACK
        return from_python(DIRECTORY_STACK)


class ExpandFileName(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ExpandFileName.html</url>

    <dl>
      <dt>'ExpandFileName'["$name$"]
      <dd>expands $name$ to an absolute filename for your system.
    </dl>

    >> ExpandFileName["ExampleData/sunflowers.jpg"]
     = ...
    """

    messages = {
        "string": "String expected at position 1 in `1`.",
    }
    summary_text = "absolute path"

    def eval(self, name, evaluation):
        "ExpandFileName[name_]"

        py_name = name.to_python()

        if not (isinstance(py_name, str) and py_name[0] == py_name[-1] == '"'):
            evaluation.message("ExpandFileName", "string", get_eval_Expression())
            return
        py_name = py_name[1:-1]

        return String(osp.abspath(py_name))


class File(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/File.html</url>

    <dl>
      <dt>'File'["$file$"]
      <dd>is a symbolic representation of an element in the local file system.
    </dl>
    """

    summary_text = "element of the local filesystem"


class FileBaseName(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FileBaseName.html</url>

    <dl>
      <dt>'FileBaseName'["$file$"]
      <dd>gives the base name for the specified file name.
    </dl>

    >> FileBaseName["file.txt"]
     = file

    >> FileBaseName["file.tar.gz"]
     = file.tar
    """

    options = {
        "OperatingSystem": "$OperatingSystem",
    }
    summary_text = "base name of the file"

    def eval(self, filename, evaluation: Evaluation, options: dict):
        "FileBaseName[filename_String, OptionsPattern[FileBaseName]]"
        path = filename.to_python()[1:-1]

        filename_base, filename_ext = osp.splitext(path)
        return String(filename_base)


class FileByteCount(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileByteCount.html</url>

    <dl>
      <dt>'FileByteCount'[$file$]
      <dd>returns the number of bytes in $file$.
    </dl>

    >> FileByteCount["ExampleData/sunflowers.jpg"]
     = 142286
    """

    messages = {
        "fstr": "File specification `1` is not a string of one or more characters.",
    }
    summary_text = "length of the file"

    def eval(self, filename, evaluation):
        "FileByteCount[filename_]"
        py_filename = filename.to_python()
        if not (
            isinstance(py_filename, str) and py_filename[0] == py_filename[-1] == '"'
        ):
            evaluation.message("FileByteCount", "fstr", filename)
            return
        py_filename = py_filename[1:-1]

        try:
            with MathicsOpen(py_filename, "rb") as f:
                count = 0
                tmp = f.read(1)
                while tmp != b"":
                    count += 1
                    tmp = f.read(1)

        except IOError:
            evaluation.message("General", "noopen", filename)
            return
        except MessageException as e:
            e.message(evaluation)
            return

        return Integer(count)


class FileExistsQ(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileExistsQ.html</url>

    <dl>
      <dt>'FileExistsQ'["$file$"]
      <dd>returns 'True' if $file$ exists and 'False' otherwise.
    </dl>

    >> FileExistsQ["ExampleData/sunflowers.jpg"]
     = True
    >> FileExistsQ["ExampleData/sunflowers.png"]
     = False
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }
    summary_text = "test whether a file exists"

    def eval(self, filename, evaluation):
        "FileExistsQ[filename_]"
        path = filename.to_python()
        if not (isinstance(path, str) and path[0] == path[-1] == '"'):
            evaluation.message("FileExistsQ", "fstr", filename)
            return
        path = path[1:-1]

        path, is_temporary_file = path_search(path)

        if path is None:
            return SymbolFalse
        return SymbolTrue


class FileExtension(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FileExtension.html</url>

    <dl>
      <dt>'FileExtension'["$file$"]
      <dd>gives the extension for the specified file name.
    </dl>

    >> FileExtension["file.txt"]
     = txt

    >> FileExtension["file.tar.gz"]
     = gz
    """

    options = {
        "OperatingSystem": "$OperatingSystem",
    }
    summary_text = "file extension"

    def eval(self, filename, evaluation: Evaluation, options: dict):
        "FileExtension[filename_String, OptionsPattern[FileExtension]]"
        path = filename.to_python()[1:-1]
        filename_base, filename_ext = osp.splitext(path)
        filename_ext = filename_ext.lstrip(".")
        return String(filename_ext)


class FileInformation(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileInformation.html</url>

    <dl>
      <dt>'FileInformation'["$file$"]
      <dd>returns information about $file$.
    </dl>

    This function is totally undocumented in MMA!

    >> FileInformation["ExampleData/sunflowers.jpg"]
     = {File -> ..., FileType -> File, ByteCount -> 142286, Date -> ...}
    """

    rules = {
        "FileInformation[name_String]": "If[FileExistsQ[name], {File -> ExpandFileName[name], FileType -> FileType[name], ByteCount -> FileByteCount[name], Date -> AbsoluteTime[FileDate[name]]}, {}]",
    }
    summary_text = "information about a file"


class FindFile(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileFind.html</url>

    <dl>
      <dt>'FindFile'[$name$]
      <dd>searches '\$Path' for the given filename.
    </dl>

    >> FindFile["ExampleData/sunflowers.jpg"]
     = ...

    >> FindFile["VectorAnalysis`"]
     = ...

    >> FindFile["VectorAnalysis`VectorAnalysis`"]
     = ...
    """

    messages = {
        "string": "String expected at position 1 in `1`.",
    }
    summary_text = (
        "search the path of of a file in the current directory and its subdirectories"
    )

    def eval(self, name, evaluation):
        "FindFile[name_]"

        py_name = name.to_python()

        if not (isinstance(py_name, str) and py_name[0] == py_name[-1] == '"'):
            evaluation.message("FindFile", "string", get_eval_Expression())
            return
        py_name = py_name[1:-1]

        result, is_temporary_file = path_search(py_name)

        if result is None:
            return SymbolFailed

        return String(osp.abspath(result))


class FileNames(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileNames.html</url>

    <dl>
      <dt>'FileNames[]'
      <dd>Returns a list with the filenames in the current working folder.

      <dt>'FileNames'[$form$]
      <dd>Returns a list with the filenames in the current working folder that \
          matches with $form$.

      <dt>'FileNames'[{$form_1$, $form_2$, ...}]
      <dd>Returns a list with the filenames in the current working folder that \
          matches with one of $form_1$, $form_2$, ....

      <dt>'FileNames'[{$form_1$, $form_2$, ...},{$dir_1$, $dir_2$, ...}]
      <dd>Looks into the directories $dir_1$, $dir_2$, ....

      <dt>'FileNames'[{$form_1$, $form_2$, ...},{$dir_1$, $dir_2$, ...}]
      <dd>Looks into the directories $dir_1$, $dir_2$, ....

      <dt>'FileNames'[{$forms$, $dirs$, $n$]
      <dd>Look for files up to the level $n$.
    </dl>

    >> SetDirectory[$InstallationDirectory <> "/autoload"];
    >> FileNames["*.m", "formats"]//Length
     = ...
    >> FileNames["*.m", "formats", 3]//Length
     = ...
    >> FileNames["*.m", "formats", Infinity]//Length
     = ...
    """

    # >> FileNames[]//Length
    #  = 2
    fmtmaps = {Symbol("System`All"): "*"}
    messages = {
        "nofmtstr": "`1` is not a format or a list of formats.",
        "nodirstr": "`1` is not a directory name  or a list of directory names.",
        "badn": "`1` is not an integer number.",
    }
    options = {
        "IgnoreCase": "Automatic",
    }
    summary_text = "list file names in the current directory"

    def eval(self, evaluation, **options):
        """FileNames[OptionsPattern[FileNames]]"""
        return self.eval_with_forms_dirs_and_level(
            String("*"), String(os.getcwd()), None, evaluation, **options
        )

    def eval_with_forms(self, forms, evaluation, **options):
        """FileNames[forms_, OptionsPattern[FileNames]]"""
        return self.eval_with_forms_dirs_and_level(
            forms, String(os.getcwd()), None, evaluation, **options
        )

    def eval_with_forms_and_dirs(self, forms, dirs, evaluation, **options):
        """FileNames[forms_, dirs_, OptionsPattern[FileNames]]"""
        return self.eval_with_forms_dirs_and_level(
            forms, dirs, None, evaluation, **options
        )

    def eval_with_forms_dirs_and_level(self, forms, dirs, n, evaluation, **options):
        """FileNames[forms_, dirs_, n_, OptionsPattern[FileNames]]"""
        filenames = set()
        # Build a list of forms.
        if forms.get_head_name() == "System`List":
            form_list = []
            for p in forms._elements:
                if self.fmtmaps.get(p, None):
                    form_list.append(self.fmtmaps[p])
                else:
                    form_list.append(p)
        else:
            form_list = [
                self.fmtmaps[forms] if self.fmtmaps.get(forms, None) else forms
            ]
        # Build a list of directories.
        if isinstance(dirs, String):
            py_dirs = [dirs.value]
        elif dirs.get_head_name() == "System`List":
            py_dirs = []
            for p in dirs._elements:
                if isinstance(p, String):
                    py_dirs.append(p.value)
                else:
                    evaluation.message("FileNames", "nodirstr", dirs)
                    return
        else:
            evaluation.message("FileNames", "nodirstr", dirs)
            return

        if n is not None:
            if isinstance(n, Integer):
                level = n.value
            # We can't test against SymbolDirectedInfinity,
            # because Infinity a compound expression.
            elif n.get_head_name() == "System`DirectedInfinity":
                level = None
            else:
                evaluation.message("FileNames", "badn", n)
                return
        else:
            level = 1

        # list the files

        def re_compile_form_list(form_list: list, re_flags: int) -> List[re.Pattern]:
            """
            re.compile each Expression in ``form_list``. Compile using
            re_flags which is either re.NO_FLAGS or re.IGNORECASE.
            Return a list of the compiled patterns when the string in
            form_list that are valid string expressions.

            Invalid string expressions are removed removed from the list.
            """
            patterns = []
            for p in form_list:
                opt_pat_str = to_regex(
                    p, abbreviated_patterns=True, show_message=evaluation.message
                )

                if opt_pat_str is None:
                    continue
                pat_str = f"^{opt_pat_str}$"
                patterns.append(re.compile(pat_str, re_flags))
            return patterns

        re_flags = (
            re.IGNORECASE if options.get("System`IgnoreCase", None) is SymbolTrue else 0
        )
        patterns = re_compile_form_list(form_list, re_flags)

        for py_dir in py_dirs:
            if not osp.isdir(py_dir):
                continue
            if level == 1:
                for fn in os.listdir(py_dir):
                    fullname = osp.join(py_dir, fn)
                    for pattern in patterns:
                        if pattern.match(fn):
                            filenames.add(fullname)
                            break
            else:
                pathlen = len(py_dir)
                for root, child_dirs, child_files in os.walk(py_dir):
                    # FIXME: This is an ugly and inefficient way
                    # to avoid looking deeper than the level n, but I do not realize
                    # how to do this better without a lot of code...
                    if level is not None and len(root[pathlen:].split(osp.sep)) > level:
                        continue
                    for fn in child_files + child_dirs:
                        for pattern in patterns:
                            if pattern.match(fn):
                                filenames.add(osp.join(root, fn))
                                break

        return to_mathics_list(*sorted(filenames), elements_conversion_fn=String)


class FileNameTake(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileNameTake.html</url>

    <dl>
      <dt>'FileNameTake'["$file$"]
      <dd>returns the last path element in the file name $name$.

      <dt>'FileNameTake'["$file$", $n$]
      <dd>returns the first $n$ path elements in the file name $name$.

      <dt>'FileNameTake'["$file$", $-n$]
      <dd>returns the last $n$ path elements in the file name $name$.
    </dl>

    """

    # mmatera: please put in a pytest
    # >> FileNameTake["/tmp/file.txt"]
    #  = file.txt
    # >> FileNameTake["tmp/file.txt", 1]
    #  = tmp
    # >> FileNameTake["tmp/file.txt", -1]
    #  = file.txt

    options = {
        "OperatingSystem": "$OperatingSystem",
    }
    summary_text = "take a part of the filename"

    def eval(self, filename, evaluation: Evaluation, options: dict):
        "FileNameTake[filename_String, OptionsPattern[FileBaseName]]"
        path = pathlib.Path(filename.to_python()[1:-1])
        return String(path.name)

    def eval_n(self, filename, n, evaluation: Evaluation, options: dict):
        "FileNameTake[filename_String, n_Integer, OptionsPattern[FileBaseName]]"
        n_int = n.get_int_value()
        parts = pathlib.Path(filename.to_python()[1:-1]).parts
        if n_int >= 0:
            subparts = parts[:n_int]
        else:
            subparts = parts[n_int:]
        return String(str(pathlib.PurePath(*subparts)))


class Needs(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/Needs.html</url>

    <dl>
    <dt>'Needs["context`"]'
        <dd>loads the specified context if not already in '\$Packages'.
    </dl>

    >> Needs["VectorAnalysis`"]
    """

    messages = {
        "ctx": (
            "Invalid context specified at position `2` in `1`. "
            "A context must consist of valid symbol names separated by "
            "and ending with `3`."
        ),
        "nocont": "Context `1` was not created when Needs was evaluated.",
    }
    summary_text = "load a package if it is not already loaded"

    def eval(self, context, evaluation):
        "Needs[context_String]"
        context_str = context.value
        if context_str == "":
            return SymbolNull
        if context_str[0] == "`":
            curr_ctxt = evaluation.definitions.get_current_context()
            context_str = curr_ctxt + context_str[1:]
            context = String(context_str)
        if not valid_context_name(context_str):
            evaluation.message("Needs", "ctx", Expression(SymbolNeeds, context), 1, "`")
            return
        test_loaded = Expression(SymbolMemberQ, SymbolPackages, context)
        test_loaded = test_loaded.evaluate(evaluation)
        if test_loaded is SymbolTrue:
            # Already loaded
            return SymbolNull
        result = eval_Get(context_str, evaluation)

        if result is SymbolFailed:
            evaluation.message("Needs", "nocont", context)
            return SymbolFailed

        return SymbolNull


class OperatingSystem(Predefined):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/OperatingSystem.html</url>

    <dl>
      <dt>'\$OperatingSystem'
      <dd>gives the type of operating system running Mathics.
    </dl>

    >> $OperatingSystem
     = ...
    """

    attributes = A_LOCKED | A_PROTECTED
    name = "$OperatingSystem"
    summary_text = "type of operating system"

    def evaluate(self, evaluation):
        if os.name == "posix":
            return String("Unix")
        elif os.name == "nt":
            return String("Windows")
        elif os.name == "os2":
            return String("MacOSX")
        else:
            return String("Unknown")


class PathnameSeparator(Predefined):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$PathnameSeparator.html</url>

    <dl>
      <dt>'\$PathnameSeparator'
      <dd>returns a string for the separator in paths.
    </dl>

    >> $PathnameSeparator
     = ...
    """

    name = "$PathnameSeparator"
    summary_text = "system character path separator"

    def evaluate(self, evaluation):
        return String(os.sep)


class RenameFile(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/RenameFile.html</url>

    <dl>
    <dt>'RenameFile'["$file_1$", "$file_2$"]
      <dd>renames $file_1$ to $file_2$.
    </dl>

    >> CopyFile["ExampleData/sunflowers.jpg", "MathicsSunflowers.jpg"]
     = MathicsSunflowers.jpg
    >> RenameFile["MathicsSunflowers.jpg", "MathicsSunnyFlowers.jpg"]
     = MathicsSunnyFlowers.jpg
    >> DeleteFile["MathicsSunnyFlowers.jpg"]
    """

    messages = {
        "filex": "Cannot overwrite existing file `1`.",
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }
    summary_text = "change the name of a file"

    def eval(self, source, dest, evaluation):
        "RenameFile[source_, dest_]"

        py_source = source.to_python()
        py_dest = dest.to_python()

        # Check filenames
        if not (isinstance(py_source, str) and py_source[0] == py_source[-1] == '"'):
            evaluation.message("RenameFile", "fstr", source)
            return
        if not (isinstance(py_dest, str) and py_dest[0] == py_dest[-1] == '"'):
            evaluation.message("RenameFile", "fstr", dest)
            return

        py_source = py_source[1:-1]
        py_dest = py_dest[1:-1]

        py_source, _ = path_search(py_source)

        if py_source is None:
            evaluation.message("RenameFile", "filex", source)
            return SymbolFailed

        if osp.exists(py_dest):
            evaluation.message("RenameFile", "filex", dest)
            return SymbolFailed

        try:
            shutil.move(py_source, py_dest)
        except IOError:
            evaluation.message("RenameFile", "nffil", dest)
            return SymbolFailed

        return dest


class ResetDirectory(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ResetDirectory.html</url>

    <dl>
    <dt>'ResetDirectory[]'
      <dd>pops a directory from the directory stack and returns it.
    </dl>

    >> ResetDirectory[]
    = ...
    """

    messages = {
        "dtop": "Directory stack is empty.",
    }
    summary_text = "return to the directory before the last SetDirectory call"

    def eval(self, evaluation):
        "ResetDirectory[]"
        try:
            tmp = DIRECTORY_STACK.pop()
        except IndexError:
            tmp = os.getcwd()
            evaluation.message("ResetDirectory", "dtop")
        else:
            os.chdir(tmp)
        return String(tmp)


class SetDirectory(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/SetDirectory.html</url>

    <dl>
    <dt>'SetDirectory'[$dir$]
      <dd>sets the current working directory to $dir$.
    </dl>

    S> SetDirectory[]
    = ...
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
        "cdir": "Cannot set current directory to `1`.",
    }
    rules = {
        "SetDirectory[]": "SetDirectory[$HomeDirectory]",
    }
    summary_text = "set the working directory"

    def eval(self, path, evaluation):
        "SetDirectory[path_]"

        if not isinstance(path, String):
            evaluation.message("SetDirectory", "fstr", path)
            return

        py_path = path.__str__()[1:-1]

        if py_path is None or not osp.isdir(py_path):
            evaluation.message("SetDirectory", "cdir", path)
            return SymbolFailed

        try:
            os.chdir(py_path)
        except Exception:
            return SymbolFailed

        DIRECTORY_STACK.append(os.getcwd())
        return String(os.getcwd())


class ToFileName(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ToFileName.html</url>

    <dl>
    <dt>'ToFileName'[{"$dir_1$", "$dir_2$", ...}]
      <dd>joins the $dir_i$ together into one path.
    </dl>

    'ToFileName' has been superseded by 'FileNameJoin'.

    >> ToFileName[{"dir1", "dir2"}, "file"]
     = dir1...dir2...file

    >> ToFileName["dir1", "file"]
     = dir1...file

    >> ToFileName[{"dir1", "dir2", "dir3"}]
     = dir1...dir2...dir3
    """

    rules = {
        "ToFileName[dir_String, name_String]": "FileNameJoin[{dir, name}]",
        "ToFileName[dirs_List, name_String]": "FileNameJoin[Append[dirs, name]]",
        "ToFileName[dirs_List]": "FileNameJoin[dirs]",
    }
    summary_text = "build a path from a list of directory names and a filename"


class URLSave(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/URLSave.html</url>

    <dl>
      <dt>'URLSave["url"]'
      <dd>Save "url" in a temporary file.

      <dt>'URLSave'["url", $filename$]
      <dd>Save "url" in $filename$.
    </dl>
    """

    messages = {
        "invfile": "`1` is not a valid Filename",
        "invhttp": "`1` is not a valid URL",
    }
    summary_text = "save the content of an URL"

    def eval_with_url(self, url, evaluation: Evaluation, **options):
        "URLSave[url_String, OptionsPattern[URLSave]]"
        return self.eval_with_url_and_filename(url, None, evaluation, **options)

    def eval_with_url_and_filename(
        self, url, filename, evaluation: Evaluation, **options
    ):
        "URLSave[url_String, filename_, OptionsPattern[URLSave]]"
        url = url.value
        if filename is None:
            result = urlsave_tmp(url, None, **options)
        elif isinstance(filename, String):
            filename = filename.value
            result = urlsave_tmp(url, filename, **options)
        else:
            evaluation.message("URLSave", "invfile", filename)
            return SymbolFailed
        if result is None:
            return SymbolFailed
        return String(result)
