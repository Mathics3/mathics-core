(* ::Package:: *)

(* ZIP compressed file and file archive Importer.
   This is used by Import[].
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
    "ZIP",
    ImportZIP,
    {}, (* Post importer function(s) *)
    FunctionChannels -> {"FileNames"},
    (* WMA has this, but I (rocky) am not sure why or what it means:
    AvailableElements -> $ZIPAvailableElements, *)
    AvailableElements -> {"Filenames", "Summary"},
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
