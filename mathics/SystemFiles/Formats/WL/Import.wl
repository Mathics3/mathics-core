(* ::Package:: *)

(* Note: this is stripped down a lot from what WMA handles. *)

Begin["System`Convert`WLDump`"];


ImportExport`RegisterImport[
	"WL",  (* WMA mime-type name *)
	WLDump`ImportWL (* Default Function name that handles this. *),
	{},
	"AvailableElements" -> {"Get", "Script"},
	"DefaultElement" -> "Get"
];


End[];
