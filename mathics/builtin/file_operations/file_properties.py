"""
File Properties
"""

import os
import os.path as osp
import time

from mathics.builtin.exp_structure.size_and_sig import Hash
from mathics.builtin.files_io.files import MathicsOpen
from mathics.core.atoms import Real, String
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin, MessageException
from mathics.core.convert.expression import to_expression
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.streams import path_search
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolAbsoluteTime, SymbolFailed, SymbolNone
from mathics.eval.nevaluator import eval_N

sort_order = "mathics.builtin.file-operations.file_properties"


class FileDate(Builtin):
    """
    <url>
    :WMA link:https://reference.wolfram.com/language/ref/FileDate.html</url>

    <dl>
      <dt>'FileDate'[$file$, $types$]
      <dd>returns the time and date at which the file was last modified.
    </dl>

    >> FileDate["ExampleData/sunflowers.jpg"]
     = ...

    >> FileDate["ExampleData/sunflowers.jpg", "Access"]
     = ...

    >> FileDate["ExampleData/sunflowers.jpg", "Creation"]
     = ...

    >> FileDate["ExampleData/sunflowers.jpg", "Change"]
     = ...

    >> FileDate["ExampleData/sunflowers.jpg", "Modification"]
     = ...

    >>  FileDate["ExampleData/sunflowers.jpg", "Rules"]
     = ...
    """

    messages = {
        "nffil": "File not found during `1`.",
        "datetype": (
            'Date type Fail should be "Access", "Modification", '
            '"Creation" (Windows only), '
            '"Change" (Macintosh and Unix only), or "Rules".'
        ),
    }

    rules = {
        'FileDate[filepath_String, "Rules"]': """{"Access" -> FileDate[filepath, "Access"],
            "Creation" -> FileDate[filepath, "Creation"],
            "Change" -> FileDate[filepath, "Change"],
            "Modification" -> FileDate[filepath, "Modification"]}""",
    }
    summary_text = "get date and time of the last change in a file"

    def eval(self, path, timetype, evaluation):
        "FileDate[path_, timetype_]"
        py_path, _ = path_search(path.to_python()[1:-1])

        if py_path is None:
            if timetype is None:
                evaluation.message("FileDate", "nffil", to_expression("FileDate", path))
            else:
                evaluation.message(
                    "FileDate", "nffil", to_expression("FileDate", path, timetype)
                )
            return

        if timetype is None:
            time_type = "Modification"
        else:
            time_type = timetype.to_python()[1:-1]

        if time_type == "Access":
            result = osp.getatime(py_path)
        elif time_type == "Creation":
            if os.name == "posix":
                return to_expression("Missing", "NotApplicable")
            result = osp.getctime(py_path)
        elif time_type == "Change":
            if os.name != "posix":
                return to_expression("Missing", "NotApplicable")
            result = osp.getctime(py_path)
        elif time_type == "Modification":
            result = osp.getmtime(py_path)
        else:
            evaluation.message("FileDate", "datetype")
            return

        # Offset for system epoch
        epochtime_expr = Expression(
            SymbolAbsoluteTime, String(time.strftime("%Y-%m-%d %H:%M", time.gmtime(0)))
        )
        epochtime_N = eval_N(epochtime_expr, evaluation)
        if epochtime_N is None:
            return None
        epochtime = epochtime_N.to_python()
        result += epochtime

        return to_expression("DateList", Real(result))

    def eval_default(self, path, evaluation):
        "FileDate[path_]"
        return self.eval(path, None, evaluation)


class FileHash(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FileHash.html</url>

    <dl>
      <dt>'FileHash'[$file$]
      <dd>returns an integer hash for the given $file$.

      <dt>'FileHash'[$file$, $type$]
      <dd>returns an integer hash of the specified $type$ for the given $file$.
      <dd>The types supported are "MD5", "Adler32", "CRC32", "SHA", "SHA224", "SHA256", \
          "SHA384", and "SHA512".

      <dt>'FileHash'[$file$, $type$, $format$]
      <dd>gives a hash code in the specified format.
    </dl>

    >> FileHash["ExampleData/sunflowers.jpg"]
     = 109937059621979839952736809235486742106

    >> FileHash["ExampleData/sunflowers.jpg", "MD5"]
     = 109937059621979839952736809235486742106

    >> FileHash["ExampleData/sunflowers.jpg", "Adler32"]
     = 1607049478

    >> FileHash["ExampleData/sunflowers.jpg", "SHA256"]
     = 111619807552579450300684600241129773909359865098672286468229443390003894913065
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    rules = {
        "FileHash[filename_String]": 'FileHash[filename, "MD5", "Integer"]',
        "FileHash[filename_String, hashtype_String]": 'FileHash[filename, hashtype, "Integer"]',
    }
    summary_text = "compute a hash from the content of a file"

    def eval(self, filename, hashtype, format, evaluation):
        "FileHash[filename_String, hashtype_String, format_String]"
        py_filename = filename.get_string_value()

        try:
            with MathicsOpen(py_filename, "rb") as f:
                dump = f.read()
        except IOError:
            evaluation.message("General", "noopen", filename)
            return
        except MessageException as e:
            e.message(evaluation)
            return

        return Hash.compute(
            lambda update: update(dump),
            hashtype.get_string_value(),
            format.get_string_value(),
        )


class FileType(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FileType.html</url>

    <dl>
      <dt>'FileType'["$file$"]
      <dd>gives the type of a file, a string. This is typically 'File', 'Directory' \
          or 'None'.
    </dl>

    >> FileType["ExampleData/sunflowers.jpg"]
     = File
    >> FileType["ExampleData"]
     = Directory
    >> FileType["ExampleData/nonexistent"]
     = None
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }
    summary_text = "get the file extension or file type of a file"

    def eval(self, filename, evaluation):
        "FileType[filename_]"
        if not isinstance(filename, String):
            evaluation.message("FileType", "fstr", filename)
            return
        path = filename.to_python()[1:-1]

        path, _ = path_search(path)

        if path is None:
            return SymbolNone

        if osp.isfile(path):
            return Symbol("File")
        else:
            return Symbol("Directory")


class SetFileDate(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/SetFileDate.html</url>

    <dl>
    <dt>'SetFileDate'["$file$"]
      <dd>set the file access and modification dates of $file$ to the current date.
    <dt>'SetFileDate'["$file$", $date$]
      <dd>set the file access and modification dates of $file$ to the specified date list.
    <dt>'SetFileDate'["$file$", $date$, "$type$"]
      <dd>set the file date of $file$ to the specified date list.
      The "$type$" can be one of "$Access$", "$Creation$", "$Modification$", or 'All'.
    </dl>

    Create a temporary file (for example purposes)
    >> tmpfilename = $TemporaryDirectory <> "/tmp0";
    >> Close[OpenWrite[tmpfilename]];

    >> SetFileDate[tmpfilename, {2002, 1, 1, 0, 0, 0.}, "Access"];

    #> DeleteFile[tmpfilename]
    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of one or " "more characters."
        ),
        "nffil": "File not found during `1`.",
        "fdate": (
            "Date specification should be either the number of seconds "
            "since January 1, 1900 or a {y, m, d, h, m, s} list."
        ),
        "datetype": (
            'Date type a should be "Access", "Modification", '
            '"Creation" (Windows only), or All.'
        ),
        "nocreationunix": (
            "The Creation date of a file cannot be set on " "Macintosh or Unix."
        ),
    }
    summary_text = "set the access/modification time of a file in the filesystem"

    def eval(self, filename, datelist, attribute, evaluation):
        "SetFileDate[filename_, datelist_, attribute_]"

        py_filename = filename.to_python()

        if datelist is None:
            py_datelist = to_expression("DateList").evaluate(evaluation).to_python()
            expr = to_expression("SetFileDate", filename)
        else:
            py_datelist = datelist.to_python()

        if attribute is None:
            py_attr = "All"
            if datelist is not None:
                expr = to_expression("SetFileDate", filename, datelist)
        else:
            py_attr = attribute.to_python()
            expr = to_expression("SetFileDate", filename, datelist, attribute)

        # Check filename
        if not (
            isinstance(py_filename, str) and py_filename[0] == py_filename[-1] == '"'
        ):
            evaluation.message("SetFileDate", "fstr", filename)
            return
        py_filename, _ = path_search(py_filename[1:-1])

        if py_filename is None:
            evaluation.message("SetFileDate", "nffil", expr)
            return SymbolFailed

        # Check datelist
        if not (
            isinstance(py_datelist, list)
            and len(py_datelist) == 6
            and all(isinstance(d, int) for d in py_datelist[:-1])
            and isinstance(py_datelist[-1], float)
        ):
            evaluation.message("SetFileDate", "fdate", expr)

        # Check attribute
        if py_attr not in ['"Access"', '"Creation"', '"Modification"', "All"]:
            evaluation.message("SetFileDate", "datetype")
            return

        epochtime = (
            to_expression(
                "AbsoluteTime", time.strftime("%Y-%m-%d %H:%M", time.gmtime(0))
            )
            .evaluate(evaluation)
            .to_python()
        )

        stattime = to_expression("AbsoluteTime", from_python(py_datelist))
        stattime_N = eval_N(stattime, evaluation)
        if stattime_N is None:
            return

        stattime = stattime_N.to_python() - epochtime

        try:
            os.stat(py_filename)
            if py_attr == '"Access"':
                os.utime(py_filename, (stattime, osp.getatime(py_filename)))
            if py_attr == '"Creation"':
                if os.name == "posix":
                    evaluation.message("SetFileDate", "nocreationunix")
                    return SymbolFailed
                else:
                    # TODO: Note: This is windows only
                    return SymbolFailed
            if py_attr == '"Modification"':
                os.utime(py_filename, (osp.getatime(py_filename), stattime))
            if py_attr == "All":
                os.utime(py_filename, (stattime, stattime))
        except OSError:
            # evaluation.message(...)
            return SymbolFailed

        return SymbolNull

    def eval_with_filename(self, filename, evaluation: Evaluation):
        "SetFileDate[filename_]"
        return self.eval(filename, None, None, evaluation)

    def eval_with_filename_date(self, filename, datelist, evaluation: Evaluation):
        "SetFileDate[filename_, datelist_]"
        return self.eval(filename, datelist, None, evaluation)


# TODO:
# FileFormat, FileFormatQ, FileByteCount, FileSize
