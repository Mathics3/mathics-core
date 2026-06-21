(* ::Package:: *)

Begin["System`Convert`JSONDump`"]

(* JSON legacy element is Data even if Expression would be better. *)
$AvailableElements = {"Data", "Dataset"};

ImportExport`RegisterImport[
    "JSON",
    ImportJSON,
    {},
    "AvailableElements" -> $AvailableElements,
    "FunctionChannels" -> {"FileNames"},
    "DefaultElement" -> "Data"
]

End[]
