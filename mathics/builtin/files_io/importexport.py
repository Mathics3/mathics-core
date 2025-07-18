# -*- coding: utf-8 -*-

r"""
Importing and Exporting

Many kinds data formats can be read into \\Mathics. Variable <url>
:\$ExportFormats:
/doc/reference-of-built-in-symbols/inputoutput-files-and-filesystem/importing-and-exporting/\$exportformats</url> \
contains a list of file formats that are supported by <url>
:Export:
/doc/reference-of-built-in-symbols/inputoutput-files-and-filesystem/importing-and-exporting/export</url>, \
while <url>
:\$ImportFormats:
/doc/reference-of-built-in-symbols/inputoutput-files-and-filesystem/importing-and-exporting/\$importformats</url> \
does the corresponding thing for <url>
:Import:
/doc/reference-of-built-in-symbols/inputoutput-files-and-filesystem/importing-and-exporting/import</url>.
"""

import base64
import mimetypes
import os
import sys
import urllib.request as request
from itertools import chain
from urllib.error import HTTPError, URLError

from mathics.builtin.pymimesniffer import magic
from mathics.core.atoms import ByteArrayAtom
from mathics.core.attributes import A_NO_ATTRIBUTES, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Integer, Predefined, String, get_option
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.streams import stream_manager
from mathics.core.symbols import Symbol, SymbolNull, SymbolTrue, strip_context
from mathics.core.systemsymbols import (
    SymbolByteArray,
    SymbolFailed,
    SymbolRule,
    SymbolToString,
)
from mathics.eval.files_io.files import eval_Close, eval_Open

# This tells documentation how to sort this module
# Here we are also hiding "file_io" since this can erroneously appear at the top level.
sort_order = "mathics.builtin.importing-and-exporting"

mimetypes.add_type("application/vnd.wolfram.mathematica.package", ".m")

SymbolDeleteFile = Symbol("DeleteFile")
SymbolFileExtension = Symbol("FileExtension")
SymbolFileFormat = Symbol("FileFormat")
SymbolFindFile = Symbol("FindFile")
SymbolOpenWrite = Symbol("OpenWrite")
SymbolOutputStream = Symbol("OutputStream")
SymbolStringToStream = Symbol("StringToStream")
SymbolWriteString = Symbol("WriteString")

# Seems that JSON is not registered on the mathics.net server, so we do it manually here.
# Keep in mind that mimetypes has system-dependent aspects (it inspects "/etc/mime.types" and other files).
mimetypes.add_type("application/json", ".json")

# TODO: Add more file formats

mimetype_dict = {
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

IMPORTERS = {}
EXPORTERS = {}
EXTENSIONMAPPINGS = {
    "*.3ds": "3DS",
    "*.3fr": "Raw",
    "*.aac": "M4A",
    "*.aco": "ACO",
    "*.aif": "AIFF",
    "*.aiff": "AIFF",
    "*.arw": "Raw",
    "*.au": "AU",
    "*.avi": "AVI",
    "*.b64": "BASE64",
    "*.bay": "Raw",
    "*.bdf": "BDF",
    "*.bmp": "BMP",
    "*.bmq": "Raw",
    "*.bson": "BSON",
    "*.byu": "BYU",
    "*.bz2": "BZIP2",
    "*.c": "C",
    "*.cdf": "CDF",
    "*.ch": "SCT",
    "*.cha": "HarwellBoeing",
    "*.che": "HarwellBoeing",
    "*.cif": "CIF",
    "*.cine": "Raw",
    "*.col": "DIMACS",
    "*.col.b": "DIMACS",
    "*.cr2": "Raw",
    "*.cra": "HarwellBoeing",
    "*.cre": "HarwellBoeing",
    "*.crw": "Raw",
    "*.cs1": "Raw",
    "*.csa": "HarwellBoeing",
    "*.cse": "HarwellBoeing",
    "*.css": "CSS",
    "*.csv": "CSV",
    "*.ct": "SCT",
    "*.cua": "HarwellBoeing",
    "*.cue": "HarwellBoeing",
    "*.cur": "CUR",
    "*.cza": "HarwellBoeing",
    "*.cze": "HarwellBoeing",
    "*.dae": "DAE",
    "*.dat": "Table",
    "*.dc2": "Raw",
    "*.dcm": "DICOM",
    "*.dcr": "Raw",
    "*.dib": "BMP",
    "*.dic": "DICOM",
    "*.dicm": "DICOM",
    "*.dif": "DIF",
    "*.dng": "Raw",
    "*.dot": "DOT",
    "*.dxf": "DXF",
    "*.edf": "EDF",
    "*.emf": "EMF",
    "*.eml": "EML",
    "*.enc": "UUE",
    "*.ent": "PDB",
    "*.eps": "EPS",
    "*.epsf": "EPS",
    "*.epsi": "EPS",
    "*.erf": "Raw",
    "*.fa": "FASTA",
    "*.fasta": "FASTA",
    "*.fastq": "FASTQ",
    "*.fcs": "FCS",
    "*.fff": "Raw",
    "*.fit": "FITS",
    "*.fits": "FITS",
    "*.flac": "FLAC",
    "*.flv": "FLV",
    "*.fmu": "FMU",
    "*.fq": "FASTQ",
    "*.fsa": "FASTA",
    "*.g6": "Graph6",
    "*.geojson": "GeoJSON",
    "*.gif": "GIF",
    "*.gml": "Graphlet",
    "*.graphml": "GraphML",
    "*.grb": "GRIB",
    "*.grd": "SurferGrid",
    "*.grib": "GRIB",
    "*.gv": "DOT",
    "*.gw": "LEDA",
    "*.gxl": "GXL",
    "*.gz": "GZIP",
    "*.h5": "HDF5",
    "*.hdf": "HDF",
    "*.hdr": "Raw",
    "*.hmm": "HMMER",
    "*.htm": "HTML",
    # "*.htm": "XHTML",
    "*.html": "HTML",
    # "*.html": "XHTML",
    "*.ia": "Raw",
    "*.icc": "ICC",
    "*.icm": "ICC",
    "*.icns": "ICNS",
    "*.ico": "ICO",
    "*.ics": "ICS",
    "*.ini": "INI",
    "*.j2k": "JPEG2000",
    "*.jar": "ZIP",
    "*.jfif": "JPEG",
    "*.jp2": "JPEG2000",
    "*.jpc": "JPEG2000",
    "*.jpeg": "JPEG",
    "*.jpg": "JPEG",
    "*.json": "JSON",
    "*.jvx": "JVX",
    "*.k25": "Raw",
    "*.kc2": "Raw",
    "*.kdc": "Raw",
    "*.kml": "KML",
    "*.kmz": "KML",
    "*.lgr": "LEDA",
    "*.lmd": "FCS",
    "*.lwo": "LWO",
    "*.m": "Package",
    "*.m4a": "M4A",
    "*.ma": "Maya",
    "*.mat": "MAT",
    "*.mbox": "MBOX",
    "*.mbx": "MBOX",
    "*.mdc": "Raw",
    "*.mef": "Raw",
    "*.mesh": "MESH",
    "*.mgf": "MGF",
    "*.mid": "MIDI",
    "*.mml": "MathML",
    "*.mo": "MO",
    "*.mol": "MOL",
    "*.mol2": "MOL2",
    "*.mos": "Raw",
    "*.mov": "QuickTime",
    "*.mp3": "MP3",
    "*.mpfa": "FASTA",
    "*.mrw": "Raw",
    "*.mtx": "MTX",
    "*.mulaw": "AU",
    "*.mx": "MX",
    "*.nb": "NB",
    "*.nc": "NETCDF",
    "*.ndk": "NDK",
    "*.nef": "Raw",
    "*.net": "PAJEK",
    "*.nex": "NEXUS",
    "*.noff": "NOFF",
    "*.nrw": "Raw",
    "*.nxs": "NEXUS",
    "*.obj": "OBJ",
    "*.ods": "ODS",
    "*.off": "OFF",
    "*.oga": "OGG",
    "*.ogg": "OGG",
    "*.orf": "Raw",
    "*.pbm": "PBM",
    "*.pct": "PICT",
    "*.pcx": "PCX",
    "*.pdb": "PDB",
    "*.pdf": "PDF",
    "*.pef": "Raw",
    "*.pgm": "PGM",
    "*.pha": "HarwellBoeing",
    "*.phe": "HarwellBoeing",
    "*.pic": "PICT",
    # "*.pic": "PXR",
    "*.pict": "PICT",
    "*.ply": "PLY",
    "*.png": "PNG",
    "*.pnm": "PNM",
    "*.pov": "POV",
    "*.ppm": "PPM",
    "*.pra": "HarwellBoeing",
    "*.pre": "HarwellBoeing",
    "*.properties": "JavaProperties",
    "*.psa": "HarwellBoeing",
    "*.pse": "HarwellBoeing",
    "*.pua": "HarwellBoeing",
    "*.pue": "HarwellBoeing",
    "*.pxn": "Raw",
    "*.pxr": "PXR",
    "*.pza": "HarwellBoeing",
    "*.pze": "HarwellBoeing",
    "*.qt": "QuickTime",
    "*.qtk": "Raw",
    "*.raf": "Raw",
    "*.raw": "Raw",
    # "*.raw": "RawBitmap",
    "*.rdc": "Raw",
    "*.rha": "HarwellBoeing",
    "*.rhe": "HarwellBoeing",
    "*.rib": "RIB",
    "*.rle": "RLE",
    "*.rra": "HarwellBoeing",
    "*.rre": "HarwellBoeing",
    "*.rsa": "HarwellBoeing",
    "*.rse": "HarwellBoeing",
    "*.rtf": "RTF",
    "*.rua": "HarwellBoeing",
    "*.rue": "HarwellBoeing",
    "*.rw2": "Raw",
    "*.rwl": "Raw",
    "*.rza": "HarwellBoeing",
    "*.rze": "HarwellBoeing",
    "*.s6": "Sparse6",
    "*.sct": "SCT",
    "*.sdf": "SDF",
    "*.sds": "HDF",
    "*.sff": "SFF",
    "*.sma": "SMA",
    "*.sme": "SME",
    "*.smi": "SMILES",
    "*.snd": "SND",
    "*.sp3": "SP3",
    "*.sr2": "Raw",
    "*.srf": "Raw",
    "*.sti": "Raw",
    "*.stl": "STL",
    "*.svg": "SVG",
    "*.svgz": "SVGZ",
    "*.swf": "SWF",
    "*.tar": "TAR",
    "*.tcx": "TCX",
    # "*.tcx": "TECHEXPLORER",
    "*.tex": "TeX",
    "*.tff": "TIFF",
    "*.tga": "TGA",
    "*.tgf": "TGF",
    "*.tgz": "GZIP",
    "*.tif": "TIFF",
    "*.tiff": "TIFF",
    "*.tsv": "TSV",
    "*.txt": "Text",
    "*.ubj": "UBJSON",
    "*.uue": "UUE",
    "*.vtk": "VTK",
    "*.w64": "Wave64",
    "*.wav": "WAV",
    "*.wdx": "WDX",
    "*.webp": "WebP",
    "*.wl": "Package",
    "*.wlnet": "WLNet",
    "*.wls": "Package",
    "*.wmf": "WMF",
    "*.wmlf": "WMLF",
    "*.wrl": "VRML",
    "*.wxf": "WXF",
    "*.x3d": "X3D",
    "*.x3f": "Raw",
    "*.xbm": "XBM",
    "*.xht": "XHTML",
    "*.xhtml": "XHTML",
    "*.xls": "XLS",
    "*.xlsx": "XLSX",
    # "*.xml": "ExpressionML",
    # "*.xml": "XHTML",
    # "*.xml": "XHTMLMathML",
    "*.xml": "XML",
    "*.xyz": "XYZ",
    "*.zip": "ZIP",
    "*.zpr": "ZPR",
}


FORMATMAPPINGS = {
    "3DS": "3DS",
    "ACO": "ACO",
    "AFFYMETRIX": "Affymetrix",
    "AGILENTMICROARRAY": "AgilentMicroarray",
    "AIFC": "AIFF",
    "AIFF": "AIFF",
    "APACHELOG": "ApacheLog",
    "APPLICATION/ACAD": "DXF",
    "APPLICATION/ACROBAT": "PDF",
    "APPLICATION/BMP": "BMP",
    "APPLICATION/CSV": "CSV",
    "APPLICATION/DICOM": "DICOM",
    "APPLICATION/DXF": "DXF",
    "APPLICATION/EMF": "EMF",
    "APPLICATION/EPS": "EPS",
    "APPLICATION/EXCEL": "XLS",
    # "APPLICATION/EXCEL": "XLSX",
    "APPLICATION/FITS": "FITS",
    "APPLICATION/GEO+JSON": "GeoJSON",
    "APPLICATION/JPG": "JPEG",
    "APPLICATION/JSON": "JSON",
    "APPLICATION/MATHEMATICA": "NB",
    "APPLICATION/MS-EXCEL": "XLS",
    # "APPLICATION/MS-EXCEL": "XLSX",
    "APPLICATION/MSWORD": "DOC",
    "APPLICATION/PCX": "PCX",
    "APPLICATION/PDF": "PDF",
    "APPLICATION/PNG": "PNG",
    "APPLICATION/POSTSCRIPT": "EPS",
    "APPLICATION/RTF": "RTF",
    "APPLICATION/SLA": "STL",
    "APPLICATION/TAR": "TAR",
    "APPLICATION/TGA": "TGA",
    "APPLICATION/TIF": "TIFF",
    "APPLICATION/TIFF": "TIFF",
    "APPLICATION/TXT": "Text",
    "APPLICATION/UBJSON": "UBJSON",
    "APPLICATION/VCARD": "VCF",
    "APPLICATION/VND.MS-EXCEL": "XLS",
    # "APPLICATION/VND.MS-EXCEL": "XLSX",
    "APPLICATION/VND.OASIS.OPENDOCUMENT.SPREADSHEET": "ODS",
    "APPLICATION/VND.PDF": "PDF",
    "APPLICATION/VND.TCPDUMP.PCAP": "PCAP",
    "APPLICATION/VND.WOLFRAM.CDF.TEXT": "CDF",
    "APPLICATION/VND.WOLFRAM.MATHEMATICA": "NB",
    "APPLICATION/VND.WOLFRAM.MATHEMATICA.PACKAGE": "Package",
    "APPLICATION/VND.WOLFRAM.PLAYER": "NB",
    "APPLICATION/WARC": "WARC",
    "APPLICATION/WMF": "WMF",
    "APPLICATION/X-3DS": "3DS",
    "APPLICATION/X-AUTOCAD": "DXF",
    "APPLICATION/X-BMP": "BMP",
    "APPLICATION/X-BZIP": "BZIP2",
    "APPLICATION/X-DOS_MS_EXCEL": "XLS",
    # "APPLICATION/X-DOS_MS_EXCEL": "XLSX",
    "APPLICATION/X-DXF": "DXF",
    "APPLICATION/X-EMF": "EMF",
    "APPLICATION/X-EPS": "EPS",
    "APPLICATION/X-EXCEL": "XLS",
    # "APPLICATION/X-EXCEL": "XLSX",
    "APPLICATION/X-GZIP": "GZIP",
    "APPLICATION/X-GZIP-COMPRESSED": "GZIP",
    "APPLICATION/X-HDF": "HDF",
    "APPLICATION/X-HDF5": "HDF5",
    "APPLICATION/X-JPG": "JPEG",
    "APPLICATION/X-LATEX": "LaTeX",
    "APPLICATION/X-MS-EXCEL": "XLS",
    # "APPLICATION/X-MS-EXCEL": "XLSX",
    "APPLICATION/X-MSEXCEL": "XLS",
    # "APPLICATION/X-MSEXCEL": "XLSX",
    "APPLICATION/X-MSMETAFILE": "WMF",
    "APPLICATION/X-PCAPNG": "PCAP",
    "APPLICATION/X-PCX": "PCX",
    "APPLICATION/X-PDF": "PDF",
    "APPLICATION/X-PNG": "PNG",
    "APPLICATION/X-RTF": "RTF",
    "APPLICATION/X-SHOCKWAVE-FLASH": "SWF",
    "APPLICATION/X-TAR": "TAR",
    "APPLICATION/X-TARGA": "TGA",
    "APPLICATION/X-TEX": "TeX",
    "APPLICATION/X-TGA": "TGA",
    "APPLICATION/X-TIF": "TIFF",
    "APPLICATION/X-TIFF": "TIFF",
    "APPLICATION/X-TROFF-MSVIDEO": "AVI",
    "APPLICATION/X-VND.OASIS.OPENDOCUMENT.SPREADSHEET": "ODS",
    "APPLICATION/X-WIN-BITMAP": "BMP",
    "APPLICATION/X-WINZIP": "ZIP",
    "APPLICATION/X-WMF": "WMF",
    "APPLICATION/X-XLS": "XLS",
    # "APPLICATION/X-XLS": "XLSX",
    "APPLICATION/X-ZIP": "ZIP",
    "APPLICATION/X-ZIP-COMPRESSED": "ZIP",
    "APPLICATION/XHTML+XML": "XHTML",
    "APPLICATION/XML": "XML",
    "APPLICATION/ZIP": "ZIP",
    "ARCGRID": "ArcGRID",
    "AU": "AU",
    "AUDIO/3GPP": "M4A",
    "AUDIO/3GPP2": "M4A",
    "AUDIO/AAC": "M4A",
    "AUDIO/AACP": "M4A",
    "AUDIO/AIFF": "AIFF",
    "AUDIO/BASIC": "AU",
    "AUDIO/MP3": "MP3",
    "AUDIO/MP4": "M4A",
    "AUDIO/MP4A-LATM": "M4A",
    "AUDIO/MPEG": "MP3",
    "AUDIO/MPEG3": "MP3",
    "AUDIO/MPEG4-GENERIC": "M4A",
    "AUDIO/MPG": "MP3",
    "AUDIO/OGG": "OGG",
    "AUDIO/VORBIS": "OGG",
    "AUDIO/WAV": "WAV",
    "AUDIO/WAVE": "WAV",
    "AUDIO/X-AIFF": "AIFF",
    "AUDIO/X-AU": "AU",
    "AUDIO/X-MP3": "MP3",
    "AUDIO/X-MPEG": "MP3",
    "AUDIO/X-MPEG3": "MP3",
    "AUDIO/X-MPEGAUDIO": "MP3",
    "AUDIO/X-MPG": "MP3",
    "AUDIO/X-ULAW": "AU",
    "AUDIO/X-WAV": "WAV",
    "AVI": "AVI",
    "Agilent": "AgilentMicroarray",
    "BASE64": "Base64",
    "BDF": "BDF",
    "BINARY": "Binary",
    "BIT": "Bit",
    "BMP": "BMP",
    "BSON": "BSON",
    "BYTE": "Byte",
    "BYU": "BYU",
    "BZ2": "BZIP2",
    "BZIP": "BZIP2",
    "BZIP2": "BZIP2",
    "C": "C",
    "CDED": "CDED",
    "CDF": "CDF",
    "CHARACTER16": "Character16",
    "CHARACTER8": "Character8",
    "CIF": "CIF",
    "COMPLEX128": "Complex128",
    "COMPLEX256": "Complex256",
    "COMPLEX64": "Complex64",
    "CSV": "CSV",
    "CUR": "CUR",
    "DAE": "DAE",
    "DBF": "DBF",
    "DICOM": "DICOM",
    "DIF": "DIF",
    "DIMACS": "DIMACS",
    "DIRECTORY": "Directory",
    "DOT": "DOT",
    "DXF": "DXF",
    "EDF": "EDF",
    "EMF": "EMF",
    "EML": "EML",
    "ENHANCEDMETAFILE": "EMF",
    "EPS": "EPS",
    "EXPRESSIONJSON": "ExpressionJSON",
    "EXPRESSIONML": "ExpressionML",
    "Excel": "XLS",
    "FASTA": "FASTA",
    "FASTQ": "FASTQ",
    "FCS": "FCS",
    "FITS": "FITS",
    "FLAC": "FLAC",
    "FLASH": "SWF",
    "FLV": "FLV",
    "FMU": "FMU",
    "Flash": "SWF",
    "GENBANK": "GenBank",
    "GEOJSON": "GeoJSON",
    "GEOTIFF": "GeoTIFF",
    "GIF": "GIF",
    "GPX": "GPX",
    "GRAPH6": "Graph6",
    "GRAPHLET": "Graphlet",
    "GRAPHML": "GraphML",
    "GRIB": "GRIB",
    "GTOPO30": "GTOPO30",
    "GXL": "GXL",
    "GZ": "GZIP",
    "GZIP": "GZIP",
    "GraphWin": "LEDA",
    "HARWELLBOEING": "HarwellBoeing",
    "HDF": "HDF",
    "HDF5": "HDF5",
    "HIN": "HIN",
    "HTML": "HTML",
    "HTMLFRAGMENT": "HTMLFragment",
    "HTMLMathML": "XHTMLMathML",
    "HTTPREQUEST": "HTTPRequest",
    "HTTPRESPONSE": "HTTPResponse",
    "ICC": "ICC",
    "ICNS": "ICNS",
    "ICO": "ICO",
    "ICS": "ICS",
    "IMAGE/BITMAP": "BMP",
    "IMAGE/BMP": "BMP",
    "IMAGE/DXF": "DXF",
    "IMAGE/EPS": "EPS",
    "IMAGE/FITS": "FITS",
    "IMAGE/GIF": "GIF",
    "IMAGE/JP2": "JPEG2000",
    "IMAGE/JPEG": "JPEG",
    "IMAGE/JPEG2000": "JPEG2000",
    "IMAGE/JPEG2000-IMAGE": "JPEG2000",
    "IMAGE/JPG": "JPEG",
    "IMAGE/MS-BMP": "BMP",
    "IMAGE/PCX": "PCX",
    "IMAGE/PICT": "PICT",
    "IMAGE/PJPEG": "JPEG",
    "IMAGE/PNG": "PNG",
    "IMAGE/SVG+XML": "SVG",
    "IMAGE/SVG-XML": "SVG",
    "IMAGE/TARGA": "TGA",
    "IMAGE/TGA": "TGA",
    "IMAGE/TIF": "TIFF",
    "IMAGE/TIFF": "TIFF",
    "IMAGE/VND.DXF": "DXF",
    "IMAGE/VND.MICROSOFT.ICON": "ICO",
    "IMAGE/WMF": "WMF",
    "IMAGE/X-3DS": "3DS",
    "IMAGE/X-AUTOCAD": "DXF",
    "IMAGE/X-BITMAP": "BMP",
    "IMAGE/X-BMP": "BMP",
    "IMAGE/X-DXF": "DXF",
    "IMAGE/X-EMF": "EMF",
    "IMAGE/X-EPS": "EPS",
    "IMAGE/X-EXR": "OpenEXR",
    "IMAGE/X-JPEG2000-IMAGE": "JPEG2000",
    "IMAGE/X-MGX-EMF": "EMF",
    "IMAGE/X-MS-BMP": "BMP",
    "IMAGE/X-PBM": "PBM",
    "IMAGE/X-PC-PAINTBRUCH": "PCX",
    "IMAGE/X-PCX": "PCX",
    "IMAGE/X-PGM": "PGM",
    "IMAGE/X-PICT": "PICT",
    "IMAGE/X-PNG": "PNG",
    "IMAGE/X-PNM": "PNM",
    "IMAGE/X-PORTABLE-ANYMAP": "PNM",
    "IMAGE/X-PORTABLE-BITMAP": "PBM",
    "IMAGE/X-PORTABLE-GRAYMAP": "PGM",
    "IMAGE/X-PORTABLE-PIXMAP": "PPM",
    "IMAGE/X-PPM": "PPM",
    "IMAGE/X-TARGA": "TGA",
    "IMAGE/X-TGA": "TGA",
    "IMAGE/X-TIF": "TIFF",
    "IMAGE/X-TIFF": "TIFF",
    "IMAGE/X-WIN-BITMAP": "BMP",
    "IMAGE/X-WIN-METAFILE": "WMF",
    "IMAGE/X-WINDOWS-BITMAP": "BMP",
    "IMAGE/X-WMF": "WMF",
    "IMAGE/X-XBITMAP": "EMF",
    # "IMAGE/X-XBITMAP": "XBM",
    "IMAGE/X-XBM": "XBM",
    "IMAGE/XBM": "XBM",
    "INI": "Ini",
    "INTEGER128": "Integer128",
    "INTEGER16": "Integer16",
    "INTEGER24": "Integer24",
    "INTEGER32": "Integer32",
    "INTEGER64": "Integer64",
    "INTEGER8": "Integer8",
    "JAR": "ZIP",
    "JAVAPROPERTIES": "JavaProperties",
    "JAVASCRIPTEXPRESSION": "JavaScriptExpression",
    "JCAMP-DX": "JCAMP-DX",
    "JCAMPDX": "JCAMP-DX",
    "JPEG": "JPEG",
    "JPEG2000": "JPEG2000",
    "JPG": "JPEG",
    "JSON": "JSON",
    "JVX": "JVX",
    "KML": "KML",
    "LATEX": "LaTeX",
    "LEDA": "LEDA",
    "LIST": "List",
    "LWO": "LWO",
    "M4A": "M4A",
    "MAT": "MAT",
    "MATHML": "MathML",
    "MAYA": "Maya",
    "MBOX": "MBOX",
    "MCTT": "MCTT",
    "MDB": "MDB",
    "MESH": "MESH",
    "MESSAGE/RFC822": "EML",
    "METAFILE": "WMF",
    "MGF": "MGF",
    "MIDI": "MIDI",
    "MMCIF": "MMCIF",
    "MO": "MO",
    "MODEL/X-POV": "POV",
    "MOL": "MOL",
    "MOL2": "MOL2",
    "MP3": "MP3",
    "MPS": "MPS",
    "MTP": "MTP",
    "MTX": "MTX",
    "MULTIPART/X-GZIP": "GZIP",
    "MULTIPART/X-TAR": "TAR",
    "MULTIPART/X-ZIP": "ZIP",
    "MX": "MX",
    "MXNET": "MXNet",
    "MatrixMarket": "MTX",
    "Metafile": "WMF",
    "MuLaw": "AU",
    "NASACDF": "NASACDF",
    "NB": "NB",
    "NDK": "NDK",
    "NETCDF": "NetCDF",
    "NEXUS": "NEXUS",
    "NOFF": "NOFF",
    "OBJ": "OBJ",
    "ODS": "ODS",
    "OFF": "OFF",
    "OGG": "OGG",
    "OPENEXR": "OpenEXR",
    "PACKAGE": "Package",
    "PAJEK": "Pajek",
    "PBM": "PBM",
    "PCAP": "PCAP",
    "PCX": "PCX",
    "PDB": "PDB",
    "PDF": "PDF",
    "PGM": "PGM",
    "PHPINI": "PHPIni",
    "PICT": "PICT",
    "PLY": "PLY",
    "PNG": "PNG",
    "PNM": "PNM",
    "POV": "POV",
    "PPM": "PPM",
    "PXR": "PXR",
    "PYTHONEXPRESSION": "PythonExpression",
    "QUICKTIME": "QuickTime",
    "RAW": "Raw",
    "RAWBITMAP": "RawBitmap",
    "RAWJSON": "RawJSON",
    "REAL128": "Real128",
    "REAL32": "Real32",
    "REAL64": "Real64",
    "RIB": "RIB",
    "RICHTEXT": "RTF",
    "RLE": "RLE",
    "RSS": "RSS",
    "RTF": "RTF",
    "RichText": "RTF",
    "SCT": "SCT",
    "SDF": "SDF",
    "SDTS": "SDTS",
    "SDTSDEM": "SDTSDEM",
    "SFF": "SFF",
    "SHP": "SHP",
    "SMA": "SMA",
    "SME": "SME",
    "SMILES": "SMILES",
    "SND": "SND",
    "SP3": "SP3",
    "SPARSE6": "Sparse6",
    "STL": "STL",
    "STRING": "String",
    "SURFERGRID": "SurferGrid",
    "SVG": "SVG",
    "SWF": "SWF",
    "SXC": "SXC",
    "TABLE": "Table",
    "TAR": "TAR",
    "TERMINATEDSTRING": "TerminatedString",
    "TEX": "TeX",
    "TEXFRAGMENT": "TeXFragment",
    "TEXT": "Text",
    "TEXT/CALENDAR": "ICS",
    # "TEXT/CALENDAR": "VCS",
    "TEXT/COMMA-SEPARATED-VALUES": "CSV",
    "TEXT/CSV": "CSV",
    "TEXT/HTML": "HTML",
    "TEXT/PDF": "PDF",
    "TEXT/PLAIN": "Text",
    "TEXT/RICHTEXT": "RTF",
    "TEXT/RTF": "RTF",
    "TEXT/TAB-SEPARATED-VALUES": "TSV",
    "TEXT/X-COMMA-SEPARATED-VALUES": "CSV",
    "TEXT/X-PDF": "PDF",
    "TEXT/X-VCARD": "VCF",
    "TEXT/XML": "XML",
    "TGA": "TGA",
    "TGF": "TGF",
    "TGZ": "GZIP",
    "TIFF": "TIFF",
    "TIGER": "TIGER",
    "TLE": "TLE",
    "TSV": "TSV",
    "UBJSON": "UBJSON",
    "UNSIGNEDINTEGER128": "UnsignedInteger128",
    "UNSIGNEDINTEGER16": "UnsignedInteger16",
    "UNSIGNEDINTEGER24": "UnsignedInteger24",
    "UNSIGNEDINTEGER32": "UnsignedInteger32",
    "UNSIGNEDINTEGER64": "UnsignedInteger64",
    "UNSIGNEDINTEGER8": "UnsignedInteger8",
    "USGSDEM": "USGSDEM",
    "UUE": "UUE",
    "VCARD": "VCF",
    "VCF": "VCF",
    "VCS": "VCS",
    "VIDEO/AVI": "AVI",
    "VIDEO/MSVIDEO": "AVI",
    "VIDEO/QUICKTIME": "QuickTime",
    "VIDEO/X-FLV": "FLV",
    "VIDEO/X-MATROSKA": "MKV",
    "VIDEO/X-MSVIDEO": "AVI",
    "VIDEOFRAMES": "VideoFrames",
    "VRML": "VRML",
    "VTK": "VTK",
    "WARC": "WARC",
    "WAV": "WAV",
    "WAVE": "WAV",
    "WAVE64": "Wave64",
    "WDX": "WDX",
    "WEBP": "WebP",
    "WINDOWS/METAFILE": "WMF",
    "WLNET": "WLNet",
    "WMF": "WMF",
    "WMLF": "WMLF",
    "WXF": "WXF",
    "X3D": "X3D",
    "XBITMAP": "XBM",
    "XBM": "XBM",
    "XHTML": "XHTML",
    "XHTMLMATHML": "XHTMLMathML",
    "XLS": "XLS",
    "XLSX": "XLSX",
    "XML": "XML",
    "XPORT": "XPORT",
    "XYZ": "XYZ",
    "ZIP": "ZIP",
    "ZPR": "ZPR",
    "ZZ-APPLICATION/ZZ-WINASSOC-DXF": "DXF",
    "ZZ-APPLICATION/ZZ-WINASSOC-PCX": "PCX",
    "ZZ-APPLICATION/ZZ-WINASSOC-WMF": "WMF",
    # "ZZ-APPLICATION/ZZ-WINASSOC-XLS": "XLS",
    # "ZZ-APPLICATION/ZZ-WINASSOC-XLS": "XLSX",
    "vCard": "VCF",
}


def _importer_exporter_options(
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
                Expression(SymbolRule, strip_context(name), value),
                strip_context(builtin_name),
            )

    return stream_options, custom_options


class ConverterDumpsExtensionMappings(Predefined):
    r"""
    ## <url>:internal native symbol:</url>

    <dl>
      <dt>'System`ConvertersDump`\$ExtensionMappings'
      <dd>Returns a list of associations between file extensions and file types.
    </dl>

    The format associated to the extension "*.jpg"
    >> "*.jpg"/. System`ConvertersDump`$ExtensionMappings
     = JPEG

    """

    attributes = A_NO_ATTRIBUTES
    context = "System`ConvertersDump`"
    name = "$ExtensionMappings"
    summary_text = "get associations file extensions and their abstract file type"

    def evaluate(self, evaluation: Evaluation):
        return from_python(EXTENSIONMAPPINGS)


class ConverterDumpsFormatMappings(Predefined):
    r"""
    ## <url>:internal native symbol:</url>

    <dl>
      <dt>'System`ConverterDump\$FormatMappings'
      <dd>Returns a list of associations between file extensions and file types.
    </dl>

    The list of MIME types associated to the extension JPEG:
    >> Select[System`ConvertersDump`$FormatMappings,(#1[[2]]=="JPEG")&][[All, 1]]
     = ...

    """

    attributes = A_NO_ATTRIBUTES
    context = "System`ConvertersDump`"
    # TODO: Check why this does not follows the convention of
    # starting words in identifiers with caps.
    name = "$FormatMappings"
    summary_text = "get associations between mime types their abstract file type"

    def evaluate(self, evaluation: Evaluation):
        return from_python(FORMATMAPPINGS)


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
    <url>:WMA link:https://reference.wolfram.com/language/ref/$ImportFormats.html</url>

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
    ## <url>:internal native symbol:</url>

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
        "Options": "{}",
        "OriginalChannel": "False",
        "Path": "Automatic",
        "Sources": "None",
    }

    rules = {
        "ImportExport`RegisterImport[formatname_String, function_]": "ImportExport`RegisterImport[formatname, function, {}]",
    }
    summary_text = "register an importer for a file format"

    def eval(self, formatname, function, posts, evaluation: Evaluation, options):
        """ImportExport`RegisterImport[formatname_String, function_, posts_,
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
        posts = {}

        IMPORTERS[formatname.get_string_value()] = (
            conditionals,
            default,
            posts,
            options,
        )

        return SymbolNull


class RegisterExport(Builtin):
    """
    ## <url>:internal native symbol:</url>

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

        import os
        import tempfile

        py_url = url.get_string_value()

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
                # reader (e.g. Import._import) can access it. so close the file here.
                os.close(temp_handle)

            def determine_filetype():
                return mimetype_dict.get(content_type)

            result = Import._import(
                temp_path, determine_filetype, elements, evaluation, options
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
      <dt>'Import'["$file$"]
      <dd>imports data from a file.

      <dt>'Import'["$file$", "$fmt$"]
      <dd>imports file assuming the specified file format.

      <dt>'Import'["$file$", $elements$]
      <dd>imports the specified elements from a file.

      <dt>'Import'["$file$", {"$fmt$", $elements$}]
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
     = {colorsArray -> {{colorName -> black, rgbValue -> (0, 0, 0), hexValue -> #000000}, {colorName -> red, rgbValue -> (255, 0, 0), hexValue -> #FF0000}, {colorName -> green, rgbValue -> (0, 255, 0), hexValue -> #00FF00}, {colorName -> blue, rgbValue -> (0, 0, 255), hexValue -> #0000FF}, {colorName -> yellow, rgbValue -> (255, 255, 0), hexValue -> #FFFF00}, {colorName -> cyan, rgbValue -> (0, 255, 255), hexValue -> #00FFFF}, {colorName -> magenta, rgbValue -> (255, 0, 255), hexValue -> #FF00FF}, {colorName -> white, rgbValue -> (255, 255, 255), hexValue -> #FFFFFF}}}
    """

    messages = {
        "nffil": "File not found during Import.",
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

    def eval(self, filename, evaluation, options={}):
        "Import[filename_, OptionsPattern[]]"
        return self.eval_elements(filename, ListExpression(), evaluation, options)

    def eval_element(self, filename, element: String, evaluation, options={}):
        "Import[filename_, element_String, OptionsPattern[]]"
        return self.eval_elements(
            filename, ListExpression(element), evaluation, options
        )

    def eval_elements(self, filename, elements, evaluation, options={}):
        "Import[filename_, elements_List?(AllTrue[#, NotOptionQ]&), OptionsPattern[]]"
        # Check filename
        path = filename.to_python()
        if not (isinstance(path, str) and path[0] == path[-1] == '"'):
            evaluation.message("Import", "chtype", filename)
            return SymbolFailed

        # Load local file
        findfile = Expression(SymbolFindFile, filename).evaluate(evaluation)

        if findfile is SymbolFailed:
            evaluation.message("Import", "nffil")
            return findfile

        def determine_filetype():
            return (
                Expression(SymbolFileFormat, findfile)
                .evaluate(evaluation=evaluation)
                .get_string_value()
            )

        return self._import(findfile, determine_filetype, elements, evaluation, options)

    @staticmethod
    def _import(findfile, determine_filetype, elements, evaluation, options, data=None):
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

        stream_options, custom_options = _importer_exporter_options(
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

        def get_results(tmp_function, findfile):
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
                    stream = None
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
                        encoding_option.value
                        if isinstance(encoding_option, String)
                        else None
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
                tmp = Expression(tmp_function, stream, *custom_options).evaluate(
                    evaluation
                )
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

        # Perform the import
        defaults = None

        if not elements:
            defaults = get_results(default_function, findfile)
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
                defaults = get_results(default_function, findfile)
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
                    result = get_results(conditionals[el], findfile)
                    if result is None:
                        evaluation.predetermined_out = current_predetermined_out
                        return SymbolFailed
                    if len(list(result.keys())) == 1 and list(result.keys())[0] == el:
                        evaluation.predetermined_out = current_predetermined_out
                        return list(result.values())[0]
                elif el in posts.keys():
                    # TODO: allow use of conditionals
                    result = get_results(posts[el])
                    if result is None:
                        evaluation.predetermined_out = current_predetermined_out
                        return SymbolFailed
                else:
                    if defaults is None:
                        defaults = get_results(default_function, findfile)
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


class ImportString(Import):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImportString.html</url>

    <dl>
      <dt>'ImportString'["$data$", "$format$"]
      <dd>imports data in the specified format from a string.

      <dt>'ImportString'["$file$", $elements$]
      <dd>imports the specified elements from a string.

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
        path = data.value

        def determine_filetype():
            if not FileFormat.detector:
                loader = magic.MagicLoader()
                loader.load()
                FileFormat.detector = magic.MagicDetector(loader.mimetypes)
            mime = set(FileFormat.detector.match("", data=data.to_python()))

            result = []
            for key in mimetype_dict.keys():
                if key in mime:
                    result.append(mimetype_dict[key])

            # The following fixes an extremely annoying behaviour on some (not all)
            # installations of Windows, where we end up classifying .csv files als XLS.
            if (
                len(result) == 1
                and result[0] == "XLS"
                and path.lower().endswith(".csv")
            ):
                return String("CSV")

            if len(result) == 0:
                result = "Binary"
            elif len(result) == 1:
                result = result[0]
            else:
                return None

            return result

        return self._import(
            None, determine_filetype, elements, evaluation, options, data=data
        )


class Export(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Export.html</url>

    <dl>
      <dt>'Export'["$file$.$ext$", $expr$]
      <dd>exports $expr$ to a file, using the extension $ext$ to determine the format.

      <dt>'Export'["$file$", $expr$, "$format$"]
      <dd>exports $expr$ to a file in the specified format.

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

    def _check_filename(self, filename, evaluation: Evaluation):
        path = filename.to_python()
        if isinstance(path, str) and path[0] == path[-1] == '"':
            return True
        evaluation.message("Export", "chtype", filename)
        return False

    def _infer_form(self, filename, evaluation: Evaluation):
        ext = Expression(SymbolFileExtension, filename).evaluate(evaluation)
        ext = ext.get_string_value().lower()
        # TODO: This dictionary should be accessible from the WL API
        # to allow defining specific converters
        return self._extdict.get(ext)

    def eval(self, filename, expr, evaluation, options={}):
        "Export[filename_, expr_, OptionsPattern[Export]]"

        # Check filename
        if not self._check_filename(filename, evaluation):
            return SymbolFailed

        # Determine Format
        form = self._infer_form(filename, evaluation)

        if form is None:
            evaluation.message("Export", "infer", filename)
            return SymbolFailed
        else:
            return self.eval_elements(filename, expr, String(form), evaluation, options)

    def eval_element(self, filename, expr, element: String, evaluation, options={}):
        "Export[filename_, expr_, element_String, OptionsPattern[]]"
        return self.eval_elements(
            filename, expr, ListExpression(element), evaluation, options
        )

    def eval_elements(self, filename, expr, elems, evaluation, options={}):
        "Export[filename_, expr_, elems_List?(AllTrue[#, NotOptionQ]&), OptionsPattern[]]"

        # Check filename
        if not self._check_filename(filename, evaluation):
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
            format_spec = self._infer_form(filename, evaluation)
            if format_spec is None:
                evaluation.message("Export", "infer", filename)
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
        stream_options, custom_options = _importer_exporter_options(
            exporter_options.get("System`Options"), options, "System`Export", evaluation
        )

        if function_channels is None:
            evaluation.message("Export", "emptyfch")
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed
        elif function_channels == ListExpression(String("FileNames")):
            exporter_function = Expression(
                exporter_symbol,
                filename,
                expr,
                *list(chain(stream_options, custom_options)),
            )
            res = exporter_function.evaluate(evaluation)
        elif function_channels == ListExpression(String("Streams")):
            stream = Expression(SymbolOpenWrite, filename, *stream_options).evaluate(
                evaluation
            )
            if stream.get_head_name() != "System`OutputStream":
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
            return filename
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
            element_str = element.get_string_value()

            if not found_form and element_str in EXPORTERS:
                found_form = True

            if found_form:
                format_spec.append(element_str)
            else:
                elems_spec.append(element)

        # Just to be sure that the following evaluations do not change the value of this property
        current_predetermined_out = evaluation.predetermined_out

        # Infer format if not present
        if format_spec is None:
            # evaluation.message("ExportString", "infer", filename)
            evaluation.predetermined_out = current_predetermined_out
            return SymbolFailed

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

        stream_options, custom_options = _importer_exporter_options(
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
                        # On Windows unlink make the second NamedTemporaryFIle
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
                    res = Expression(SymbolByteArray, ByteArrayAtom(res))
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
                    res = Expression(
                        SymbolByteArray, ByteArrayAtom(pystream.getvalue())
                    )
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
    messages = {
        "nffil": "File not found during `1`.",
    }

    detector = None

    def eval(self, filename: String, evaluation: Evaluation):
        "FileFormat[filename_String]"

        findfile = Expression(SymbolFindFile, filename).evaluate(evaluation)
        if findfile is SymbolFailed:
            evaluation.message(
                "FileFormat", "nffil", Expression(SymbolFileFormat, filename)
            )
            return findfile

        path = findfile.value
        if not FileFormat.detector:
            loader = magic.MagicLoader()
            loader.load()
            FileFormat.detector = magic.MagicDetector(loader.mimetypes)

        mime = set(FileFormat.detector.match(path))

        # If match fails match on extension only
        if mime == set():
            mime, encoding = mimetypes.guess_type(path)
            if mime is None:
                mime = set()
            else:
                mime = set([mime])
        result = []
        for key in mimetype_dict.keys():
            if key in mime:
                result.append(mimetype_dict[key])

        # the following fixes an extremely annoying behaviour on some (not all)
        # installations of Windows, where we end up classifying .csv files as XLS.
        if len(result) == 1 and result[0] == "XLS" and path.lower().endswith(".csv"):
            return String("CSV")

        if len(result) == 0:
            result = "Binary"
        elif len(result) == 1:
            result = result[0]
        else:
            return None

        return from_python(result)


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
            stringtocodify = (
                Expression(SymbolToString, expr).evaluate(evaluation).get_string_value()
            )
        return String(
            base64.b64encode(bytearray(stringtocodify, "utf8")).decode("utf8")
        )
