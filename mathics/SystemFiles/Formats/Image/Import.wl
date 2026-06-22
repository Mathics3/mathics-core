(* ::Package:: *)

(* Image Importer *)

Begin["System`Convert`Image`"]

RegisterImageImport[type_] := ImportExport`RegisterImport[
    type,
    System`ImageImport,
    {}, (* post *)
    AvailableElements -> {"Image"},
    DefaultElement -> "Image",
    FunctionChannels -> {"FileNames"}
];

(* FIXME: RegisterImageImport should work with MIME types, not psuedo-canonicalized file extensions. *)
RegisterImageImport[#]& /@ {"BMP", "GIF", "JPEG2000", "JPEG", "JPG", "PCX", "PNG", "PPM", "PBM", "PGM", "TIFF", "ICO", "TGA"};

End[]
