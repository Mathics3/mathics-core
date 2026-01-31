(* JSON Importer *)

Begin["JSON`Import`"]

ImportExport`RegisterImport[
    "JSON", {
    JSON`Import`JSONImport
    },
    {},
    FunctionChannels -> {"FileNames"}
]

End[]
