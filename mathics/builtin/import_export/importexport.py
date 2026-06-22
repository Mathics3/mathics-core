# -*- coding: utf-8 -*-

"""
Import and Export Functions and Variables

"""

import base64
import os
import sys
import tempfile
import urllib.request as request
from itertools import chain
from urllib.error import HTTPError, URLError

from mathics.builtin.import_export.checking import import_setup_check
from mathics.core.atoms import ByteArray
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Integer, Predefined, String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.streams import stream_manager
from mathics.core.symbols import Symbol, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolByteArray,
    SymbolFailed,
    SymbolFileExtension,
    SymbolOpenWrite,
    SymbolOutputStream,
    SymbolToString,
)
from mathics.eval.files_io.files import eval_Close
from mathics.eval.files_io.filesystem import eval_FindFile
from mathics.eval.import_export.importexport import (
    IMPORTERS,
    MIMETYPE_TO_SHORTNAME,
    eval_FileFormat,
    eval_Import,
    eval_Import_Elements,
    filetype_from_mime_content,
    importer_exporter_options,
)

# This tells documentation how to sort this module.
# We want, this to come before specific converters.
sort_order = "mathics.builtin.importing-and-exporting.base"

EXPORTERS = {}


class ExportFormats(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$ExportFormats.html</url>

    <dl>
      <dt>'\$ExportFormats'
      <dd>returns a list of file formats supported by Export.
    </dl>

    >> $ExportFormats
     = {...CSV,...SVG,...Text...}
    """

    name = "$ExportFormats"
    summary_text = "list supported export formats"

    def evaluate(self, evaluation: Evaluation):
        return to_mathics_list(*sorted(EXPORTERS.keys()), elements_conversion_fn=String)


class ImportFormats(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$ImportFormats.html</url>

    <dl>
      <dt>'\$ImportFormats'
      <dd>returns a list of file formats supported by Import.
    </dl>

    >> $ImportFormats
     = {...CSV,...JSON,...Text...}
    """

    name = "$ImportFormats"
    summary_text = "list supported import formats"

    def evaluate(self, evaluation: Evaluation):
        return to_mathics_list(*sorted(IMPORTERS.keys()), elements_conversion_fn=String)


class RegisterImport(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/tutorial/ImportingAndExporting.html#138898786</url>

    <dl>
      <dt>'RegisterImport'["$format$", $defaultFunction$]
      <dd>register '$defaultFunction$' as the default function used when \
          importing from a file of type '"$format$"'.

      <dt>'RegisterImport["$format$", {"$elem_1$" :> $conditionalFunction_1$, \
          "$elem_2$" :> $conditionalFunction_2$, ..., $defaultFunction$}]'
      <dd>registers multiple elements ($elem_1$, ...) and their corresponding \
          converter functions ($conditionalFunction_1$, ...) in addition to the $defaultFunction$.

      <dt>'RegisterImport["$format$", {"$conditionalFunctions$, $defaultFunction$, \
           "$elem_3$" :> $postFunction_3$, "$elem_4$" :> $postFunction_4$, ...}]'
      <dd>also registers additional elements ($elem_3$, ...) whose converters \
          ($postFunction_3$, ...) act on output from the low-level functions.
    </dl>

    First, define the default function used to import the data.
    >> ExampleFormat1Import[filename_String] := Module[{stream, head, data}, stream = OpenRead[filename]; head = ReadList[stream, String, 2]; data = Partition[ReadList[stream, Number], 2]; Close[stream]; {"Header" -> head, "Data" -> data}]

    'RegisterImport' is then used to register the above function to a new data format.
    >> ImportExport`RegisterImport["ExampleFormat1", ExampleFormat1Import]

    >> FilePrint["ExampleData/ExampleData.txt"]
     | Example File Format
     | Created by Angus
     | 0.629452    0.586355
     | 0.711009    0.687453
     | 0.246540    0.433973
     | 0.926871    0.887255
     | 0.825141    0.940900
     | 0.847035    0.127464
     | 0.054348    0.296494
     | 0.838545    0.247025
     | 0.838697    0.436220
     | 0.309496    0.833591

    >> Import["ExampleData/ExampleData.txt", {"ExampleFormat1", "Elements"}]
     = {Data, Header}

    >> Import["ExampleData/ExampleData.txt", {"ExampleFormat1", "Header"}]
     = {Example File Format, Created by Angus}

    Conditional Importer:
    >> ExampleFormat2DefaultImport[filename_String] := Module[{stream, head}, stream = OpenRead[filename]; head = ReadList[stream, String, 2]; Close[stream]; {"Header" -> head}]

    >> ExampleFormat2DataImport[filename_String] := Module[{stream, data}, stream = OpenRead[filename]; Skip[stream, String, 2]; data = Partition[ReadList[stream, Number], 2]; Close[stream]; {"Data" -> data}]

    >> ImportExport`RegisterImport["ExampleFormat2", {"Data" :> ExampleFormat2DataImport, ExampleFormat2DefaultImport}]

    >> Import["ExampleData/ExampleData.txt", {"ExampleFormat2", "Elements"}]
     = {Data, Header}

    >> Import["ExampleData/ExampleData.txt", {"ExampleFormat2", "Header"}]
     = {Example File Format, Created by Angus}

    >> Import["ExampleData/ExampleData.txt", {"ExampleFormat2", "Data"}] // Grid
     = 0.629452   0.586355
     .
     . 0.711009   0.687453
     .
     . 0.24654    0.433973
     .
     . 0.926871   0.887255
     .
     . 0.825141   0.9409
     .
     . 0.847035   0.127464
     .
     . 0.054348   0.296494
     .
     . 0.838545   0.247025
     .
     . 0.838697   0.43622
     .
     . 0.309496   0.833591

    """

    context = "ImportExport`"

    attributes = A_PROTECTED | A_READ_PROTECTED

    # XXX OptionsIssue
    options = {
        "AlphaChannel": "False",
        "AvailableElements": "None",
        "BinaryFormat": "False",
        "DefaultElement": "Automatic",
        "Encoding": "False",
        "Extensions": "{}",
        "FunctionChannels": '{"FileNames"}',
        "HiddenNames": "None",
        "Options": "{}",
        "OriginalChannel": "False",
        "Path": "Automatic",
        "SkipPostImport": "None",
        "Sources": "None",
    }

    rules = {
        "ImportExport`RegisterImport[formatname_String, function_]": "ImportExport`RegisterImport[formatname, function, {}]",
    }
    summary_text = "register an importer for a file format"

    def eval(
        self,
        formatname: String,
        function,
        posts: ListExpression,
        evaluation: Evaluation,
        options,
    ):
        """ImportExport`RegisterImport[formatname_String, function_, posts_List,
        OptionsPattern[ImportExport`RegisterImport]]"""

        if function.has_form("List", None):
            elements = function.get_elements()
        else:
            elements = [function]

        if not (
            len(elements) >= 1
            and isinstance(elements[-1], Symbol)
            and all(x.has_form("RuleDelayed", None) for x in elements[:-1])
        ):
            # TODO: Message
            return SymbolFailed

        conditionals = {
            elem.get_string_value(): expr
            for elem, expr in (x.get_elements() for x in elements[:-1])
        }
        default = elements[-1]

        IMPORTERS[formatname.value] = (
            conditionals,
            default,
            posts,
            options,
        )

        return SymbolNull


class RegisterExport(Builtin):
    """
    <url>:WMA Link:https://reference.wolfram.com/language/tutorial/ImportingAndExporting.html#373283445</url>

    <dl>
      <dt>'RegisterExport'["$format$", $func$]
      <dd>register '$func$' as the default function used when exporting from a file of \
          type '"$format$"'.
    </dl>

    Simple text exporter
    >> ExampleExporter1[filename_, data_, opts___] := Module[{strm = OpenWrite[filename], char = data}, WriteString[strm, char]; Close[strm]]

    >> ImportExport`RegisterExport["ExampleFormat1", ExampleExporter1]

    >> Export["sample.txt", "Encode this string!", "ExampleFormat1"];

    >> FilePrint["sample.txt"]
     | Encode this string!

    >> DeleteFile["sample.txt"]

    Very basic encrypted text exporter:
    >> ExampleExporter2[filename_, data_, opts___] := Module[{strm = OpenWrite[filename], char}, (* TODO: Check data *) char = FromCharacterCode[Mod[ToCharacterCode[data] - 84, 26] + 97]; WriteString[strm, char]; Close[strm]]

    >> ImportExport`RegisterExport["ExampleFormat2", ExampleExporter2]

    >> Export["sample.txt", "encodethisstring", "ExampleFormat2"];

    >> FilePrint["sample.txt"]
     | rapbqrguvffgevat

    >> DeleteFile["sample.txt"]
    """

    summary_text = "register an exporter for a file format"
    context = "ImportExport`"

    options = {
        "AlphaChannel": "False",
        "AvailableElements": "None",
        "BinaryFormat": "False",
        "DefaultElement": "None",
        "Encoding": "False",
        "Extensions": "{}",
        "FunctionChannels": '{"FileNames"}',
        "Options": "{}",
        "OriginalChannel": "False",
        "Path": "Automatic",
        "Sources": "None",
    }

    def eval(self, formatname: String, function, evaluation: Evaluation, options):
        """ImportExport`RegisterExport[formatname_String, function_,
        OptionsPattern[ImportExport`RegisterExport]]"""
        EXPORTERS[formatname.value] = (function, options)

        return SymbolNull


class URLFetch(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/URLFetch.html</url>

    <dl>
      <dt>'URLFetch'[$URL$]
      <dd> Returns the content of $URL$ as a string.
    </dl>
    """

    summary_text = "fetch data from a URL"
    messages = {
        "httperr": "`1` could not be retrieved; `2`.",
    }

    def eval(self, url: String, elements, evaluation: Evaluation, options={}):
        "URLFetch[url_String, elements_, OptionsPattern[]]"

        py_url = url.value

        temp_handle, temp_path = tempfile.mkstemp(suffix="")
        try:
            # some pages need cookies or they will end up in an infinite redirect (i.e. HTTP 303)
            # loop, which prevents the page from getting loaded.
            f = request.build_opener(request.HTTPCookieProcessor).open(py_url)

            try:
                content_type = f.info().get_content_type()
                os.write(temp_handle, f.read())
            finally:
                f.close()

                # on some OS (e.g. Windows) all writers need to be closed before another
                # reader (e.g. Import) can access it. so close the file here.
                os.close(temp_handle)

            def determine_filetype(content_type: str) -> str:
                return MIMETYPE_TO_SHORTNAME.get(content_type, "Text")

            result = eval_Import(
                String(temp_path),
                determine_filetype,
                elements,
                evaluation,
                options,
                data=content_type,
            )
        except HTTPError as e:
            evaluation.message(
                "URLFetch",
                "httperr",
                url,
                "the server returned an HTTP status code of %s (%s)"
                % (e.code, str(e.reason)),
            )
            return SymbolFailed
        except URLError as e:  # see https://docs.python.org/3/howto/urllib2.html
            if hasattr(e, "reason"):
                evaluation.message("URLFetch", "httperr", url, str(e.reason))
            elif hasattr(e, "code"):
                evaluation.message(
                    "URLFetch", "httperr", url, "server returned %s" % e.code
                )
            return SymbolFailed
        except ValueError as e:
            evaluation.message("URLFetch", "httperr", url, str(e))
            return SymbolFailed
        finally:
            try:
                os.close(temp_handle)
            except OSError:
                pass
            os.unlink(temp_path)

        return result


class Import(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Import.html</url>

    <dl>
      <dt>'Import'["$source$"]
      <dd>imports data from a $source$.

      <dt>'Import'["$source$", "$fmt$"]
      <dd>imports file assuming the specified file format.

      <dt>'Import'["$source$", $elements$]
      <dd>imports the specified elements from a file.

      <dt>'Import'["$source$", {"$fmt$", $elements$}]
      <dd>imports the specified elements from a file assuming the specified file format.

      <dt>'Import'["http://$url$", ...] and 'Import'["ftp://$url$", ...]
      <dd>imports from a URL.
    </dl>


    ## Text
    >> Import["ExampleData/ExampleData.txt", "Elements"]
     = {Data, Lines, Plaintext, String, Words}
    >> Import["ExampleData/ExampleData.txt", "Lines"]
     = ...

    ## JSON
    >> Import["ExampleData/colors.json"]
     = {colorsArray ⇾ {{colorName ⇾ black, rgbValue ⇾ (0, 0, 0), hexValue ⇾ #000000}, {colorName ⇾ red, rgbValue ⇾ (255, 0, 0), hexValue ⇾ #FF0000}, {colorName ⇾ green, rgbValue ⇾ (0, 255, 0), hexValue ⇾ #00FF00}, {colorName ⇾ blue, rgbValue ⇾ (0, 0, 255), hexValue ⇾ #0000FF}, {colorName ⇾ yellow, rgbValue ⇾ (255, 255, 0), hexValue ⇾ #FFFF00}, {colorName ⇾ cyan, rgbValue ⇾ (0, 255, 255), hexValue ⇾ #00FFFF}, {colorName ⇾ magenta, rgbValue ⇾ (255, 0, 255), hexValue ⇾ #FF00FF}, {colorName ⇾ white, rgbValue ⇾ (255, 255, 255), hexValue ⇾ #FFFFFF}}}
    """

    messages = {
        "nffil": "File `1` not found during Import.",
        "chtype": (
            "First argument `1` is not a valid file, directory, "
            "or URL specification."
        ),
        "noelem": ("The Import element `1` is not present when importing as `2`."),
        "fmtnosup": "`1` is not a supported Import format.",
        "emptyfch": "Function Channel not defined.",
    }

    options = {
        "$OptionSyntax": "System`Ignore",
    }

    rules = {
        "Import[filename_]": "Import[filename, {}]",
    }

    summary_text = "import elements from a file"

    def eval(self, source, evaluation, options={}):
        "Import[source_, OptionsPattern[]]"
        return self.eval_element_list(source, ListExpression(), evaluation, options)

    def eval_elements_query(self, source, evaluation, options={}):
        """Import[source_, "Elements", OptionsPattern[]]"""
        _, file_format = import_setup_check(source, evaluation)
        return eval_Import_Elements(file_format, evaluation)

    def eval_fmt(self, source, fmt: String, evaluation, options={}):
        "Import[source_, fmt_String, OptionsPattern[]]"
        return self.eval_element_list(source, ListExpression(fmt), evaluation, options)

    def eval_element_list(self, source, elements, evaluation, options={}):
        "Import[source_, elements_List?(AllTrue[#, NotOptionQ]&), OptionsPattern[]]"

        findfile, data = import_setup_check(source, evaluation)
        if findfile is SymbolFailed:
            return SymbolFailed

        def determine_filetype(data: str) -> str:
            return data

        return eval_Import(
            findfile, determine_filetype, elements, evaluation, options, data
        )


class ImportString(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImportString.html</url>

    <dl>
      <dt>'ImportString'["$data$", "$format$"]
      <dd>imports data in the specified format from a string.

      <dt>'ImportString'["$file$", $elements$]
      <dd>imports the specified elements from a file $file$.

      <dt>'ImportString'["$data$"]
      <dd>attempts to determine the format of the string from its content.
    </dl>

    ## Text
    >> str = "Hello!\\n    This is a testing text\\n";
    >> ImportString[str, "Elements"]
     = {Data, Lines, Plaintext, String, Words}
    >> ImportString[str, "Lines"]
     = ...
    """

    messages = {
        "string": "First argument `1` is not a string.",
        "noelem": ("The Import element `1` is not present when importing as `2`."),
        "fmtnosup": "`1` is not a supported Import format.",
    }
    options = {
        "$OptionSyntax": "System`Ignore",
    }
    rules = {}
    summary_text = "import elements from a string"

    def eval(self, data, evaluation, options={}):
        "ImportString[data_, OptionsPattern[]]"
        return self.eval_elements(data, ListExpression(), evaluation, options)

    def eval_element(self, data, element: String, evaluation, options={}):
        "ImportString[data_, element_String, OptionsPattern[]]"

        return self.eval_elements(data, ListExpression(element), evaluation, options)

    def eval_elements(self, data, elements, evaluation, options={}):
        "ImportString[data_, elements_List?(AllTrue[#, NotOptionQ]&), OptionsPattern[]]"
        if not (isinstance(data, String)):
            evaluation.message("ImportString", "string", data)
            return SymbolFailed

        def determine_filetype(py_data: str) -> str:
            return filetype_from_mime_content(py_data)

        return eval_Import(
            None, determine_filetype, elements, evaluation, options, data=data.value
        )


class Export(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Export.html</url>

    <dl>
      <dt>'Export'["$dest.ext$", $expr$]
      <dd>exports $expr$ to a file, using the extension $ext$ to determine the format.

      <dt>'Export'["$dest$", $expr$, "$fmt$"]
      <dd>exports data $expr$ to a file in the specified format, $fmt$.

      <dt>'Export'["$file$", $exprs$, $elems$]
      <dd>exports $exprs$ to a file as elements specified by $elems$.
    </dl>
    """

    messages = {
        "chtype": "First argument `1` is not a valid file specification.",
        "infer": "Cannot infer format of file `1`.",
        "noelem": "`1` is not a valid set of export elements for the `2` format.",
        "emptyfch": "Function Channel not defined.",
        "nffil": "File `1` could not be opened",
    }

    # TODO: This hard-linked dictionary should be
    # replaced by a definition accessible from inside
    # WL
    _extdict = {
        "bmp": "BMP",
        "gif": "GIF",
        "jp2": "JPEG2000",
        "jpg": "JPEG",
        "pcx": "PCX",
        "png": "PNG",
        "ppm": "PPM",
        "pbm": "PBM",
        "pgm": "PGM",
        "tif": "TIFF",
        "txt": "Text",
        "csv": "CSV",
        "svg": "SVG",
        "asy": "asy",
    }

    rules = {
        "Export[filename_, expr_, elems_?NotListQ]": (
            "Export[filename, expr, {elems}]"
        ),
    }

    options = {
        "$OptionSyntax": "System`Ignore",
    }

    summary_text = "export elements to a file"

    # FIXME: move to mathics.eval
    def _check_filename(self, filename, evaluation: Evaluation):
        path = filename.to_python()
        if isinstance(path, str) and path[0] == path[-1] == '"':
            return True
        evaluation.message("Export", "chtype", filename)
        return False

    # FIXME: move to mathics.eval
    def _infer_form(self, filename, evaluation: Evaluation):
        ext = Expression(SymbolFileExtension, filename).evaluate(evaluation)
        ext = ext.get_string_value().lower()
        # TODO: This dictionary should be accessible from the WL API
        # to allow defining specific converters
        return self._extdict.get(ext)

    def eval(self, dest, expr, evaluation, options={}):
        "Export[dest_, expr_, OptionsPattern[Export]]"

        # Check dest
        if not self._check_filename(dest, evaluation):
            return SymbolFailed

        # Determine Format
        form = self._infer_form(dest, evaluation)

        if form is None:
            evaluation.message("Export", "infer", dest)
            return SymbolFailed
        else:
            return self.eval_elements(dest, expr, String(form), evaluation, options)

    def eval_element(self, dest, expr, element: String, evaluation, options={}):
        "Export[dest_, expr_, element_String, OptionsPattern[]]"
        return self.eval_elements(
            dest, expr, ListExpression(element), evaluation, options
        )

    def eval_elements(self, dest, expr, elems, evaluation, options={}):
        "Export[dest_, expr_, elems_List?(AllTrue[#, NotOptionQ]&), OptionsPattern[]]"

        # Check filename
        if not self._check_filename(dest, evaluation):
            return SymbolFailed

        # Process elems {comp* format?, elem1*}
        elements = elems.get_elements()

        format_spec, elems_spec = [], []
        found_form = False
        for element in elements[::-1]:
            element_str = element.get_string_value()

            if not found_form and element_str in EXPORTERS:
                found_form = True

            if found_form:
                format_spec.append(element_str)
            else:
                elems_spec.append(element)

        # Just to be sure that the following calls do not change the state of this property
        current_predetermined_out = evaluation.predetermined_out
        # Infer format if not present
        if not found_form:
            assert format_spec == []
            format_spec = self._infer_form(dest, evaluation)
            if format_spec is None:
                evaluation.message("Export", "infer", dest)
                evaluation.predetermined_out = current_predetermined_out
                return SymbolFailed
            format_spec = [format_spec]
        else:
            assert format_spec != []

        # First item in format_spec is the explicit format.
        # The other elements (if present) are compression formats

        if elems_spec != []:  # FIXME: support elems
            evaluation.message("Export", "noelem", elems, String(format_spec[0]))
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed

        # Load the exporter
        exporter_symbol, exporter_options = EXPORTERS[format_spec[0]]
        function_channels = exporter_options.get("System`FunctionChannels")
        stream_options, custom_options = importer_exporter_options(
            exporter_options.get("System`Options"), options, "System`Export", evaluation
        )

        if function_channels is None:
            evaluation.message("Export", "emptyfch")
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed
        elif function_channels == ListExpression(String("FileNames")):
            exporter_function = Expression(
                exporter_symbol,
                dest,
                expr,
                *list(chain(stream_options, custom_options)),
            )
            res = exporter_function.evaluate(evaluation)
        elif function_channels == ListExpression(String("Streams")):
            stream = Expression(SymbolOpenWrite, dest, *stream_options).evaluate(
                evaluation
            )
            if stream.head not in (SymbolOutputStream, SymbolOpenWrite):
                evaluation.message("Export", "nffil")
                evaluation.predetermined_out = current_predetermined_out
                return SymbolFailed
            exporter_function = Expression(
                exporter_symbol,
                stream,
                expr,
                *list(chain(stream_options, custom_options)),
            )
            res = exporter_function.evaluate(evaluation)
            eval_Close(stream, evaluation)
        if res is SymbolNull:
            evaluation.predetermined_out = current_predetermined_out
            return dest
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed


class ExportString(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ExportString.html</url>

    <dl>
      <dt>'ExportString'[$expr$, $form$]
      <dd>exports $expr$ to a string, in the format $form$.

      <dt>'Export'["$file$", $exprs$, $elems$]
      <dd>exports $exprs$ to a string as elements specified by $elems$.
    </dl>

    >> ExportString[{{1,2,3,4},{3},{2},{4}}, "CSV"]
     = 1,2,3,4
     . 3,
     . 2,
     . 4,

    >> ExportString[{1,2,3,4}, "CSV"]
     = 1,
     . 2,
     . 3,
     . 4,
    >> ExportString[Integrate[f[x],{x,0,2}], "SVG"]//Head
     = String
    """

    messages = {
        "noelem": "`1` is not a valid set of export elements for the `2` format.",
        "emptyfch": "Function Channel not defined.",
    }

    options = {
        "$OptionSyntax": "System`Ignore",
    }

    rules = {
        "ExportString[expr_, elems_?NotListQ]": ("ExportString[expr, {elems}]"),
    }
    summary_text = "export elements to a string"

    def eval_element(self, expr, element: String, evaluation: Evaluation, **options):
        "ExportString[expr_, element_String, OptionsPattern[ExportString]]"
        return self.eval_elements(expr, ListExpression(element), evaluation, **options)

    def eval_elements(self, expr, elems, evaluation: Evaluation, **options):
        "ExportString[expr_, elems_List?(AllTrue[#, NotOptionQ]&), OptionsPattern[ExportString]]"
        # Process elems {comp* format?, elem1*}
        elements = elems.get_elements()
        format_spec, elems_spec = [], []
        found_form = False
        for element in elements[::-1]:
            element_str = element.value

            if not found_form and element_str in EXPORTERS:
                found_form = True

            if found_form:
                format_spec.append(element_str)
            else:
                elems_spec.append(element)

        # Just to be sure that the following evaluations do not change the value of this property
        current_predetermined_out = evaluation.predetermined_out

        # First item in format_spec is the explicit format.
        # The other elements (if present) are compression formats

        if elems_spec != []:  # FIXME: support elems
            if format_spec != []:
                evaluation.message(
                    "ExportString", "noelem", elems, String(format_spec[0])
                )
            else:
                evaluation.message("ExportString", "noelem", elems, String("Unknown"))
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed

        # Load the exporter
        exporter_symbol, exporter_options = EXPORTERS[format_spec[0]]
        function_channels = exporter_options.get("System`FunctionChannels")

        stream_options, custom_options = importer_exporter_options(
            exporter_options.get("System`Options"),
            options,
            "System Options",
            evaluation,
        )

        is_binary = exporter_options["System`BinaryFormat"] is SymbolTrue
        if function_channels is None:
            evaluation.message("ExportString", "emptyfch")
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed
        elif function_channels == ListExpression(String("FileNames")):
            # Generates a temporary file
            import tempfile

            tmpfile = tempfile.NamedTemporaryFile(
                dir=tempfile.gettempdir(),
                prefix="Mathics3-ExportString",
                suffix="." + format_spec[0].lower(),
                delete=True,
            )
            filename = String(tmpfile.name)
            tmpfile.close()
            exporter_function = Expression(
                exporter_symbol,
                filename,
                expr,
                *list(chain(stream_options, custom_options)),
            )
            exportres = exporter_function.evaluate(evaluation)
            if exportres != SymbolNull:
                evaluation.predetermined_out = current_predetermined_out
                return SymbolFailed
            else:
                try:
                    if is_binary:
                        tmpstream = open(filename.value, "rb")
                    else:
                        tmpstream = open(filename.value, "r")
                    res = tmpstream.read()
                    tmpstream.close()
                    if sys.platform not in ("win32",):
                        # On Windows unlink make the second NamedTemporaryFile
                        # fail giving something like:
                        #   [WinError 32] The process cannot access the file because it is being used by another process: ...
                        #    \\AppData\\Local\\Temp\\Mathics3-ExportString35eo_rih.svg'
                        os.unlink(tmpstream.name)
                except Exception as e:
                    print("something went wrong")
                    print(e)
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed
                if is_binary:
                    res = Expression(SymbolByteArray, ByteArray(res))
                else:
                    res = String(str(res))
        elif function_channels == ListExpression(String("Streams")):
            from io import BytesIO, StringIO

            if is_binary:
                pystream = BytesIO()
            else:
                pystream = StringIO()

            name = "ExportString"
            stream = stream_manager.add(name, mode="w", io=pystream)
            outstream = Expression(
                SymbolOutputStream, String("String"), Integer(stream.n)
            )
            exporter_function = Expression(
                exporter_symbol,
                outstream,
                expr,
                *list(chain(stream_options, custom_options)),
            )
            res = exporter_function.evaluate(evaluation)
            if res is SymbolNull:
                if is_binary:
                    res = Expression(SymbolByteArray, ByteArray(pystream.getvalue()))
                else:
                    res = String(str(pystream.getvalue()))
            else:
                res = Symbol("$Failed")
            eval_Close(outstream, evaluation)
        else:
            evaluation.message("ExportString", "emptyfch")
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed

        evaluation.predetermined_out = current_predetermined_out
        return res


class FileFormat(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FileFormat.html</url>

    <dl>
    <dt>'FileFormat'["$name$"]
      <dd>attempts to determine what format 'Import' should use to import specified file.
    </dl>

    >> FileFormat["ExampleData/sunflowers.jpg"]
     = JPEG

    ## UTF-8 Unicode text
    >> FileFormat["ExampleData/EinsteinSzilLetter.txt"]
     = Text

    >> FileFormat["ExampleData/hedy.tif"]
     = TIFF
    """

    summary_text = "determine the file format of a file"

    def eval(self, filename: String, evaluation: Evaluation):
        "FileFormat[filename_String]"

        py_name = filename.value
        if py_name[0] == filename.value[-1] == '"':
            py_name = py_name[1:-1]

        resolved_path = eval_FindFile(py_name)

        if resolved_path is None:
            evaluation.message("FileFormat", "nffil", evaluation.current_expression)
            return SymbolFailed

        return eval_FileFormat(resolved_path.value)


class B64Decode(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/B64Decode.html</url>
    <dl>
    <dt> 'System`Convert`B64Dump`B64Decode'[$string$]
    <dd>Decode  $string$ in Base64 coding to an expression.
    </dl>

    >> System`Convert`B64Dump`B64Decode["R!="]
     : String "R!=" is not a valid b64 encoded string.
     = $Failed
    """

    summary_text = "decode a base64 string"
    context = "System`Convert`B64Dump`"
    name = "B64Decode"

    messages = {
        "b64invalidstr": 'String "`1`" is not a valid b64 encoded string.',
    }

    def eval(self, expr: String, evaluation: Evaluation):
        "System`Convert`B64Dump`B64Decode[expr_String]"
        try:
            clearstring = base64.b64decode(bytearray(expr.value, "utf8")).decode("utf8")
            clearstring = String(str(clearstring))
        except Exception:
            evaluation.message(
                "System`Convert`B64Dump`B64Decode", "b64invalidstr", expr
            )
            return Symbol("$Failed")
        return clearstring


class B64Encode(Builtin):
    """
    <url>
    :WMA link
    :https://reference.wolfram.com/language/ref/B64Encode.html</url>

    <dl>
      <dt> 'System`Convert`B64Dump`B64Encode'[$expr$]
      <dd>Encodes $expr$ in Base64 coding
    </dl>

    >> System`Convert`B64Dump`B64Encode["Hello world"]
     = SGVsbG8gd29ybGQ=
    >> System`Convert`B64Dump`B64Decode[%]
     = Hello world
    >> System`Convert`B64Dump`B64Encode[Integrate[f[x],{x,0,2}]]
     = SW50ZWdyYXRlW2ZbeF0sIHt4LCAwLCAyfV0=
    >> System`Convert`B64Dump`B64Decode[%]
     = Integrate[f[x], {x, 0, 2}]
    """

    context = "System`Convert`B64Dump`"
    name = "B64Encode"
    summary_text = "encode an element as a base64 string"

    def eval(self, expr, evaluation: Evaluation):
        "System`Convert`B64Dump`B64Encode[expr_]"
        if isinstance(expr, String):
            stringtocodify = expr.value
        elif expr.get_head_name() == "System`ByteArray":
            return String(expr._elements[0].__str__())
        else:
            stringtocodify = Expression(SymbolToString, expr).evaluate(evaluation).value
        return String(
            base64.b64encode(bytearray(stringtocodify, "utf8")).decode("utf8")
        )
