r"""Import/Export File Formats, Importers and Exporters

The data of files on a filesystem or retrieved from the Internet often are structured \
according to a specific structures and rules. For example, consider different kinds of \
structuring used in a JSON file, versus an HTML files, or a compressed GZIP file.

In some cases, such as archive files, e.g., ZIP, TAR, and JAR, the file contains component parts, \
which in WMA terminology are called "members" which is part of the broader metadata items \
called "elements".

A MIME type is typically associated with each kind of format. \Mathics3, following WMA, \
uses a shortend name for this MIME type. For example \Mathics3 uses "HTML" as a shorthand \
for the MIME type "text/html".

Below is a list of file supported file types that we have builtin importers or exporters written \
in Python. Other importers, however, are written in \Mathics3.

Variable <url>
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

Many Import/Export functions are registered in SystemFiles/Formats/*.wl which is \
autoloaded on startup.

The Built-in Functions are defined in a separate context.
For example, HTML` or Compress`.  This is done to not pollute the System` namespace.
"""

# This tells documentation how to sort this module
# Here we are also hiding "file_io" since this can erroneously appear at the top level.
sort_order = "mathics.builtin.importing-export-file-formats"
