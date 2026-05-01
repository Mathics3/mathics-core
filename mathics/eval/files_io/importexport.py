"""
Functions for figuring out a filetype or MIME type a given
file path.
"""

import mimetypes
import os.path as osp
from typing import Dict, Final, Optional

from mathics.core.builtin import String, get_option
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue, strip_context
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.files_io.files import eval_Close, eval_Open

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


# Note Matlab and Objective C also use the ".m" extension!
mimetypes.add_type("application/vnd.wolfram.mathematica.package", ".m")

# Do we need the below?
# mimetypes.add_type("application/vnd.wolfram.mathematica.package", ".wl")

# MIMETYPE_TO_SHORTNAME is a mapping form MIME type names to short common names.
# The short common names are typically used as a file extension.

# Here we should have *only* the names used when the name differs
# from mimetypes.guess_extension(mimetype).upper() gives a name different
# from what we have here. This happens for lowercase or mixed-case names.

# TODO: go over to remove names that do not need to be on this list.
MIMETYPE_TO_SHORTNAME: Final[Dict[str, str]] = {
    "application/dbase": "DBF",
    "application/dbf": "DBF",
    "application/dicom": "DICOM",
    "application/eps": "EPS",
    "application/fits": "FITS",
    "application/json": "JSON",
    "application/mathematica": "NB",
    "application/mbox": "MBOX",
    "application/mdb": "MDB",
    "application/msaccess": "MDB",
    "application/octet-stream": "OBJ",
    "application/pcx": "PCX",
    "application/pdf": "PDF",
    "application/postscript": "EPS",
    "application/rss+xml": "RSS",
    "application/rtf": "RTF",
    "application/sla": "STL",
    "application/tga": "TGA",
    "application/vnd.google-earth.kml+xml": "KML",
    "application/vnd.ms-excel": "XLS",
    "application/vnd.ms-pki.stl": "STL",
    "application/vnd.msaccess": "MDB",
    "application/vnd.oasis.opendocument.spreadsheet": "ODS",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",  # nopep8
    "application/vnd.sun.xml.calc": "SXC",
    "application/vnd.wolfram.cdf": "CDF",
    "application/vnd.wolfram.cdf.text": "CDF",
    "application/vnd.wolfram.mathematica.package": "Package",
    "application/x-3ds": "3DS",
    "application/x-cdf": "NASACDF",
    "application/x-eps": "EPS",
    "application/x-flac": "FLAC",
    "application/x-font-bdf": "BDF",
    "application/x-hdf": "HDF",
    "application/x-msaccess": "MDB",
    "application/x-netcdf": "NetCDF",
    "application/x-shockwave-flash": "SWF",
    "application/x-tex": "TeX",  # Also TeX
    "application/xhtml+xml": "XHTML",
    "application/xml": "XML",
    "application/zip": "ZIP",
    "audio/aiff": "AIFF",
    "audio/basic": "AU",  # Also SND
    "audio/midi": "MIDI",
    "audio/x-aifc": "AIFF",
    "audio/x-aiff": "AIFF",
    "audio/x-flac": "FLAC",
    "audio/x-wav": "WAV",
    "chemical/seq-aa-fasta": "FASTA",
    "chemical/seq-na-fasta": "FASTA",
    "chemical/seq-na-fastq": "FASTQ",
    "chemical/seq-na-genbank": "GenBank",
    "chemical/seq-na-sff": "SFF",
    "chemical/x-cif": "CIF",
    "chemical/x-daylight-smiles": "SMILES",
    "chemical/x-hin": "HIN",
    "chemical/x-jcamp-dx": "JCAMP-DX",
    "chemical/x-mdl-molfile": "MOL",
    "chemical/x-mdl-sdf": "SDF",
    "chemical/x-mdl-sdfile": "SDF",
    "chemical/x-mdl-tgf": "TGF",
    "chemical/x-mmcif": "CIF",
    "chemical/x-mol2": "MOL2",
    "chemical/x-mopac-input": "Table",
    "chemical/x-pdb": "PDB",
    "chemical/x-xyz": "XYZ",
    "image/bmp": "BMP",
    "image/eps": "EPS",
    "image/fits": "FITS",
    "image/gif": "GIF",
    "image/jp2": "JPEG2000",
    "image/jpeg": "JPEG",
    "image/pbm": "PNM",
    "image/pcx": "PCX",
    "image/pict": "PICT",
    "image/png": "PNG",
    "image/svg+xml": "SVG",
    "image/tga": "TGA",
    "image/tiff": "TIFF",
    "image/vnd.dxf": "DXF",
    "image/vnd.microsoft.icon": "ICO",
    "image/x-3ds": "3DS",
    "image/x-dxf": "DXF",
    "image/x-exr": "OpenEXR",
    "image/x-icon": "ICO",
    "image/x-ms-bmp": "BMP",
    "image/x-pcx": "PCX",
    "image/x-portable-anymap": "PNM",
    "image/x-portable-bitmap": "PBM",
    "image/x-portable-graymap": "PGM",
    "image/x-portable-pixmap": "PPM",
    "image/x-xbitmap": "XBM",
    "model/vrml": "VRML",
    "model/x-lwo": "LWO",
    "model/x-pov": "POV",
    "model/x3d+xml": "X3D",
    "text/calendar": "ICS",
    "text/comma-separated-values": "CSV",
    "text/csv": "CSV",
    "text/html": "HTML",
    "text/mathml": "MathML",
    "text/plain": "Text",
    "text/rtf": "RTF",
    "text/scriptlet": "SCT",
    "text/tab-separated-values": "TSV",
    "text/texmacs": "Text",
    "text/vnd.graphviz": "DOT",
    "text/x-comma-separated-values": "CSV",
    "text/x-csrc": "C",
    "text/x-tex": "TeX",
    "text/x-vcalendar": "VCS",
    "text/x-vcard": "VCF",
    "text/xml": "XML",
    "video/avi": "AVI",
    "video/quicktime": "QuickTime",
    "video/x-flv": "FLV",
    # None: 'Binary',
}


def filetype_from_path(path: str) -> Optional[String]:
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
        MIME_content_type = from_file(path, mime=True)
        return filetype_from_MIME_content(MIME_content_type)
        if MIME_content_type in MIMETYPE_TO_SHORTNAME:
            short_name = MIMETYPE_TO_SHORTNAME[MIME_content_type]
        else:
            # Map MIME type to a standard extension using the stdlib
            # mimetypes.guess_extension returns things like '.zip' or '.py'
            ext = mimetypes.guess_extension(MIME_content_type)

            if ext:
                # Clean up the extension (remove trailing dot and uppercase)
                short_name = ext.rstrip(".").upper()
            else:
                short_name = MIME_content_type

        return String(short_name)

    except Exception:
        return None


def filetype_from_MIME_content(mime_content_name: str) -> Optional[String]:

    if mime_content_name in MIMETYPE_TO_SHORTNAME:
        short_name = MIMETYPE_TO_SHORTNAME[mime_content_name]
    else:
        # Map MIME type to a standard extension using the stdlib
        # mimetypes.guess_extension returns things like '.zip' or '.py'
        file_extension = mimetypes.guess_extension(mime_content_name)

        if file_extension:
            # Clean up the extension (remove trailing dot and uppercase)
            short_name = file_extension.rstrip(".").upper()

    return String(short_name)


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


def eval_Import(findfile, determine_filetype, elements, evaluation, options, data=None):
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

    elements = [el.get_string_value() for el in elements]

    # Determine file type
    for el in elements:
        if el in IMPORTERS.keys():
            filetype = el
            elements.remove(el)
            break
    else:
        filetype = determine_filetype()

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
                        + list(posts.keys())
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
                )
                if result is None:
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed
                if len(list(result.keys())) == 1 and list(result.keys())[0] == el:
                    evaluation.predetermined_out = current_predetermined_out
                    return list(result.values())[0]
            elif el in posts.keys():
                # TODO: allow use of conditionals
                result = get_results(
                    posts[el],
                    findfile,
                    function_channels,
                    stream_options,
                    custom_options,
                    evaluation,
                )
                if result is None:
                    evaluation.predetermined_out = current_predetermined_out
                    return SymbolFailed
            else:
                if defaults is None:
                    defaults = get_results(
                        default_function,
                        findfile,
                        function_channels,
                        stream_options,
                        custom_options,
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


def get_results(
    tmp_function,
    findfile,
    function_channels,
    stream_options,
    custom_options,
    evaluation,
):
    if function_channels == ListExpression(String("FileNames")):
        joined_options = list(chain(stream_options, custom_options))
        tmpfile = False
        if findfile is None:
            tmpfile = True
            stream = Expression(SymbolOpenWrite).evaluate(evaluation)
            findfile = stream.elements[0]
            if data is not None:
                Expression(SymbolWriteString, data).evaluate(evaluation)
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
            stream = Expression(SymbolStringToStream, data).evaluate(evaluation)
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
        if stream.get_head_name() != "System`InputStream":
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
