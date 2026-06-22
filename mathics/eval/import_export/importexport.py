"""
Functions for figuring out a filetype or MIME type a given
file path.
"""

import mimetypes
import os.path as osp
from itertools import chain
from typing import Dict, Final, Optional

from mathics.core.atoms import ByteArray, String
from mathics.core.builtin import get_option
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue, strip_context
from mathics.core.systemsymbols import (
    SymbolByteArray,
    SymbolDeleteFile,
    SymbolFailed,
    SymbolInputStream,
    SymbolOpenWrite,
    SymbolRule,
    SymbolStringToStream,
    SymbolWriteString,
)
from mathics.eval.files_io.files import eval_Close, eval_Open

# Some WMA file types reported by FileFormat do not
# match what the mimetypes (and thereofre MIME) extensions
# that would be reported. So we have this table to
# convert these mismatches
MIME_SHORTNAME_TO_WMA: Final[Dict[str, str]] = {"JPG": "JPEG", "TXT": "Text"}

IMPORTERS = {}

try:
    from magic import from_file
except ImportError:

    def from_file(path: str, mime: bool = False) -> str:
        """
        Standard library implementation mimicking magic.from_file.

        Args:
            path: Path to the file.
            mime: If True, returns MIME type. If False, returns a description.
        """
        # Guess the MIME type based on the file extension
        # Example: 'image/jpeg' or 'text/x-python'.
        mime_type, encoding = mimetypes.guess_type(path)

        # Handle cases where the extension is unknown.
        if mime_type is None:
            # Fallback to binary or plain text if the extension is missing.
            mime_type = "application/octet-stream"

        if mime:
            return mime_type

        # Mimic the 'description' behavior of libmagic Since mimetypes
        # doesn't provide descriptions, we provide a clean label.
        description = mime_type.split("/")[-1].replace("x-", "").upper()

        if encoding:
            return f"{description} ({encoding} compressed)"
        return f"{description} data"


mimetypes.init()

# As of 2026, file extension ".wl" is not known to be Mathematica or anything else.
# but ".m" is associated with Mathematica rather than Objective C.
# So we add ".wl" (which probably will be added in the future of MIME mappings),
# and we will make explicit our choice of ".m" for "mathematica package", even though
# that is currently the default.
mimetypes.add_type("application/vnd.wolfram.mathematica.package", ".wl")
# Note Matlab and Objective C also use the ".m" extension!
mimetypes.add_type("application/vnd.wolfram.mathematica.package", ".m")

# MIMETYPE_TO_SHORTNAME is a mapping from a MIME type to a short common
# name.  The short common names are similar, but not quite the same as the
# name of a file extension, uppercased and without a leading dot.

# Also, note that the short name derived from a MIME type is not always the same
# name that WMA uses in builtin FileFormat. In particular, the shortname "JPG" is noted
# in WMA as "JPEG"; "TXT" in WMA is "Text". See MIME_SHORTNAME_TO_WMA for the full list of
# mismatch mappings.

# Some MIME types, like "application/octet-stream", are associated with more than one
# extension. For example "video/mpeg" can have file extensions ".mpeg", ".m1v", ".mpa",
# ".mpe", or "mpg".
#
# The MIME short names given by FileFormat, strips off the "." extension
# and uppercases the extension.
#
# For example in mimetypes.types_map , you may find:
#   "image/png" -> ".png"
# We and WMA use "PNG" as the short name for MIME type "image/png".
#
# Also note that /etc/mimetypes also strips the leading ".",
# and can list multiple extensions for a MIME type. For example:
#   application/postscript	ps ai eps epsi epsf eps2 eps3

MIMETYPE_TO_SHORTNAME: Final[Dict[str, str]] = {
    file_extension.upper().lstrip("."): mime_type
    for mime_type, file_extension in mimetypes.types_map.items()
}


def filetype_from_path(path: str) -> Optional[str]:
    """Classifies what kind of file `path` is.
    A Mathics3 String is return if we can do this and None, if
    there was some sort of error, e.g., `path` is not found.

    It does is using a MIME type, even though the path doesn't have to
    be something received or transmitted over HTTP.

    MIME types are standardized and do not change, while file
    descriptions or WL's codes are not and can change.
    """

    if not osp.exists(path):
        return None

    try:
        mime_content_type = from_file(path, mime=True)
    except Exception:
        return None
    mime_file_extension = filetype_from_mime_content(mime_content_type).lstrip(".")
    return MIME_SHORTNAME_TO_WMA.get(mime_file_extension, mime_file_extension)


def eval_ImageExport(expr, path: Optional[str] = None) -> Expression:
    expr_pil = expr.pil()
    expr_pil.save(path)
    return Expression(SymbolByteArray, ByteArray(expr_pil.tobytes()))


def filetype_from_mime_content(mime_content_name: str) -> str:

    if mime_content_name in MIMETYPE_TO_SHORTNAME:
        short_name = MIMETYPE_TO_SHORTNAME[mime_content_name]
    else:
        # Map MIME type to a standard extension using the stdlib
        # mimetypes.guess_extension returns things like '.zip' or '.py'
        file_extension = mimetypes.guess_extension(mime_content_name)

        if file_extension:
            # Clean up the extension (remove trailing dot and uppercase)
            short_name = file_extension.rstrip(".").upper()
        else:
            return "Text"

    return short_name


def importer_exporter_options(
    available_options, options, builtin_name: str, evaluation
):
    stream_options = []
    custom_options = []
    remaining_options = options.copy()

    if available_options and available_options.has_form("List", None):
        for name in available_options.elements:
            if isinstance(name, String):
                py_name = name.get_string_value()
            elif isinstance(name, Symbol):
                py_name = strip_context(name.get_name())
            else:
                py_name = None

            if py_name:
                option = get_option(remaining_options, py_name, evaluation, pop=True)
                if option is not None:
                    expr = Expression(SymbolRule, String(py_name), option)
                    if py_name == "CharacterEncoding":
                        stream_options.append(expr)
                    else:
                        custom_options.append(expr)

    syntax_option = remaining_options.get("System`$OptionSyntax", None)
    if syntax_option and syntax_option != Symbol("System`Ignore"):
        # warn about unsupported options.
        for name, value in remaining_options.items():
            evaluation.message(
                builtin_name,
                "optx",
                Expression(SymbolRule, String(strip_context(name)), value),
                strip_context(builtin_name),
            )

    return stream_options, custom_options


def eval_FileFormat(path: str) -> String:
    """
    Basic implemenation beind FileFormat[filename].
    """
    return String(filetype_from_path(path))


def eval_Import(
    findfile: Optional[String],
    determine_filetype,
    elements,
    evaluation,
    options,
    data: Optional[str],
):
    """
    Basic implemenation beind Import[].
    """

    current_predetermined_out = evaluation.predetermined_out
    # Check elements
    if elements.has_form("List", None):
        elements = elements.get_elements()
    else:
        elements = [elements]

    for el in elements:
        if not isinstance(el, String):
            evaluation.message("Import", "noelem", el)
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed

    elements = [el.value for el in elements]

    # Determine file type
    for el in elements:
        if el in IMPORTERS.keys():
            filetype = el
            elements.remove(el)
            break
    else:
        filetype = determine_filetype(data)
        filetype = MIME_SHORTNAME_TO_WMA.get(filetype, filetype)

    if filetype not in IMPORTERS.keys():
        evaluation.message("Import", "fmtnosup", filetype)
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Load the importer
    conditionals, default_function, posts, importer_options = IMPORTERS[filetype]

    stream_options, custom_options = importer_exporter_options(
        importer_options.get("System`Options"), options, "System`Import", evaluation
    )

    function_channels = importer_options.get("System`FunctionChannels")

    if function_channels is None:
        # TODO message
        if data is None:
            evaluation.message("Import", "emptyfch")
        else:
            evaluation.message("ImportString", "emptyfch")
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    default_element = importer_options.get("System`DefaultElement")
    if default_element is None:
        # TODO message
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Perform the import
    defaults = None

    if not elements:
        defaults = get_results(
            default_function,
            findfile,
            function_channels,
            stream_options,
            custom_options,
            evaluation,
            options,
            data=data,
        )
        if defaults is None:
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed
        elif defaults is SymbolFailed:
            return SymbolFailed
        if default_element is Symbol("Automatic"):
            evaluation.predetermined_out = current_predetermined_out
            return ListExpression(
                *(
                    Expression(SymbolRule, String(key), defaults[key])
                    for key in defaults.keys()
                )
            )
        else:
            result = defaults.get(default_element.get_string_value())
            if result is None:
                evaluation.message(
                    "Import", "noelem", default_element, String(filetype)
                )
                evaluation.predetermined_out = current_predetermined_out
                return SymbolFailed
            evaluation.predetermined_out = current_predetermined_out
            return result
    else:
        assert len(elements) >= 1
        el = elements[0]
        if el == "Elements":
            defaults = get_results(
                default_function,
                findfile,
                function_channels,
                stream_options,
                custom_options,
                evaluation,
                options,
                data=data,
            )
            if defaults is None:
                evaluation.predetermined_out = current_predetermined_out
                return SymbolFailed
            # Use set() to remove duplicates
            evaluation.predetermined_out = current_predetermined_out
            return from_python(
                sorted(
                    set(
                        list(conditionals.keys())
                        + list(defaults.keys())
                        # + list(posts.keys())
                    )
                )
            )
        else:
            if el in conditionals.keys():
                result = get_results(
                    conditionals[el],
                    findfile,
                    function_channels,
                    stream_options,
                    custom_options,
                    evaluation,
                    options,
                    data=data,
                )
                if result is None:
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed
                if len(list(result.keys())) == 1 and list(result.keys())[0] == el:
                    evaluation.predetermined_out = current_predetermined_out
                    return list(result.values())[0]
            # elif el in posts.keys():
            #     # TODO: allow use of conditionals
            #     result = get_results(
            #         posts[el],
            #         findfile,
            #         function_channels,
            #         stream_options,
            #         custom_options,
            #         evaluation,
            #         options,
            #         data=data,
            #     )
            #     if result is None:
            #         evaluation.predetermined_out = current_predetermined_out
            #         return SymbolFailed
            else:
                if defaults is None:
                    defaults = get_results(
                        default_function,
                        findfile,
                        function_channels,
                        stream_options,
                        custom_options,
                        evaluation,
                        options,
                        data=data,
                    )
                    if defaults is None:
                        evaluation.predetermined_out = current_predetermined_out
                        return SymbolFailed
                if el in defaults.keys():
                    evaluation.predetermined_out = current_predetermined_out
                    return defaults[el]
                else:
                    evaluation.message(
                        "Import", "noelem", from_python(el), String(filetype)
                    )
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed


def eval_Import_Elements(file_format: str, evaluation):
    """
    Basic implemenation beind Import[xxx, Elements].
    """
    filetype = MIME_SHORTNAME_TO_WMA.get(file_format, file_format)

    if filetype not in IMPORTERS.keys():
        evaluation.message("Import", "fmtnosup", String(filetype))
        return SymbolFailed

    # Get information from the registered Importer.
    # In this we've registered, the field names that can be asked for
    # under the option "Elements".
    _, _, _, options = IMPORTERS[filetype]
    return options.get("System`AvailableElements")


def get_results(
    tmp_function,
    findfile: Optional[String],
    function_channels,
    stream_options,
    custom_options,
    evaluation,
    options,
    data: Optional[str],
):
    current_predetermined_out = evaluation.predetermined_out
    if function_channels == ListExpression(String("FileNames")):
        joined_options = list(chain(stream_options, custom_options))
        tmpfile = False
        if findfile is None:
            tmpfile = True
            stream = Expression(SymbolOpenWrite).evaluate(evaluation)
            findfile = stream.elements[0]
            if data is not None:
                Expression(SymbolWriteString, String(data)).evaluate(evaluation)
            else:
                Expression(SymbolWriteString, String("")).evaluate(evaluation)
            eval_Close(stream, evaluation)
        import_expression = Expression(tmp_function, findfile, *joined_options)
        tmp = import_expression.evaluate(evaluation)
        if tmp is SymbolFailed:
            return SymbolFailed
        if tmpfile:
            Expression(SymbolDeleteFile, findfile).evaluate(evaluation)
    elif function_channels == ListExpression(String("Streams")):
        if findfile is None:
            stream = Expression(SymbolStringToStream, String(data)).evaluate(evaluation)
        else:
            mode = "r"
            if options.get("System`BinaryFormat") is SymbolTrue:
                if not mode.endswith("b"):
                    mode += "b"

            encoding_option = options.get("System`CharacterEncoding")
            encoding = (
                encoding_option.value if isinstance(encoding_option, String) else None
            )

            stream = eval_Open(
                name=findfile,
                mode=mode,
                stream_type="InputStream",
                encoding=encoding,
                evaluation=evaluation,
            )
        if stream is None:
            return
        if stream.head is not SymbolInputStream:
            evaluation.message("Import", "nffil")
            evaluation.predetermined_out = current_predetermined_out
            return None
        tmp = Expression(tmp_function, stream, *custom_options).evaluate(evaluation)
        eval_Close(stream, evaluation)
    else:
        # TODO message
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed
    tmp = tmp.get_elements()
    if not all(expr.has_form("Rule", None) for expr in tmp):
        evaluation.predetermined_out = current_predetermined_out
        return None

    # return {a.get_string_value() : b for a,b in map(lambda x:
    # x.get_elements(), tmp)}
    evaluation.predetermined_out = current_predetermined_out
    return {a.get_string_value(): b for a, b in (x.get_elements() for x in tmp)}
