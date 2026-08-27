(* ::Package:: *)

(* XML Importer *)

(* "CDATA", "Comments", "EmbeddedDTD", "Plaintext", "Tags", "XMLObject", "XMLElement" *)

Begin["System`Convert`XMLDump`"]

ImportExport`RegisterImport[
    "XML",
    {
        "XMLObject" :> XML`XMLObjectImport,
        "Plaintext" :> XML`PlaintextImport,
        "Tags" :> XML`TagsImport,
        XML`XMLObjectImport
    },
    {},  (* post importer functions *)
    AvailableElements -> {"Plaintext", "Tags", "XMLObject"},
    DefaultElement -> "XMLObject",
    FunctionChannels -> {"FileNames"}
]

End[]
