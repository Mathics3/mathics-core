(* ZIP compressed file and file archive Importer *)

Begin["System`ZIP`"]
ImportExport`RegisterImport[
    "ZIP",
    ImportZip,
    FunctionChannels -> {"Streams"},
    AvailableElements -> {"FileNames", "Summary"},
    DefaultElement -> "FileNames"
]

End[]
