"""
Functions for figuring out a filetype or MIME type a given
file path.

Following WMA, we use WMA's custom short name for a mime type.
"""

import mimetypes
import os.path as osp
from itertools import chain
from typing import Dict, Final, Optional

from mathics.core.atoms import ByteArray, String
from mathics.core.builtin import get_option
from mathics.core.convert.expression import to_expression
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue, strip_context
from mathics.core.systemsymbols import (
    SymbolByteArray,
    SymbolFailed,
    SymbolInputStream,
    SymbolNone,
    SymbolRule,
    SymbolStringToStream,
)
from mathics.eval.files_io.files import (
    create_temp_file_with_extension,
    eval_Close,
    eval_Open,
)
from mathics.eval.files_io.filesystem import eval_FileExtension

# Some WMA file types reported by FileFormat do not
# match what the mimetypes (and therefore MIME) extensions
# that would be reported. So we have this table to
# convert these mismatches
MIME_SHORTNAME_TO_WMA: Final[Dict[str, str]] = {"JPG": "JPEG", "TXT": "Text"}

# FIXME: elements of the below dict should be a dataclass.
IMPORTERS = {}

# TODO: This hard-coded dictionary should be
# accessible from the WL API, and be user modifiable.
FILE_EXTENSION_MAP: dict[str, str] = {
    "bmp": "BMP",
    "gif": "GIF",
    "jp2": "JPEG2000",
    "jpg": "JPEG",
    "json": "JSON",
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
    descriptions or WL's codes are not, and can change.
    """

    if not osp.exists(path):
        return None

    # Special case for ".m" files and ".wl' files. Although ".m" could be Objective C,
    # we need it to be Mathematica, for Import and Get.
    # Also ".wl" might not currently be known in libmagic as Wolfram language.
    # So check extension first before relying on libmagic's content analysis.
    file_extension = osp.splitext(path)[1].lower()
    if file_extension in (".m", ".wl"):
        return "WL"

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
    Basic implementation behind FileFormat[filename].
    """
    return String(filetype_from_path(path))


def eval_Import_general(
    findfile: Optional[String],
    determine_filetype,
    elements,
    evaluation: Evaluation,
    options,
    data: Optional[str] = None,
):
    """
    Basic implementation behind most general kind of Import[source, elements, options].
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

    # Determine WMA version of the mime type.
    file_format = None
    for el in elements.copy():
        if el.upper() in IMPORTERS.keys():
            file_format = el.upper()
            elements.remove(el)

    if file_format is None:
        filetype = determine_filetype(data)
        file_format = MIME_SHORTNAME_TO_WMA.get(filetype, filetype).upper()

    if file_format not in IMPORTERS.keys():
        evaluation.message("Import", "fmtnosup", filetype)
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Extract information about the loader used for this MIME type.
    # FIXME: turn into dataclass
    conditionals, import_function_symbol, posts, importer_options = IMPORTERS[
        file_format
    ]

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

    defaults = None

    # Perform the import
    if not elements:
        defaults = perform_import(
            import_function_symbol,
            findfile,
            file_format,
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
            result = defaults.get(default_element.value)
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
            if (
                result := eval_Import_Elements(file_format, evaluation)
            ) is not SymbolNone:
                return result
            # A list of "Elements" is not obtainable via AvailableElements listed when
            # ImportExport`RegisterImport was used. Get a list of the field names via
            # the the "defaults" and "conditional" keys.
            defaults = perform_import(
                import_function_symbol,
                findfile,
                file_format,
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
                result = perform_import(
                    conditionals[el],
                    findfile,
                    file_format,
                    function_channels,
                    stream_options,
                    custom_options,
                    evaluation,
                    options,
                    elements=elements,
                    data=data,
                )
                if result is None:
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed
                if len(list(result.keys())) == 1 and list(result.keys())[0] == el:
                    evaluation.predetermined_out = current_predetermined_out
                    return list(result.values())[0]
            else:
                if defaults is None:
                    defaults = perform_import(
                        import_function_symbol,
                        findfile,
                        file_format,
                        function_channels,
                        stream_options,
                        custom_options,
                        evaluation,
                        options,
                        data=data,
                        elements=elements,
                    )
                    if defaults is None:
                        evaluation.predetermined_out = current_predetermined_out
                        return SymbolFailed
                if el in defaults.keys():
                    evaluation.predetermined_out = current_predetermined_out
                    return defaults[el]
                else:
                    evaluation.message(
                        "Import", "noelem", from_python(el), String(file_format)
                    )
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed


def eval_Import_Elements(file_format: str, evaluation):
    """Basic implementation behind Import[fileformat, Elements].

    This returns the element names that can be used for a specific
    file_format type. We get this from the
    AvailableElements field mentioned when registering an importer.
    """
    filetype = MIME_SHORTNAME_TO_WMA.get(file_format, file_format).upper()

    if filetype not in IMPORTERS.keys():
        evaluation.message("Import", "fmtnosup", String(filetype))
        return SymbolFailed

    # Get information from the registered Importer.
    # In this we've registered, the field names that can be asked for
    # under the option "Elements".
    _, _, _, options = IMPORTERS[filetype]
    return options.get("System`AvailableElements")


def perform_import(
    import_function_symbol: Symbol,
    findfile: Optional[String],
    file_format: str,
    function_channels,
    stream_options,
    custom_options,
    evaluation,
    options,
    data: Optional[str],
    elements: Optional[list] = None,
):
    """ This routine does the import. "import" here means reading a  \
    file or string which has been structured according to a format belonging to a mime type.

    "findfile", if not "None", is the path of a file where the unimported data resides.
    If "findfile" is empty, then "data" will have the string data for that file, and
    this routine will create a temporary file containing the data. The actual importer
    then uses this file.

    "elements", when given, contains the parts or kinds of things that should be extracted.
    Usually, there are custom routines for retrieving an element.

    It is also possible that when a custom element extraction does not
    exist, that the caller will do the filtering after retrieving all of the information.

    This is not advisable when the information inside an element is small compared
    to the information of the entire importable file. For example consider asking
    about the member names or contents of tar file compared to the entire tar file.
    """
    current_predetermined_out = evaluation.predetermined_out
    if function_channels == ListExpression(String("FileNames")):
        joined_options = list(chain(stream_options, custom_options))
        if findfile is None:
            findfile = String(
                create_temp_file_with_extension(data, file_format.lower())
            )

        # FIXME: Some import functions do not support element
        # selection of a collection, just collection retrieval. Here,
        # when a selection is desired, the entire collection is
        # returned, and *then* the element is selected. This is
        # potentially very slow for large collections and selection
        # items that can be retrieved quickly. Until we can come up
        # with a better solution for these kinds import functions, to
        # address this when element selection is requested and doesn't
        # return a different result, we retry without the element
        # selection.
        import_collection_expression = to_expression(
            import_function_symbol, findfile, *joined_options
        )
        if elements is None:
            tmp = import_collection_expression.evaluate(evaluation)
        else:
            import_select_expression = to_expression(
                import_function_symbol, findfile, *elements, *joined_options
            )
            tmp = import_select_expression.evaluate(evaluation)
            if tmp == import_select_expression:
                # Retry by retieving the entire collection.
                # Element selection is done afterwards.
                tmp = import_collection_expression.evaluate(evaluation)

        if tmp is SymbolFailed:
            return SymbolFailed
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
        tmp = Expression(import_function_symbol, stream, *custom_options).evaluate(
            evaluation
        )
        eval_Close(stream, evaluation)
    else:
        # TODO message
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # .get_elements() is more tolerant of the type of "tmp" than
    # ._elements which assumes a Expression type.
    result_elts = tmp.get_elements()
    if not all(expr.has_form("Rule", None) for expr in result_elts):
        evaluation.predetermined_out = current_predetermined_out
        return None

    evaluation.predetermined_out = current_predetermined_out
    return {a.get_string_value(): b for a, b in (x.get_elements() for x in tmp)}


def eval_Import_data_only(
    data: str,
    file_format: Optional[str],
    evaluation: Evaluation,
    options,
):
    """
    Basic implementation behind Import_String[data].
    Here, no elements were given, just a import data string.
    """

    current_predetermined_out = evaluation.predetermined_out

    if file_format is None:
        filetype = filetype_from_mime_content(data)
        file_format = MIME_SHORTNAME_TO_WMA.get(filetype, filetype).upper()

    if file_format not in IMPORTERS.keys():
        evaluation.message("Import", "fmtnosup", String(file_format))
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Load the importer
    _, import_function_symbol, _posts, importer_options = IMPORTERS[file_format]

    stream_options, custom_options = importer_exporter_options(
        importer_options.get("System`Options"), options, "System`Import", evaluation
    )

    function_channels = importer_options.get("System`FunctionChannels")

    if function_channels is None:
        evaluation.message("ImportString", "emptyfch")
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    default_element = importer_options.get("System`DefaultElement")
    if default_element is None:
        # TODO message
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Perform the import
    defaults = perform_import(
        import_function_symbol,
        None,
        file_format,
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
        result = defaults.get(default_element.value)
        if result is None:
            evaluation.message("Import", "noelem", default_element, String(file_format))
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed
        evaluation.predetermined_out = current_predetermined_out
        return result


def eval_Import_source_only(
    findfile: String,
    filetype: str,
    evaluation: Evaluation,
    options,
):
    """
    Basic implementation behind Import[source].
    Here, no elements were given, just a import source.
    """

    current_predetermined_out = evaluation.predetermined_out
    file_format = MIME_SHORTNAME_TO_WMA.get(filetype, filetype).upper()

    if file_format not in IMPORTERS.keys():
        evaluation.message("Import", "fmtnosup", filetype)
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Load the importer
    conditionals, import_function_symbol, posts, importer_options = IMPORTERS[
        file_format
    ]

    stream_options, custom_options = importer_exporter_options(
        importer_options.get("System`Options"), options, "System`Import", evaluation
    )

    function_channels = importer_options.get("System`FunctionChannels")

    if function_channels is None:
        evaluation.message("ImportString", "emptyfch")
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    default_element = importer_options.get("System`DefaultElement")
    if default_element is None:
        # TODO message
        evaluation.predetermined_out = current_predetermined_out
        return SymbolFailed

    # Perform the import.
    defaults = perform_import(
        import_function_symbol,
        findfile,
        file_format,
        function_channels,
        stream_options,
        custom_options,
        evaluation,
        options,
        data=None,
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
            evaluation.message("Import", "noelem", default_element, String(filetype))
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed
        evaluation.predetermined_out = current_predetermined_out
        return result


def infer_file_format(
    filename: str, default_extension: Optional[str] = None
) -> Optional[str]:
    """
    Infer what kind of format filename is in. None is returned if we can't infer
    a format.
    """
    file_extension = eval_FileExtension(filename).lower()
    return FILE_EXTENSION_MAP.get(file_extension, default_extension)
