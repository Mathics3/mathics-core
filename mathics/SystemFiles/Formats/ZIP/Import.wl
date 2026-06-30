(* ::Package:: *)

(* Windows ZIP archive, ZIP compressed file and file archive Importer.
   This is used by Import[] and, ImportString[].
 *)

Begin["System`Convert`CommonArchiveDump`"]


$ZIPHiddenElements = {_String, "FileNamesLegacy"};

$ZIPDocumentedElements = {"FileNames"};

$ZIPAvailableElements = SortBy[Join[$ZIPHiddenElements, $ZIPDocumentedElements], ToString];

GetElements[___] :=
	"Elements" ->
		SortBy[
			$ZIPDocumentedElements,
			ToString
		];

ImportExport`RegisterImport[
    "ZIP", (* WMA mime-type name *)
    Compress`ImportZIP,  (* Default Function name that handles this. *)
    {}, (* Post importer function(s) *)
    FunctionChannels -> {"FileNames"},
    (* WMA has this, but I (rocky) am not sure why or what it means:
    AvailableElements -> $ZIPAvailableElements, *)
    AvailableElements -> {"Filenames", "Summary"},  (* names retuned by "Elements" query *)
    BinaryFormat -> True,
    DefaultElement -> "FileNames",
    HiddenElements -> $ZIPHiddenElements,
    SkipPostImport -> <|
	    "FileNames" -> Automatic,
	    "Summary" -> Automatic,
	    "FileNamesLegacy" -> None, (* Disable SkipPostImport for FileNamesLegacy explicitly*)
	    (_String | _List) -> Automatic
	|>
]

End[]
