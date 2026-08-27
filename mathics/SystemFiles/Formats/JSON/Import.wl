(* ::Package:: *)

(* JSON Javascript Object Notation or JSON web service description Importer.
   This is used by Import[] and, ImportString[].
 *)

Begin["System`Convert`JSONDump`"]

(* JSON legacy element is Data even if Expression would be better. *)
$AvailableElements = {"Data", "Dataset"};

ImportExport`RegisterImport[
    "JSON",  (* WMA mime-type name *)
    JSON`ImportJSON, (* Default Function name that handles this. *)
    {},
    "AvailableElements" -> $AvailableElements, (* names retuned by "Elements" query *)
    "FunctionChannels" -> {"FileNames"},
    "DefaultElement" -> "Data"
]

End[]
